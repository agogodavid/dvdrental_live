# Master Simulation - Quick Start (60 Seconds)

## The Absolute Simplest Start

### 1. Run (that's it!)
```bash
cd /workspaces/dvdrental_live
python master_simulation.py
```

Press Enter when prompted, wait ~30 minutes.

Done. You now have 3 years of realistic DVD rental data.

---

## Keep Your Existing Database Safe

Don't want to use your current `dvdrental_live` database? Create a new one:

```bash
python master_simulation.py dvdrental_simulation
```

✅ All credentials from config.json (host, user, password)  
✅ Only database name is different (`dvdrental_simulation`)  
✅ Original database stays untouched  
✅ No config.json changes needed  

See [MASTER_SIMULATION_DB_OVERRIDE_CHEATSHEET.md](MASTER_SIMULATION_DB_OVERRIDE_CHEATSHEET.md) for details.

---

## Want 10 Years Instead?

### 1. Edit the file
```bash
# Open in VS Code or your editor
# Line 32: Change this:
TOTAL_WEEKS = 156
# To this:
TOTAL_WEEKS = 520
```

### 2. Extend inventory additions
After line 49 (after the `(104, 50, ...)` line), add:

```python
# Year 4
(118, 60, "Q1 2004 - New year expansion"),
(130, 50, "Q2 2004 - Spring refresh"),
(144, 70, "Q3 2004 - Summer restock"),
(156, 60, "Q4 2004 - Holiday preparation"),

# Years 5-10: Copy the 1-year pattern above and repeat
# Just increment all the first numbers (week) by 52 each time
```

### 3. Run
```bash
python master_simulation.py
```

Wait ~2 hours. You now have 10 years of data.

---

## Example Output

```
╔════════════════════════════════════════════════════════════════════╗
║    MASTER DVD RENTAL SIMULATION - 3 Year Data Generation           ║
╚════════════════════════════════════════════════════════════════════╝

SIMULATION PLAN
Start Date: 2001-10-01
Duration: 156 weeks (~3.0 years)
End Date: 2004-09-27

Inventory Additions Schedule:
  Week   0 (2001-10-01): +  0 items - Initial
  Week  12 (2002-01-14): + 50 items - Q1 2002
  Week  26 (2002-04-29): + 40 items - Q2 2002
  ...

✓ Initial inventory created: 498 items
✓ Initial transactions created: 4821 rentals

📊 Weeks 12-15 (2002-01-14 - ...)
   Seasonal drift: +20% (month: January)
   Progress: 2.8% (4/144 weeks)

... [progress updates] ...

SIMULATION COMPLETE - Database Summary
✓ Total Rentals: 65,234
✓ Active Customers: 1,247
✓ Total Inventory Items: 696 (+198 added)
✓ Data Range: 2001-10-01 to 2004-09-27
✓ Average Rentals per Week: 418

SIMULATION SUCCESSFUL!
```

---

## Timeline

| Action | Time |
|--------|------|
| Start | 0 min |
| Initial setup complete | 5 min |
| Mid-simulation (50%) | 15 min |
| Simulation complete | 30 min |
| Analysis (optional) | 1 min |

**Total: 30 minutes for 3 years of data**

---

## What You Get

- ✅ 65,000+ realistic DVD rentals
- ✅ 1,200+ customers
- ✅ 700 inventory items
- ✅ Seasonal patterns (summer peaks 80-100%)
- ✅ Inventory aging (newer DVDs rented more)
- ✅ Customer lifecycle (growth, churn, loyalty)
- ✅ Complete transaction history Oct 2001 - Sept 2004

---

## After Simulation - Explore Your Data

### View summary statistics
```bash
python maintain.py
# Select option 7: Show growth metrics
```

### Check data quality
```bash
# In MySQL:
USE dvdrental_live;
SELECT COUNT(*) as rentals, 
       COUNT(DISTINCT customer_id) as customers,
       COUNT(DISTINCT inventory_id) as items_rented
FROM rental;
```

### Verify seasonal pattern (should peak June-July)
```sql
SELECT MONTH(rental_date) as month, COUNT(*) as rentals
FROM rental
GROUP BY MONTH(rental_date)
ORDER BY month;
```

---

## Customize It (Advanced - Optional)

### Change start date
Edit line 31:
```python
START_DATE = datetime(2020, 1, 6).date()  # Any date
```

### Change seasonality
Edit lines 51-63:
```python
SEASONAL_MULTIPLIERS = {
    6: 80,   # June: +80% demand
    7: 100,  # July: +100% demand
    # ... other months ...
}
```

### Change inventory schedule
Edit lines 34-49:
```python
INVENTORY_ADDITIONS = [
    (0, 0, "Initial"),
    (12, 50, "First restock"),
    (26, 40, "Second restock"),
    # ... more additions ...
]
```

See **MASTER_SIMULATION_EXAMPLES.md** for 8 complete working examples.

---

## If Something Goes Wrong

| Problem | Fix |
|---------|-----|
| "Connection refused" | Start MySQL: `mysql.server start` |
| "No database selected" | Verify config.json has correct credentials |
| "Unread result found" | Close any other MySQL connections |
| Out of disk space | Check available: `df -h` |
| Very slow | Use faster disk (SSD) or wait longer |

---

## That's It!

You're done. Open a database viewer and explore 3 years of realistic DVD rental data:

```bash
# Quick stats
mysql -u root -p dvdrental_live -e "SELECT COUNT(*) as rentals FROM rental;"

# Or open in MySQL Workbench and browse the data
```

**For complete documentation:** See MASTER_SIMULATION_GUIDE.md  
**For 8 working examples:** See MASTER_SIMULATION_EXAMPLES.md  
**For quick reference:** See MASTER_SIMULATION_QUICK_REF.md

---

## Pro Tips

💡 **Tip 1:** Run overnight for 10 years of data
```bash
# Background process
nohup python master_simulation.py > simulation.log 2>&1 &
```

💡 **Tip 2:** Backup your data after simulation
```bash
mysqldump -u root -p dvdrental_live > backup.sql
```

💡 **Tip 3:** Different scenarios = just re-run with different config
- Change TOTAL_WEEKS, SEASONAL_MULTIPLIERS, or INVENTORY_ADDITIONS
- Re-run script
- Different simulation each time

💡 **Tip 4:** Use this data for:
- ✅ Database performance testing
- ✅ Analytics and reporting practice
- ✅ Business intelligence demos
- ✅ Learning SQL on realistic data
- ✅ Testing rental application logic

---

## Next Steps

1. ✅ Run the simulation: `python master_simulation.py`
2. ✅ Explore the data: `python maintain.py`
3. ✅ Write SQL queries against realistic data
4. ✅ Build analytics/reports
5. ✅ Test your application

Enjoy your realistic DVD rental database! 🎬📀
