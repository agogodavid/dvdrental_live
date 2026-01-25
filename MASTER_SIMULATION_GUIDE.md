# Master Simulation Script - Complete Guide

## Overview

`master_simulation.py` is an orchestration script that generates realistic 3-10 year DVD rental databases with:

- **Initial setup** with starter inventory (using generator.py)
- **Periodic inventory additions** matching realistic business patterns
- **Regular weekly transactions** (using incremental_update.py)
- **Seasonal demand variations** (summer boost, holiday rush, etc.)
- **Automatic progress tracking** and final statistics

Generate complete, realistic databases in one command instead of manually running multiple scripts.

## Quick Start

### Generate 3 Years of Data (156 weeks)

```bash
python master_simulation.py
```

This runs completely automated:
1. Oct 2001: Initial database setup (~12 weeks of starter data)
2. Oct 2001 - Sept 2004: Weekly incremental updates with seasonal patterns
3. Periodic inventory additions matching business cycles
4. Final statistics and validation

### Generate 10 Years of Data

Edit `SimulationConfig` in `master_simulation.py`:

```python
TOTAL_WEEKS = 520  # Change from 156 to 520 (10 years)
```

Then extend `INVENTORY_ADDITIONS` to cover the full period:

```python
INVENTORY_ADDITIONS = [
    (0, 0, "Initial inventory created by generator"),
    (12, 50, "Q1 2002 - Holiday season restock"),
    # ... existing entries ...
    (104, 50, "Q4 2003 - Holiday season expansion"),
    # Add new entries:
    (118, 60, "Q1 2004 - New year expansion"),
    (130, 50, "Q2 2004 - Spring refresh"),
    # ... continue pattern ...
]
```

Then run:

```bash
python master_simulation.py
```

## Configuration

All simulation parameters are in the `SimulationConfig` class:

### Timeline

```python
START_DATE = datetime(2001, 10, 1).date()  # October 1, 2001
TOTAL_WEEKS = 156  # 156 weeks = 3 years
```

- **START_DATE**: First Monday of simulation (Oct 1, 2001)
- **TOTAL_WEEKS**: Duration in weeks (156 = 3 years, 520 = 10 years)

### Inventory Additions Schedule

```python
INVENTORY_ADDITIONS = [
    (week_number, quantity, "Description"),
    ...
]
```

Format: `(week_number, quantity, description)`

**Examples:**
```python
(0, 0, "Initial inventory created by generator"),      # Week 0 (initial)
(12, 50, "Q1 2002 - Holiday season restock"),          # Week 12 (3 months in)
(26, 40, "Q2 2002 - Spring refresh"),                  # Week 26 (6 months in)
(52, 50, "Q4 2002 - Holiday restock"),                 # Week 52 (1 year in)
```

**Tips:**
- Week 0 = October 1, 2001
- Week 52 = October 1, 2002 (one year later)
- Week 13 ≈ one quarter later
- Start with initial setup (week 0)
- Add inventory every 12-14 weeks to match business cycles

### Seasonal Demand Multipliers

```python
SEASONAL_MULTIPLIERS = {
    1: 20,     # January: +20% demand
    6: 80,     # June: +80% demand (summer rush!)
    7: 100,    # July: +100% demand (peak season)
    12: 60,    # December: +60% demand (holidays)
}
```

These multipliers are applied to transaction volume based on the current month.

**Realistic pattern:**
- June-August: 80-100% boost (summer vacation movies)
- December: 60% boost (holiday season)
- February: -10% (post-holiday slump)
- May/October: 15-25% (shoulder seasons)

## Simulation Phases

### Phase 1: Initial Setup (Minutes)

```
Generator runs with start_date = 2001-10-01
Creates:
  • Database schema
  • Base data (staff, stores)
  • 100 sample films
  • Initial inventory (~400-500 items)
  • Initial transactions (~12 weeks)
```

**Output:**
- ✓ Initial inventory created: X items
- ✓ Initial transactions created: Y rentals

### Phase 2: Incremental Updates (Hours for 10 years)

Processes remaining weeks in batches:

```
For each batch of weeks:
  1. Check if inventory should be added this week
  2. Get seasonal demand for the month
  3. Add 4 weeks of transactions with seasonal multiplier
  4. Update progress
```

**Output per batch:**
```
📦 Week 12 (Jan 14, 2002): Q1 2002 - Holiday season restock
   ✓ Added 50 inventory items
📊 Weeks 12-15 (Jan 14, 2002 - ...)
   Seasonal drift: +20% (month: January)
   Progress: 5.1% (8/156 weeks)
```

