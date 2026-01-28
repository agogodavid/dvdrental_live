# Master Simulation - Quick Reference

## Run Simulation

### Generate 3 Years of Data (Default)
```bash
python master_simulation.py
```
- 156 weeks (Oct 2001 - Sept 2004)
- ~30 minutes runtime
- ~65,000 transactions
- ~500+ inventory items

### Generate 10 Years of Data

**Step 1:** Edit `master_simulation.py` line ~30:
```python
TOTAL_WEEKS = 520  # Change from 156
```

**Step 2:** Extend `INVENTORY_ADDITIONS` (after line ~40):
```python
INVENTORY_ADDITIONS = [
    (0, 0, "Initial inventory created by generator"),
    (12, 50, "Q1 2002 - Holiday season restock"),
    (26, 40, "Q2 2002 - Spring refresh"),
    (40, 60, "Q3 2002 - Summer prep"),
    (52, 50, "Q4 2002 - Holiday restock"),
    # Add more entries for years 2-10 following the pattern above
    # Pattern: Every 12-14 weeks, quantities 40-70 items
]
```

**Step 3:** Run
```bash
python master_simulation.py
```

## Configuration Quick Edit

### Change Start Date
Line ~29:
```python
START_DATE = datetime(2010, 1, 4).date()  # Different year
```

### Adjust Seasonal Pattern
Line ~41-54:
```python
SEASONAL_MULTIPLIERS = {
    1: 20,     # January multiplier
    6: 80,     # June multiplier
    7: 100,    # July multiplier
    12: 60,    # December multiplier
    # Add/modify for other months
}
```

### Change Inventory Schedule
Line ~32-49:
```python
INVENTORY_ADDITIONS = [
    (week_number, quantity, "Description"),
    (0, 0, "Initial inventory created by generator"),
    (12, 50, "Q1 2002 - Holiday season restock"),
    (26, 40, "Q2 2002 - Spring refresh"),
    # Format: (week_number, quantity, description)
    # Example: (52, 50, "Q4 2002 - Holiday restock") = add 50 items at week 52
]
```

## Timeline Mapping

| Weeks | Years | Duration | Runtime |
|-------|-------|----------|---------|
| 52    | 1     | Oct 2001 - Oct 2002 | ~10 min |
| 156   | 3     | Oct 2001 - Oct 2004 | ~30 min |
| 260   | 5     | Oct 2001 - Oct 2006 | ~60 min |
| 520   | 10    | Oct 2001 - Oct 2011 | ~2 hrs |

## What Gets Generated

### Database
- ✅ 14 normalized tables (schema.sql)
- ✅ Base data (100 films, 2 stores, staff)
- ✅ Realistic customer lifecycle
- ✅ Seasonal demand patterns
- ✅ Inventory aging (newer items prioritized)
- ✅ Late fees, payments, returns

### Data Volume (for 3 years)
- ~65,000 rentals
- ~1,200 active customers
- ~700 inventory items
- ~500 late fees
- ~2,000 payments
- Daily transactions: 80-400 (varies seasonally)

## Simulation Phases

### Phase 1: Initial Setup (5 min)
- Create schema
- Seed base data
- Generate initial inventory
- Create ~12 weeks of starter transactions

### Phase 2: Incremental Updates (25 min for 3 years)
- Add 4 weeks at a time
- Apply seasonal multiplier
- Add inventory when scheduled
- Show progress

### Phase 3: Summary (1 min)
- Count total rentals, customers, inventory
- Show date range
- Calculate averages
- Display completion message

## Output Example

