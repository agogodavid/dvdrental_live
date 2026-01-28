# Level 2: Incremental Updates

## Purpose
**Add weeks of data incrementally to an existing database**

Extends any Level 1 database by adding new weeks of transaction data while maintaining realistic customer behavior patterns.

## What It Does

Adds transactional data week-by-week:
- New rental transactions
- Customer lifecycle progression (acquisition & churn)
- Return dates and payments
- Maintains referential integrity
- Preserves business logic from Level 1

## Quick Start

### Add 1 Week
```bash
cd level_2_incremental
python ../incremental_update.py
```

### Add Multiple Weeks
```bash
python ../incremental_update.py 4    # Add 4 weeks
python ../incremental_update.py 52   # Add 1 year
```

## Configuration

Database name and MySQL credentials: `../shared/configs/config.json`

## How It Works

1. **Reads latest data** from existing database
2. **Calculates next week** based on last rental date
3. **Generates transactions** using core business logic
4. **Maintains customer state**:
   - Tracks active vs inactive customers
   - Applies 40% churn rate after 5 weeks of inactivity
   - Brings back inactive customers (~10% reactivation)
5. **Applies patterns**:
   - 2% volume growth per week
   - Random spike days (4x volume)
   - Weekend-to-weekday shifts
   - Early-week returns, late-week rentals

## Database Requirements

Must have a Level 1 database already initialized with `generator.py`

## Output

After each run:
- New rental transactions added
- Payments recorded
- Customer status updated
- Last rental date advanced by 1 week

## Common Tasks

```bash
# Add weeks gradually for incremental growth
for i in {1..52}; do
    python ../incremental_update.py
    echo "Week $i complete"
done

# Monitor growth
python ../validate.py
```

## What Comes Next?

Once Level 2 is working:
- **Level 3**: Use with film releases & inventory scheduling
- **Level 4**: Use with seasonality and advanced business logic

## Key Concept
✅ **No add-ons** - Same as Level 1. Pure core rental logic extended incrementally. Good for building data over time or testing incremental ETL patterns.