### Phase 3: Summary (Seconds)

Queries database for final statistics:

```
✓ Total Rentals: 65,234
✓ Active Customers: 1,247
✓ Total Inventory Items: 547 (+147 added during simulation)
✓ Data Range: 2001-10-01 to 2004-09-29
✓ Currently Checked Out: 23 items
✓ Average Rentals per Week: 418
```

## Extending to 10+ Years

### Step 1: Update TOTAL_WEEKS

```python
TOTAL_WEEKS = 520  # 10 years instead of 156 (3 years)
```

### Step 2: Extend INVENTORY_ADDITIONS

Follow the pattern from the existing entries. Example for full 10 years:

```python
INVENTORY_ADDITIONS = [
    # Year 1 (2001-2002)
    (0, 0, "Initial inventory created by generator"),
    (12, 50, "Q1 2002 - Holiday season restock"),
    (26, 40, "Q2 2002 - Spring refresh"),
    (40, 60, "Q3 2002 - Summer prep"),
    (52, 50, "Q4 2002 - Holiday restock"),
    
    # Year 2 (2002-2003)
    (66, 40, "Q1 2003 - Winter refresh"),
    (78, 60, "Q2 2003 - Spring collection expansion"),
    (92, 70, "Q3 2003 - Summer blockbuster prep"),
    (104, 50, "Q4 2003 - Holiday season expansion"),
    
    # Year 3 (2003-2004)
    (118, 60, "Q1 2004 - New year expansion"),
    (130, 50, "Q2 2004 - Spring refresh"),
    (144, 70, "Q3 2004 - Summer restock"),
    (156, 60, "Q4 2004 - Holiday preparation"),
    
    # Year 4 (2004-2005) - REPEAT PATTERN with slightly increased quantities
    (170, 50, "Q1 2005 - New year collection"),
    (182, 60, "Q2 2005 - Spring expansion"),
    (196, 75, "Q3 2005 - Summer boost"),
    (208, 60, "Q4 2005 - Holiday restock"),
    
    # Years 5-10: Continue repeating with gradual increases
    # Pattern: Add every 12-14 weeks, gradually increase quantities
]
```

### Step 3: Run

```bash
python master_simulation.py
```

## Execution Timeline

### 3 Years (156 weeks)
- Phase 1 (Setup): ~5 minutes
- Phase 2 (Updates): ~20-30 minutes
- Phase 3 (Summary): ~1 minute
- **Total: ~30 minutes**

### 10 Years (520 weeks)
- Phase 1 (Setup): ~5 minutes
- Phase 2 (Updates): ~90-120 minutes
- Phase 3 (Summary): ~1 minute
- **Total: ~2 hours**

## Key Features

### ✅ Realistic Business Patterns

- **Initial ramp**: ~500 transactions/week initially
- **Growth**: +2% per week
- **Seasonal boosts**: Summer (80-100%), holidays (60%), winter slump (-10%)
- **Customer lifecycle**: New customers added, churn over time, loyal base builds
- **New inventory**: Prioritized for rentals (weighted selection)

### ✅ Extensible Design

- Easy to modify start date
- Duration in weeks parameter
- Inventory schedule as simple list
- Seasonal pattern as month lookup table
- Batch processing for efficiency

### ✅ Progress Tracking

- Real-time output showing each phase
- Percentage progress during updates
- Inventory additions logged
- Final statistics and validation

### ✅ Modularity

- Uses existing generator.py, incremental_update.py, inventory_manager.py
- No changes needed to those scripts
- Pure orchestration layer
- Can be extended without touching core logic

## Example Outputs

### Successful 3-Year Run

