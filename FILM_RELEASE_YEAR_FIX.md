# Film Release Year Fix - Data Quality Issue

## Problem Identified

**Issue**: Films in the database have release years (up to 2023) that are chronologically after rental transactions (2001-2011).

**Example**: A rental transaction in 2001 references a film with release_year = 2023, which is logically impossible.

## Root Cause

The `seed_films()` method in `generator.py` was using a hardcoded release year range:
```python
release_year = random.randint(1980, 2023)  # INCORRECT
```

This ignored the `start_date` parameter and always generated films with years up to 2023, regardless of when the simulation actually takes place.

## Solution Applied

### 1. Fixed generator.py

Updated the `seed_films()` method to calculate appropriate release years based on the simulation start date:

```python
def seed_films(self, count: int = 100, start_date=None):
    # Calculate appropriate release year range based on start_date
    if start_date:
        # Films should be released before or at the simulation start date
        # Generate films from 10-20 years before start_date up to start_date year
        if isinstance(start_date, str):
            from datetime import datetime
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        current_year = start_date.year
        year_min = max(1980, current_year - 20)  # Go back 20 years, but not before 1980
        year_max = current_year  # Films up to the simulation start year
    else:
        # Fallback to a reasonable range
        year_min = 1980
        year_max = 2001  # Default to 2001 if no start_date provided
    
    release_year = random.randint(year_min, year_max)  # CORRECT
```

**Result**: For a simulation starting in 2001, films will now have release years between 1981-2001.

### 2. Quarterly Film Releases (Already Correct)

The `FilmGenerator` class in `level_3_master_simulation/film_system/film_generator.py` was already correctly using the simulation date:

```python
film_year = film_date.year
release_year = film_year
```

So quarterly releases throughout the 10-year simulation will have appropriate years (2001-2011).

## Testing

Created `test_release_years.py` to verify the fix:

```bash
python test_release_years.py
```

**Result**:
```
✅ SUCCESS: All films have release years at or before simulation start!
   Expected: release_year ≤ 2001
   Got: 1981 ≤ release_year ≤ 2001
```

## Fixing Existing Databases

For databases that already have incorrect film years, use the provided fix script:

### Dry Run (Preview Only)
```bash
python fix_film_release_years.py --database dvdrental_O
```

### Apply Fix
```bash
python fix_film_release_years.py --database dvdrental_O --apply
```

### Options
- `--database DATABASE` or `-d DATABASE`: Database name to fix
- `--start-year YEAR` or `-y YEAR`: Simulation start year (default: 2001)
- `--apply`: Actually apply changes (without this, it's dry-run only)

### Example Output

**Before Fix**:
```
Total films: 840
Release year range: 1980 - 2023
Films with year > 2001: 796
```

**After Fix**:
```
✅ Fixed 796 films!
New release year range: 1981 - 2001
Remaining films with year > 2001: 0
```

## Impact on Existing Simulations

### Databases Created BEFORE This Fix
- **dvdrental_O** and other existing databases have films with years 1980-2023
- Run `fix_film_release_years.py --apply` to correct them
- This is a safe operation - it only updates the `release_year` column

### Databases Created AFTER This Fix
- Will automatically have correct release years based on simulation timeline
- No manual intervention needed

## Verification Query

To check any database for this issue:

```sql
SELECT 
    MIN(rental_date) as first_rental,
    MAX(rental_date) as last_rental,
    MIN(f.release_year) as oldest_film,
    MAX(f.release_year) as newest_film,
    COUNT(DISTINCT CASE 
        WHEN f.release_year > YEAR(r.rental_date) 
        THEN r.rental_id 
    END) as impossible_rentals
FROM rental r
JOIN inventory i ON r.inventory_id = i.inventory_id
JOIN film f ON i.film_id = f.film_id;
```

**Expected Result**:
- `impossible_rentals` should be 0
- `newest_film` should be ≤ year of `first_rental`

## Files Changed

1. **generator.py** (line 175-235)
   - Updated `seed_films()` to use simulation start_date for release year range
   
2. **test_release_years.py** (NEW)
   - Test script to verify film years are correct
   
3. **fix_film_release_years.py** (NEW)
   - Script to fix existing databases with incorrect years

## Future Simulations

All new simulations will automatically generate films with appropriate release years:

- **Level 1 Basic** (generator.py): Uses start_date from config
- **Level 2 Incremental**: Uses start_date from config  
- **Level 3 Master** (52 weeks, 2001-2002): Films 1981-2001, quarterly releases 2001-2002
- **Level 4 Advanced** (520 weeks, 2001-2011): Films 1981-2001, quarterly releases 2001-2011

This ensures data quality and logical consistency across all simulation levels.
