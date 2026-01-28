# Database Override Feature - Summary

## What Changed

You can now pass a database name as a command-line argument to run simulations in different databases without touching config.json.

## The Feature

**Before:**
```bash
python master_simulation.py
```
Uses database from config.json

**After:**
```bash
python master_simulation.py dvdrental_new_db
```
Uses `dvdrental_new_db` instead, keeping all credentials from config.json

## Key Points

### ✅ What Stays From config.json
- **Host** (e.g., localhost)
- **User** (e.g., root)  
- **Password** (e.g., your_password)

### ✅ What Can Change
- **Database** (optional CLI argument)

### ✅ Safety
- config.json is **NEVER modified**
- Original database remains **completely untouched**
- Can run multiple simulations safely

## Implementation Details

### Modified Files
- **master_simulation.py**
  - `load_config()` now accepts `override_database` parameter
  - `main()` now parses command-line arguments
  - All credentials still from config.json

### Added Documentation
- **MASTER_SIMULATION_DB_OVERRIDE_CHEATSHEET.md** - Quick reference
- **MASTER_SIMULATION_MULTI_DB.md** - Comprehensive guide
- Updated **MASTER_SIMULATION_QUICKSTART.md** - Mentions new feature

## Usage Examples

### Example 1: Keep Original, Create New
```bash
python master_simulation.py dvdrental_simulation
```
- Original `dvdrental_live`: untouched
- New `dvdrental_simulation`: fresh 3-year data
- Both use credentials from config.json

### Example 2: Multiple Test Scenarios
```bash
# Test with conservative seasonality
python master_simulation.py dvdrental_test_conservative

# Test with aggressive seasonality
python master_simulation.py dvdrental_test_aggressive

# Test 10-year extended
python master_simulation.py dvdrental_test_10years
```

All three databases exist independently, same credentials.

### Example 3: Default Behavior
```bash
python master_simulation.py
```
Uses database from config.json (backward compatible)

## Technical Implementation

```python
# Before
def load_config(config_file='config.json'):
    with open(config_file) as f:
        return json.load(f)

# After  
def load_config(config_file='config.json', override_database=None):
    with open(config_file) as f:
        config = json.load(f)
    if override_database:
        config['mysql']['database'] = override_database
        logger.info(f"Using database: {override_database}")
    return config

# And in main()
override_database = sys.argv[1] if len(sys.argv) > 1 else None
config = load_config(override_database=override_database)
```

## Safety Verification

Your config.json is safe:

```bash
# Before running
cat config.json
# Shows: "database": "dvdrental_live"

# Run simulation in different database
python master_simulation.py dvdrental_test

# After running  
cat config.json
# Still shows: "database": "dvdrental_live"
# (unchanged!)

# Check both databases exist
mysql -u root -p -e "SHOW DATABASES LIKE 'dvdrental%';"
# Shows: dvdrental_live AND dvdrental_test
```

## Benefits

✅ **No config.json editing** - Risky operation eliminated  
✅ **Safe production database** - Original always untouched  
✅ **Multiple test scenarios** - Run different configs easily  
✅ **Single source of truth** - Credentials in one place  
✅ **Backward compatible** - Works without argument  
✅ **Simple usage** - Just pass database name  

## Documentation

For more details:
- [MASTER_SIMULATION_DB_OVERRIDE_CHEATSHEET.md](MASTER_SIMULATION_DB_OVERRIDE_CHEATSHEET.md) - 60 second reference
- [MASTER_SIMULATION_MULTI_DB.md](MASTER_SIMULATION_MULTI_DB.md) - Complete guide
- [MASTER_SIMULATION_QUICKSTART.md](MASTER_SIMULATION_QUICKSTART.md) - Updated quick start

## Backward Compatibility

The feature is fully backward compatible. Existing scripts and commands continue to work:

```bash
# Old way (still works)
python master_simulation.py
# → Uses database from config.json

# New way (also works)
python master_simulation.py dvdrental_new
# → Uses dvdrental_new, credentials from config.json
```

## Next Steps

Choose your approach:

**Option A: Safe testing**
```bash
python master_simulation.py dvdrental_test
```

**Option B: Stick with default**
```bash
python master_simulation.py
```

**Option C: Multiple scenarios**
```bash
python master_simulation.py dvdrental_scenario_1
python master_simulation.py dvdrental_scenario_2
python master_simulation.py dvdrental_scenario_3
```

All use the same connection credentials from config.json!