```
╔════════════════════════════════════════════════════════════════════════════════╗
║        MASTER DVD RENTAL SIMULATION - 3 Year Data Generation                   ║
╚════════════════════════════════════════════════════════════════════════════════╝

================================================================================
SIMULATION PLAN
================================================================================
Start Date: 2001-10-01
Duration: 156 weeks (~3.0 years)
End Date: 2004-09-27

Inventory Additions Schedule:
  Week   0 (2001-10-01): +  0 items - Initial inventory created by generator
  Week  12 (2002-01-14): + 50 items - Q1 2002 - Holiday season restock
  ...
================================================================================

2024-01-25 12:34:56 INFO ✓ Initial inventory created: 498 items
2024-01-25 12:34:56 INFO ✓ Initial transactions created: 4821 rentals

================================================================================
PHASE 2: Incremental Weekly Updates with Seasonal Variations
================================================================================
Adding 144 weeks of transactions...

📊 Weeks 12-15 (2002-01-14 - ...)
   Seasonal drift: +20% (month: January)
   Progress: 2.8% (4/144 weeks)

📦 Week 12 (2002-01-14): Q1 2002 - Holiday season restock
   ✓ Added 50 inventory items - Q1 2002 - Holiday season restock

...

================================================================================
PHASE 3: Simulation Complete - Database Summary
================================================================================

✓ Total Rentals: 65,234
✓ Active Customers: 1,247
✓ Total Inventory Items: 696 (+198 added during simulation)
✓ Data Range: 2001-10-01 to 2004-09-27
✓ Currently Checked Out: 27 items
✓ Average Rentals per Week: 418

================================================================================
SIMULATION SUCCESSFUL!
================================================================================

Database is ready with 3.0 years of realistic transaction data.

To extend simulation to 10 years:
  1. Set TOTAL_WEEKS = 520 in SimulationConfig
  2. Add more entries to INVENTORY_ADDITIONS (extend the pattern)
  3. Run: python master_simulation.py
```

## Troubleshooting

### "No existing rentals found"

**Cause:** Initial setup failed
**Fix:** Check MySQL connection and verify generator.py runs successfully

### Database too large

**Issue:** Need to generate more data but database is getting too large
**Solution:** Back up current database, reinitialize, and run new simulation

### Slow performance on 10-year run

**Cause:** Large transaction volume
**Solution:**
- Run on a machine with more RAM
- Reduce batch size (change `batch_size = 4` to `batch_size = 2`)
- Run queries manually to analyze in separate sessions

### Inventory not increasing

**Check:**
1. Verify `INVENTORY_ADDITIONS` list is populated
2. Check week numbers match schedule
3. Verify inventory items in database: `SELECT COUNT(*) FROM inventory;`

## Advanced Usage

### Custom Seasonal Pattern

Modify `SEASONAL_MULTIPLIERS` for different patterns:

```python
# Alternative: Blockbuster season peaks
SEASONAL_MULTIPLIERS = {
    1: 30,    # New Year's resolutions
    3: 40,    # Spring break
    5: 50,    # Summer prep
    6: 100,   # Summer vacation
    7: 100,   # Peak summer
    11: 80,   # Thanksgiving holiday
    12: 60,   # Christmas season
    # Others default to 0 (no multiplier)
}
```

### Different Start Date

```python
START_DATE = datetime(2010, 1, 4).date()  # January 4, 2010
```

### Accelerated Growth

Add more frequent inventory additions:

```python
INVENTORY_ADDITIONS = [
    (0, 0, "Initial"),
    (8, 40, "Q1 refresh"),      # Every 8 weeks
    (16, 40, "Q2 refresh"),
    (24, 50, "Q3 refresh"),
    (32, 40, "Q4 refresh"),
    # ... every 8 weeks instead of 12-14
]
```

## Database Validation

After running the simulation, validate the data:

```sql
-- Check data distribution
SELECT 
    COUNT(*) as total_rentals,
    COUNT(DISTINCT customer_id) as unique_customers,
    COUNT(DISTINCT inventory_id) as items_rented,
    MIN(rental_date) as first_rental,
    MAX(rental_date) as last_rental,
    DATEDIFF(MAX(rental_date), MIN(rental_date)) as days_of_data
FROM rental;

-- Check seasonal pattern (should show peaks in summer)
SELECT 
    MONTH(rental_date) as month,
    COUNT(*) as rentals,
    ROUND(100 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) as pct
FROM rental
GROUP BY MONTH(rental_date)
ORDER BY month;

-- Check inventory aging (newer should have more rentals)
SELECT 
    DATEDIFF(CURDATE(), created_at) as days_old,
    COUNT(r.rental_id) as rental_count,
    ROUND(100 * COUNT(r.rental_id) / SUM(COUNT(r.rental_id)) OVER (), 1) as pct
FROM inventory i
LEFT JOIN rental r ON i.inventory_id = r.inventory_id
GROUP BY DATEDIFF(CURDATE(), created_at)
ORDER BY days_old
LIMIT 20;
```

## Next Steps

After generating data:

1. **Analyze patterns**: Use maintain.py to view growth metrics
2. **Validate quality**: Run SQL validation queries above
3. **Export for testing**: Use database dump for integration testing
4. **Modify for research**: Adjust configuration and rerun for different scenarios

