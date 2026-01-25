# Database Creation Fix - Documentation

## Problem
When running the master simulation with a CLI database override (e.g., `python master_simulation.py dvdrental_group_a`), the script would fail with:
```
ERROR - Error connecting to MySQL: 1049 (42000): Unknown database 'dvdrental_group_a'
```

## Root Cause
The `DVDRentalDataGenerator.connect()` method in `generator.py` attempts to connect directly to the specified database. If the database doesn't exist yet, the MySQL connection fails before any initialization can occur.

## Solution Implemented

### 1. New Function: `create_database_if_needed()`
Added to `master_simulation.py` (lines 109-154):
```python
def create_database_if_needed(mysql_config: dict) -> bool:
    """Create the database if it doesn't exist"""
    try:
        # Connect to MySQL WITHOUT specifying database
        conn = mysql.connector.connect(
            host=mysql_config['host'],
            user=mysql_config['user'],
            password=mysql_config['password']
        )
        cursor = conn.cursor()
        
        db_name = mysql_config['database']
        
        # Check if database exists
        cursor.execute("SHOW DATABASES LIKE %s", (db_name,))
        exists = cursor.fetchone() is not None
        
        if not exists:
            logger.info(f"Creating database '{db_name}'...")
            cursor.execute(f"CREATE DATABASE `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            logger.info(f"✓ Database '{db_name}' created successfully")
        else:
            logger.info(f"Database '{db_name}' already exists, using existing database")
        
        cursor.close()
        conn.close()
        return True
        
    except Error as e:
        logger.error(f"Error creating database: {e}")
        return False
```

**Key Features:**
- Connects to MySQL **without specifying a database** (connects to server only)
- Checks if database exists using `SHOW DATABASES LIKE`
- Creates database with UTF8MB4 charset for international character support
- Safely handles existing databases (no errors, just logs info)
- Returns boolean for success/failure handling
- Proper error handling with logging

### 2. Integration into `main()`
Modified the `main()` function (lines 330-334) to call database creation before any operations:
```python
config = load_config(override_database=override_database)
mysql_config = config['mysql']

# Create database if it doesn't exist (required for CLI overrides)
if not create_database_if_needed(mysql_config):
    logger.error("Failed to create database. Exiting.")
    sys.exit(1)

display_simulation_plan()
```

**Execution Flow:**
1. Parse CLI arguments (if any)
2. Load config (applying override if provided)
3. **Create database if needed** ← NEW STEP
4. Display simulation plan
5. Begin Phase 1 (Initial Setup)

## Usage Examples

### With Default Database (from config.json)
```bash
python master_simulation.py
# Database 'dvdrental' from config.json will be verified/created
```

### With New Database (CLI Override)
```bash
python master_simulation.py dvdrental_group_a
# New database 'dvdrental_group_a' will be created automatically
# Credentials still from config.json
```

### Running Multiple Simulations for Classes
```bash
# Create separate databases for each group
python master_simulation.py dvdrental_group_a  # Creates dvdrental_group_a
python master_simulation.py dvdrental_group_b  # Creates dvdrental_group_b
python master_simulation.py dvdrental_group_c  # Creates dvdrental_group_c
```

## Benefits

1. **No Manual Database Creation**: Users don't need to run CREATE DATABASE manually
2. **Safe for Existing Databases**: Won't error if database already exists
3. **Full CLI Integration**: Database name can be specified as command argument
4. **Idempotent**: Running twice with same database name won't cause issues
5. **Proper Error Handling**: Exits gracefully if database creation fails
6. **UTF8MB4 Support**: Handles international characters correctly

## Technical Details

### MySQL Connection Hierarchy
The fix uses a two-connection approach:
1. **First Connection** (no database):
   - Connects to MySQL server without specifying a database
   - Used for CREATE DATABASE and SHOW DATABASES operations
   - Can execute server-level SQL commands
   
2. **Second Connection** (with database):
   - Created by `DVDRentalDataGenerator.connect()`
   - Database now guaranteed to exist
   - Used for all schema and data operations

### Why This Works
- MySQL requires a connection context to execute queries
- Database-specific operations require the database to exist in the connection
- Server-level operations (CREATE DATABASE) work without a specific database
- The two-step approach ensures database exists before schema operations begin

## Testing

To verify the fix works:

```bash
# Test 1: Create new database
python master_simulation.py dvdrental_test
# Expected: Database 'dvdrental_test' created message appears

# Test 2: Verify database was created
mysql -u [user] -p -e "SHOW DATABASES LIKE 'dvdrental_test';"
# Expected: dvdrental_test appears in list

# Test 3: Run again (should use existing database)
python master_simulation.py dvdrental_test
# Expected: "Database 'dvdrental_test' already exists" message

# Test 4: Verify data in database
mysql -u [user] -p -D dvdrental_test -e "SELECT COUNT(*) FROM rental;"
# Expected: Rental count from simulation
```

## Files Modified

- **master_simulation.py**:
  - Added `create_database_if_needed()` function (lines 109-154)
  - Updated `main()` to call database creation (lines 330-334)
  - Total script now: 450 lines (was 445)

## Backward Compatibility

✅ **Fully Backward Compatible**
- Existing workflows unchanged
- Default database (config.json) still works
- All existing features preserved
- No configuration changes needed

## See Also

- [DATABASE_OVERRIDE_FEATURE_SUMMARY.md](DATABASE_OVERRIDE_FEATURE_SUMMARY.md) - CLI override feature documentation
- [MASTER_SIMULATION_FOR_CLASSES.md](MASTER_SIMULATION_FOR_CLASSES.md) - Educational use case guide
- [QUICKSTART.md](MASTER_SIMULATION_QUICKSTART.md) - Getting started guide
