# Level 1: Basic Generator

## Purpose
**Simple database initialization for demos and learning**

Creates a clean DVD rental database with 14 core tables and populates it with 12 weeks of realistic transaction data. Use this for:
- Learning SQL fundamentals
- Building basic dashboards
- Testing BI tool connections
- Simple business logic examples

## What It Creates

### Schema (schema_base.sql)
14 normalized tables:
- Reference: `country`, `city`, `language`, `category`, `actor`
- Core: `film`, `film_actor`, `film_category`, `address`
- Operations: `store`, `staff`, `customer`
- Transactions: `inventory`, `rental`, `payment`

### Data (generator.py)
- 12 weeks of transaction history (12 stores × 100 customers × realistic activity)
- ~6,000 rental transactions
- Realistic customer lifecycle (acquisition, churn, return patterns)
- Seasonal patterns and spike days
- Early week returns, late week rentals

## Quick Start

### 1. Initialize Database
```bash
cd level_1_basic
python generator.py
```

### 2. Verify Setup
```bash
python ../shared/validate.py
```

### 3. Analyze
```bash
mysql -u root -p -e "SELECT COUNT(*) FROM rental;"
```

## Command-Line Arguments

```bash
# Default: creates 'dvdrental_live' database
python generator.py

# Override database name
python generator.py --database my_test_db

# Seasonal boost percentage (e.g., 50 for 50% boost)
python generator.py --season 50

# Combine arguments
python generator.py --database custom_db --season 30

# No seasonal boost
python generator.py --season 0
```

### Argument Reference

| Argument | Default | Description |
|----------|---------|-------------|
| `--database` | `dvdrental_live` | Override the database name |
| `--season` | 0 | Seasonal boost percentage (e.g., 50 = 50% boost, 0 = no seasonality) |

## Configuration

Database credentials: `../shared/configs/config.json`

## Output Statistics

After running:
- **Total Rentals**: ~6,000
- **Active Customers**: ~500
- **Stores**: 12
- **Films**: 1,000 (seeded from `sakila` dataset)
- **Data Range**: 12 weeks of realistic business activity

## What Comes Next?

Once Level 1 is working:
- **Level 2**: Add more weeks incrementally with `incremental_update.py`
- **Level 3**: Use Level 1 as base for master simulation with film releases & inventory scheduling
- **Level 4**: Build advanced simulation with seasonality and business story

## Key Concept
✅ **No add-ons** - This is pure core DVD rental logic. No film releases, no inventory scheduling, no advanced tracking. Perfect for teaching fundamentals.
