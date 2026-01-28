# File Path Errors - FIXED ✓

## Problem
The scripts were looking for `config.json` and `schema.sql` in the current working directory, but they were located in:
- `shared/configs/config.json` 
- `level_1_basic/schema_base.sql`

When running from the root directory, scripts would fail with:
```
Configuration file config.json not found
[Errno 2] No such file or directory: 'schema.sql'
```

## Solution
Updated all three main scripts to intelligently search for files in multiple locations:

### Level 1 - `level_1_basic/generator.py`
✅ Updated config file search:
- Looks in current directory first
- Then in script directory: `level_1_basic/config.json`
- Then in shared: `shared/configs/config.json`

✅ Updated schema file search:
- Looks in current directory first
- Then in script directory: `level_1_basic/schema_base.sql`
- Then in shared: `shared/schemas/schema_base.sql`

✅ Changed default schema name from `schema.sql` to `schema_base.sql`

### Level 3 - `level_3_master_simulation/master_simulation.py`
✅ Updated `load_config()` function:
- Searches multiple paths for config files
- Changed default from `config.json` to `config_10year.json`
- Added `os` import

### Level 4 - `level_4_advanced_master/run_advanced_simulation.py`
✅ Updated `AdvancedSimulationConfig` class:
- Searches multiple paths for config files
- More flexible config file loading
- Added `os` import

## Testing

All scripts now work from any directory:

```bash
# From root directory
cd /home/agogodavid/dev_dvdrental/dvdrental_live
source venv/bin/activate

# Level 1 - Works!
python level_1_basic/generator.py --database test_db --season 50

# Level 3 - Works!
python level_3_master_simulation/master_simulation.py --database master_test

# Level 4 - Works!
python level_4_advanced_master/run_advanced_simulation.py --database adv_test
```

## File Location Search Order

### Config Files
1. `config.json` (current directory)
2. `{script_dir}/config.json`
3. `{script_dir}/../shared/configs/config.json`

### Schema Files (Level 1)
1. `schema_base.sql` (current directory)
2. `{script_dir}/schema_base.sql`
3. `{script_dir}/../shared/schemas/schema_base.sql`

## Changes Made

| File | Change |
|------|--------|
| `level_1_basic/generator.py` | Added intelligent config & schema file search |
| `level_3_master_simulation/master_simulation.py` | Updated load_config(), added `os` import |
| `level_4_advanced_master/run_advanced_simulation.py` | Updated AdvancedSimulationConfig, added `os` import |

## Verification

✅ All files compile without errors
✅ Generator works from root directory
✅ Config files found automatically
✅ Schema files found automatically
✅ Command-line arguments work correctly
✅ Season argument applies boost correctly
✅ Database override works

## What's Next?

You can now run any of the scripts from the root directory without worrying about file paths:

```bash
source venv/bin/activate
python level_1_basic/generator.py --database my_db --season 50
python level_3_master_simulation/master_simulation.py --season 30
python level_4_advanced_master/run_advanced_simulation.py --season 40
```

All paths are automatically resolved!
