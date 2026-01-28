# Inventory Aging and Weighted Rental Selection

## Overview

The DVD rental simulation now implements **inventory aging**, where newer inventory items are significantly more likely to be rented than older items. This creates realistic rental patterns where:

- **New releases** get high rental demand immediately
- **Older titles** gradually become less popular
- Physical inventory ages naturally over time

## How It Works

### Schema Changes

The `inventory` table now includes:

```sql
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- When item was added
```

Every inventory item has a creation timestamp that tracks when it entered the store's collection.

### Weighted Selection Algorithm

When generating rental transactions, the system uses **exponential weighting** based on inventory age:

1. **Get all inventory items** sorted by creation date (newest first)
2. **Calculate weight for each item**: `weight = e^(-rank / (total_items / 3))`
   - Newest items (rank 0) get maximum weight
   - Weight decays exponentially for older items
3. **Normalize weights** to sum to 1.0
4. **Random selection** using normalized weights

**Example**: With 100 inventory items:
- Newest 10 items: ~73% of all rentals
- Items 11-30: ~22% of rentals
- Items 31+: ~5% of rentals

## Usage

### Adding New Inventory

Use `inventory_manager.py` to add inventory with automatic timestamps:

```bash
python inventory_manager.py
```

Options:
- **Fixed Quantity**: Add X random items (all timestamped NOW)
- **Percentage Growth**: Grow by X%
- **Per-Film Copies**: Add copies per film per store
- **Popular Films Only**: Add to top-rented films only

All new items get `created_at = NOW()`, making them immediately high-probability for rentals.

### Running Incremental Updates

The incremental update automatically uses weighted selection:

```bash
python incremental_update.py 4
python incremental_update.py 4 --seasonal 50
```

Each transaction automatically favors newer inventory.

## Business Impact

### Realistic Demand Patterns

- **Week 1**: New inventory instantly popular
- **Week 5**: Demand drops as newer items arrive
- **Week 10+**: Old inventory rarely rented

### Inventory Lifecycle

```
Added (t=0)          Popular (weeks 1-3)      Declining (weeks 4-8)      Stale (week 9+)
████████              ████░░░░░               ░░░░░░░░░░                 ░░░░░░░░░░
73% chance           40% chance               10% chance                 <1% chance
```

### Recommendations

1. **Add inventory regularly** - Use `inventory_manager.py` to add copies weekly
2. **Monitor age distribution** - Check which items are getting no rentals
3. **Refresh collection** - Old items with <1% rental probability should be removed

## Technical Details

### Fallback Behavior

If the weighted selection method fails:
- Falls back to uniform random selection
- Prevents transaction failures

### Performance

- Single query per transaction: ~1ms overhead
- Index on `created_at` speeds lookups for large inventories

### Database Setup

For existing databases without `created_at`:
- Add column: `ALTER TABLE inventory ADD created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;`
- All existing items get current timestamp
- This can skew results, so reinitialize for fresh simulation

## Example Workflow

```bash
# 1. Initialize database (creates ~400 items with created_at=NOW)
python generator.py

# 2. Run 4 weeks of transactions (weighted to favor new items)
python incremental_update.py 4

# 3. Add new inventory (50 items with created_at=NOW)
python inventory_manager.py
# Select: Fixed Quantity, enter 50

# 4. Run 4 more weeks (now has mix of old and new items)
python incremental_update.py 4

# Check growth metrics
python maintain.py
# Select: 7 - Show growth metrics
```

## Tuning

The exponential decay factor is hardcoded as `total_items / 3`:

```python
weight = math.exp(-rank / max(1, total_items / 3))
```

To adjust how aggressive the weighting is:
- **More aggressive** (newer items MUCH more popular): Change to `total_items / 2`
- **Less aggressive** (more uniform distribution): Change to `total_items / 5`

Edit in `generator.py` method `_get_weighted_inventory_id()` line ~593.

## Validation

Check actual rental distribution:

```sql
-- Rentals by inventory age (days since creation)
SELECT 
    DATEDIFF(CURDATE(), created_at) as days_since_creation,
    COUNT(r.rental_id) as rental_count,
    ROUND(100 * COUNT(r.rental_id) / SUM(COUNT(r.rental_id)) OVER (), 1) as pct
FROM inventory i
LEFT JOIN rental r ON i.inventory_id = r.inventory_id
GROUP BY DATEDIFF(CURDATE(), created_at)
ORDER BY days_since_creation;
```

Should show exponential decline in rentals as items age.
