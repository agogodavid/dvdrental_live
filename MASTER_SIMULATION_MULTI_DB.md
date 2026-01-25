# Master Simulation - Multi-Database Support

## Overview

You can now run the master simulation on a **new database** while keeping your existing database intact. No need to modify config.json!

## Quick Start

### Use Existing Database (Default)
```bash
python master_simulation.py
```
Uses database name from config.json (likely `dvdrental_live`)

### Use Different Database
```bash
python master_simulation.py dvdrental_sim_test
```
Creates/uses `dvdrental_sim_test` instead of the one in config.json

**Original database is untouched!**

## How It Works

The `load_config()` function now accepts an optional database name override:

```python
def load_config(config_file='config.json', override_database=None):
    """Load MySQL configuration
    
    Args:
        override_database: Optional database name to override config.json
    """
    with open(config_file, 'r') as f:
        config = json.load(f)  # Read ALL credentials from config.json
    
    # ONLY override the database name if provided
    if override_database:
        config['mysql']['database'] = override_database
    
    return config  # host, user, password still from config.json
```

**Example execution flow:**

```bash
$ python master_simulation.py dvdrental_test
```

1. Read config.json completely
2. Extract: host=localhost, user=root, password=..., database=dvdrental_live
3. Override database: dvdrental_live → dvdrental_test
4. Connect using: localhost / root / password / **dvdrental_test**
5. Create/use dvdrental_test database
6. Original dvdrental_live is untouched

## Usage Examples

### Scenario 1: Keep Original, Create Test Simulation
```bash
# Original database stays: dvdrental_live
# New simulation in: dvdrental_sim_test

python master_simulation.py dvdrental_sim_test
```

**Result:**
- `dvdrental_live` untouched
- `dvdrental_sim_test` created with fresh 3-year simulation

### Scenario 2: Multiple Simulations with Different Configs

Run 3 different scenarios in parallel (or sequentially):

```bash
# Test 1: Conservative seasonality
python master_simulation.py dvdrental_test_conservative

# Test 2: Aggressive seasonality  
# First, edit master_simulation.py to change SEASONAL_MULTIPLIERS
python master_simulation.py dvdrental_test_aggressive

# Test 3: 10-year extended
# First, edit master_simulation.py to change TOTAL_WEEKS to 520
python master_simulation.py dvdrental_test_10years
```

**Result:**
- Three separate databases with different data
- Original database still untouched
- Can compare results across scenarios

### Scenario 3: Development vs Production

```bash
# Keep your production database for live app
# dvdrental_live = production (from config.json)

# Run simulation in dev database
python master_simulation.py dvdrental_dev

# Run simulation in qa database
python master_simulation.py dvdrental_qa

# Run simulation in test database
python master_simulation.py dvdrental_test
```

## Database Selection Flow

```
Command Line Argument Provided?
    ├─ YES → Use provided database name
    │        (overrides config.json)
    │        Example: python master_simulation.py my_new_db
    │
    └─ NO → Use database from config.json
            (original behavior)
            Example: python master_simulation.py
```

## Important Notes

### Database Credentials

**All connection information comes from config.json - nothing changes:**

- Host: `config.json['mysql']['host']`
- User: `config.json['mysql']['user']`
- Password: `config.json['mysql']['password']`
- Database: **Overridden by command-line argument** (or uses config.json default)

**Example config.json:**
```json
{
  "mysql": {
    "host": "localhost",
    "user": "root",
    "password": "your_password",
    "database": "dvdrental_live"
  }
}
```

When you run:
```bash
python master_simulation.py dvdrental_sim_test
```

The script uses:
- host: `localhost` (from config.json)
- user: `root` (from config.json)
- password: `your_password` (from config.json)
- database: `dvdrental_sim_test` (**from command-line argument**)

**All credentials are identical - only the database name changes.**

### Prerequisite
- MySQL user account must have CREATE DATABASE privileges
- Script will create database if it doesn't exist
- If database exists, it will be used (not recreated)

### Verification
Check which database was used by looking at the initial setup output:

```
✓ Initial inventory created: 498 items
✓ Initial transactions created: 4821 rentals
```

After completion, check database:
```bash
mysql -u root -p -e "SHOW DATABASES LIKE 'dvdrental%';"
```

Should show both original and new databases:
```
+---------------------+
| Database            |
+---------------------+
| dvdrental_live      |
| dvdrental_sim_test  |
+---------------------+
```

## No Changes to config.json

**config.json is read as-is, no modifications happen:**

```json
{
  "mysql": {
    "host": "localhost",       ← Used for connection
    "user": "root",            ← Used for authentication
    "password": "your_password",  ← Used for authentication
    "database": "dvdrental_live"  ← Used as DEFAULT only if no override
  }
}
```

**Connection Priority:**
1. Command-line database name? Use that
2. Otherwise, use database from config.json
3. Always use host, user, password from config.json

**No file is ever modified. All credentials come from config.json.**

## Error Handling

### Database Already Exists
If you run the same database name twice:
```bash
python master_simulation.py dvdrental_sim_test  # First run
python master_simulation.py dvdrental_sim_test  # Second run
```

Second run will fail because tables already exist. Either:
1. Use different database name: `dvdrental_sim_test_v2`
2. Drop database: `DROP DATABASE dvdrental_sim_test;`
3. Start fresh: `mysql.server restart` (if needed)

### Permission Denied
If you get permission error:
```
Access denied for user creating database
```

Grant privileges:
```bash
mysql -u root -p -e "GRANT ALL PRIVILEGES ON dvdrental_*.* TO 'root'@'localhost';"
```

## Real-World Workflow

```bash
# 1. Keep production database intact
# dvdrental_live is untouched

# 2. Run initial test simulation
python master_simulation.py dvdrental_test_1

# 3. Verify results
python maintain.py  # Still works on default db
mysql -u root -p dvdrental_test_1 -e "SELECT COUNT(*) FROM rental;"

# 4. Try different configuration
# Edit master_simulation.py SEASONAL_MULTIPLIERS
python master_simulation.py dvdrental_test_2

# 5. Compare two simulations
mysql -u root -p -e "
  SELECT 'test_1' as sim, COUNT(*) as rentals 
  FROM dvdrental_test_1.rental
  UNION
  SELECT 'test_2' as sim, COUNT(*) as rentals 
  FROM dvdrental_test_2.rental;
"

# 6. Run extended 10-year simulation
# Edit master_simulation.py TOTAL_WEEKS = 520
python master_simulation.py dvdrental_extended

# 7. Original production database still untouched
mysql -u root -p dvdrental_live -e "SELECT COUNT(*) FROM rental;"
```

## Cleanup

Remove test simulation databases when done:

```bash
# List all databases
mysql -u root -p -e "SHOW DATABASES;"

# Drop test database
mysql -u root -p -e "DROP DATABASE dvdrental_test_1;"

# Or drop all sim databases
for db in dvdrental_sim_test dvdrental_test_conservative dvdrental_extended; do
  mysql -u root -p -e "DROP DATABASE $db;"
done
```

## Summary

**Old way (before):**
- Edit config.json (risky, affects everything)
- Run simulation
- Swap back config.json

**New way (now):**
- Just pass database name as argument: `python master_simulation.py new_db_name`
- Original database stays intact
- No file modifications needed

That's it! 🚀
