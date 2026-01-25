# Quick Start: Inventory Enhancement

## TL;DR

Your inventory system now tracks **purchase dates** and **staff** for profitability analysis.

### Get Started in 2 Steps:

#### 1. Migrate Your Database (if you have existing data)
```bash
python migrate_inventory_schema.py
```

#### 2. Start Analyzing
```bash
python inventory_analysis.py
```

---

## What's New

| Feature | Benefit |
|---------|---------|
| **date_purchased** | Track when each inventory batch arrived |
| **staff_id** | Know which staff member sourced each batch |

This enables students to:
- 📊 Analyze batch profitability
- 👤 Compare staff performance
- 📈 Calculate ROI by batch
- 🏪 Optimize store inventory allocation
- 💼 Make data-driven purchasing decisions

---

## Using the New Features

### Adding Inventory (with tracking)

**Interactive mode** (easiest):
```bash
python inventory_manager.py
```
Then follow prompts - now includes date and staff selection.

**Python code**:
```python
from inventory_manager import InventoryManager
from datetime import date

manager = InventoryManager(config)
manager.connect()

manager.add_fixed_quantity(
    quantity=100,
    date_purchased=date(2024, 1, 20),
    staff_id=1
)
```

**Master simulation**:
```python
add_inventory_batch(
    mysql_config,
    quantity=50,
    description="January inventory",
    date_purchased=date(2024, 1, 15),
    staff_id=2
)
```

### Analyzing Inventory

**Automated report**:
```bash
python inventory_analysis.py
```

Output includes:
- ✅ Batch profitability analysis
- ✅ Staff performance rankings
- ✅ Aging inventory identification
- ✅ Breakeven analysis
- ✅ Store performance comparison

**Custom SQL** (see INVENTORY_ANALYSIS_GUIDE.md for 7+ queries):
```sql
-- Example: Top 10 most profitable batches
SELECT 
    date_purchased,
    staff_id,
    COUNT(*) as items,
    SUM(rental_rate) * COUNT(DISTINCT rental_id) as revenue,
    SUM(rental_rate) * COUNT(DISTINCT rental_id) - SUM(replacement_cost) as profit
FROM inventory
LEFT JOIN rental ON inventory.inventory_id = rental.inventory_id
GROUP BY date_purchased, staff_id
ORDER BY profit DESC
LIMIT 10;
```

---

## For New Databases

The updated `schema.sql` already includes the new columns:

```bash
# Create database with tracking built-in
mysql -u user -p < schema.sql
```

---

## For Existing Databases

**Safe migration** (handles existing data automatically):

```bash
# 1. Backup first (recommended)
mysqldump -u user -p database > backup.sql

# 2. Run migration
python migrate_inventory_schema.py

# 3. Done! ✓
```

Migration handles:
- ✓ Existing inventory data
- ✓ Foreign key constraints
- ✓ Index creation
- ✓ Default values
- ✓ Multiple runs (idempotent)

---

## Example Analyses

### 1. Which staff member sources best inventory?
```python
analyzer = InventoryAnalyzer(config)
analyzer.connect()
analyzer.get_staff_performance()
# Shows: Items sourced, ROI, profit, utilization rate
```

### 2. Which batches are most profitable?
```python
analyzer.get_batch_profitability()
# Shows: Investment, revenue, profit, ROI%, days in stock
```

### 3. What inventory is aging/underperforming?
```python
analyzer.get_aging_inventory(days_threshold=60)
# Shows: Items not moving, revenue generated, recommendations
```

### 4. How quickly do batches reach breakeven?
```python
analyzer.get_breakeven_analysis()
# Shows: Rentals needed, actual rentals, achievement %
```

---

## Student Learning Path

### Week 1: Understanding Inventory Tracking
- Learn what date_purchased and staff_id represent
- Run basic queries to explore the data
- Understand inventory cost vs. revenue

### Week 2: Analysis & Queries
- Write SQL to analyze batch profitability
- Compare staff performance
- Identify trends in aging inventory

### Week 3: Decision Making
- Recommend which staff sourced best
- Suggest inventory purchasing strategy
- Propose store allocation optimizations

### Week 4: Reporting
- Create visualizations from analysis
- Present findings to "management"
- Justify data-driven recommendations

---

## Common Tasks

**Show me all inventory from a specific date:**
```python
analyzer.get_batch_profitability(date_purchased='2024-01-15')
```

**Find inventory sourced by staff ID 3:**
```sql
SELECT * FROM inventory WHERE staff_id = 3;
```

**Calculate total profit by staff member:**
```sql
SELECT 
    staff_id,
    SUM(rental_rate) * COUNT(rental_id) - SUM(replacement_cost) as total_profit
FROM inventory
GROUP BY staff_id
ORDER BY total_profit DESC;
```

**Find items purchased in January:**
```sql
SELECT * FROM inventory WHERE MONTH(date_purchased) = 1;
```

---

## Troubleshooting

**"Unknown column 'date_purchased'"**
- Solution: Run migration: `python migrate_inventory_schema.py`

**"Foreign key constraint fails on staff_id"**
- Solution: Ensure staff members exist: `SELECT * FROM staff;`

**"No staff members found"**
- Solution: Add staff first or update default in migration script

**"Migration says already exists"**
- This is normal! Script is idempotent and safe to run multiple times

---

## Files Changed

| File | Change |
|------|--------|
| `schema.sql` | Added date_purchased, staff_id columns |
| `inventory_manager.py` | Support new parameters |
| `master_simulation.py` | Support new parameters |

## New Files

| File | Purpose |
|------|---------|
| `migrate_inventory_schema.py` | Migrate existing databases |
| `inventory_analysis.py` | Automated analysis tool |
| `INVENTORY_ANALYSIS_GUIDE.md` | SQL query reference |
| `INVENTORY_ENHANCEMENT_SUMMARY.md` | Detailed documentation |

---

## Next Steps

1. ✅ **Migrate** (if needed): `python migrate_inventory_schema.py`
2. ✅ **Add inventory** with new data: `python inventory_manager.py`
3. ✅ **Analyze** results: `python inventory_analysis.py`
4. ✅ **Create student projects** using the analysis framework

---

## Questions?

See comprehensive guides:
- 📖 `INVENTORY_ENHANCEMENT_SUMMARY.md` - Full documentation
- 📋 `INVENTORY_ANALYSIS_GUIDE.md` - SQL query examples (7+ queries)
- 💻 `inventory_analysis.py` - Example Python analysis