```
╔════════════════════════════════════════════════════════════════════════════════╗
║        MASTER DVD RENTAL SIMULATION - 3 Year Data Generation                   ║
╚════════════════════════════════════════════════════════════════════════════════╝

SIMULATION PLAN
Start Date: 2001-10-01
Duration: 156 weeks (~3.0 years)
End Date: 2004-09-27

Inventory Additions Schedule:
  Week   0 (2001-10-01): +  0 items - Initial inventory created by generator
  Week  12 (2002-01-14): + 50 items - Q1 2002 - Holiday season restock
  Week  26 (2002-04-29): + 40 items - Q2 2002 - Spring refresh
  ...

✓ Initial inventory created: 498 items
✓ Initial transactions created: 4821 rentals

📊 Weeks 12-15 (2002-01-14 - ...)
   Seasonal drift: +20% (month: January)
   Progress: 2.8% (4/144 weeks)

📦 Week 12 (2002-01-14): Q1 2002 - Holiday season restock
   ✓ Added 50 inventory items

[More updates...]

SIMULATION COMPLETE - Database Summary
✓ Total Rentals: 65,234
✓ Active Customers: 1,247
✓ Total Inventory Items: 696 (+198 added during simulation)
✓ Data Range: 2001-10-01 to 2004-09-27
✓ Currently Checked Out: 27 items
✓ Average Rentals per Week: 418

SIMULATION SUCCESSFUL!
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Script doesn't start | Verify MySQL is running: `mysql -u root -p` |
| "No existing rentals found" | Check generator.py runs: `python generator.py` |
| Very slow | Reduce batch_size in code or run on faster machine |
| Need to restart | Delete database: `DROP DATABASE dvdrental_live;` then rerun |
| Out of disk space | Check disk: `df -h` or `du -sh dvdrental_live/` |

## Validation Query

After running, verify data looks good:

```sql
USE dvdrental_live;

-- Overall stats
SELECT 
    COUNT(*) as total_rentals,
    COUNT(DISTINCT customer_id) as customers,
    COUNT(DISTINCT inventory_id) as items_rented
FROM rental;

-- Should show rental peak in summer (June/July)
SELECT 
    MONTH(rental_date) as month,
    COUNT(*) as rentals
FROM rental
GROUP BY MONTH(rental_date)
ORDER BY month;

-- Check inventory age distribution
SELECT 
    DATEDIFF(CURDATE(), created_at) as days_old,
    COUNT(*) as item_count
FROM inventory
GROUP BY DATEDIFF(CURDATE(), created_at)
ORDER BY days_old DESC
LIMIT 10;
```

## Next Steps

1. **Verify data**: Run validation queries above
2. **Analyze patterns**: `python maintain.py` → Option 7 (growth metrics)
3. **Backup database**: `mysqldump -u root -p dvdrental_live > backup.sql`
4. **Modify & rerun**: Adjust configuration and rerun for different scenarios
5. **Export for testing**: Use database for integration tests, reporting, etc.

## File Structure

```
/workspaces/dvdrental_live/
├── master_simulation.py          # Main orchestration script
├── MASTER_SIMULATION_GUIDE.md    # Full documentation
├── MASTER_SIMULATION_QUICK_REF.md # This file
├── generator.py                  # Initial setup
├── incremental_update.py         # Weekly transactions
├── inventory_manager.py          # Inventory additions
├── maintain.py                   # Database maintenance
└── config.json                   # Database credentials
```

## Tips & Tricks

### Speed Up by Reducing Batch Size
Edit line ~283 in master_simulation.py:
```python
batch_size = 2  # Was 4, now processes 2 weeks at a time (slower but uses less memory)
```

### Add Custom Inventory Schedule
For specific business strategy:
```python
INVENTORY_ADDITIONS = [
    (0, 0, "Initial"),
    (8, 30, "Monthly refresh Q1"),   # More frequent additions
    (16, 30, "Monthly refresh Q1"),
    (24, 30, "Monthly refresh Q1"),
    # ... add monthly instead of quarterly
]
```

### Aggressive Seasonal Boost
For dramatic seasonal effect:
```python
SEASONAL_MULTIPLIERS = {
    6: 200,   # 200% boost in June (2x normal)
    7: 250,   # 250% boost in July (2.5x normal)
    8: 180,   # 180% boost in August
    # Other months default to 0 (normal)
}
```

### Conservative Growth
Reduce weekly growth rate by modifying generator.py:
```python
# Line ~382 in generator.py
volume_growth = 1 + (week_number * 0.01)  # Was 0.02 (2%), now 0.01 (1%)
```
