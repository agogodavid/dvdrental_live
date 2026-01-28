# Level 4: Advanced Master Simulation

## Purpose
**Create sophisticated 10-year epoch datasets with seasonality, customer behavior patterns, and business "story"**

Extends Level 3 with advanced business modeling. Perfect for teaching:
- Complex customer segmentation
- Seasonal demand patterns
- Business intelligence concepts
- Advanced analytics with late fees and AR (Accounts Receivable)
- Multi-year trend analysis
- Realistic business challenges (overdue rentals, collections)

## What It Adds Beyond Level 3

### Advanced Features (schema_advanced_features.sql)

#### Inventory Status Tracking
- Real-time inventory status: available, rented, damaged, missing, maintenance
- Historical status changes
- Staff assignments for inventory management

#### Late Fees Tracking
- Automatic late fee calculation ($1.50/day overdue)
- Payment tracking
- AR (Accounts Receivable) aging
- Dispute tracking

#### Customer AR (Accounts Receivable)
- Total owed vs. paid tracking
- AR balance and status (current, 30/60/90+ days)
- Days past due calculations
- Collection notes

#### Rental Status Lifecycle
- Full rental state tracking: active → overdue → completed/lost
- Days since rental and expected return
- Overdue day tracking
- Dispute flags

### Business Lifecycle with Seasonality

#### Business Phases (10-Year Story)
- **Growth Phase (Weeks 1-104)**: 2% volume multiplier, new customer acquisition, aggressive inventory growth
- **Plateau Phase (Weeks 105-312)**: 1% volume multiplier, stable customer base, moderate inventory growth
- **Decline Phase (Weeks 313-416)**: -1% volume multiplier, customer churn acceleration, conservative inventory
- **Reactivation Phase (Weeks 417-520)**: -0.5% → +0.5%, customer recovery, strategic growth

#### Seasonal Multipliers
- Winter (Nov-Dec, Jan): +20-25% (holiday entertainment)
- Spring (Mar-May): +5-15% (seasonal refresh)
- Summer (Jun-Aug): +25-30% (peak vacation season)
- Fall (Sep-Oct): +10-15% (back-to-school)

#### Customer Segments
- **Premium** (15%): 2x activity, 10% churn, 12-week lifetime
- **Regular** (40%): 1x activity, 40% churn, 5-week lifetime
- **Casual** (35%): 0.5x activity, 60% churn, 3-week lifetime
- **Dormant** (10%): 0.1x activity, eventual reactivation

### Advanced Tracking System

Tracks everything needed for business analytics:
- Late fees by customer, time period, film category
- AR aging for collections strategy
- Inventory utilization and status
- Customer segment behavior
- Seasonal demand patterns
- Business phase metrics

## Quick Start

### 1. Configure
Edit `../shared/configs/config_10year_advanced.json` to set:
- Advanced tracking enabled
- Seasonal volatility
- Customer churn rates
- Late fee calculations
- Business phase timeline

### 2. Run Simulation
```bash
# From workspace root or level_4_advanced_master directory
python level_4_advanced_master/adv_master_simulation.py
```

### 3. Analyze Results
```bash
# View late fees and AR
mysql -u root -p dvdrental_10year_advanced -e "
SELECT ar_status, COUNT(*), SUM(ar_balance) 
FROM customer_ar 
WHERE ar_balance > 0 
GROUP BY ar_status;
"
```

## Command-Line Arguments

```bash
# Default: loads config_10year_advanced.json, database 'dvdrental_10year_advanced'
python level_4_advanced_master/adv_master_simulation.py

# Override database name
python level_4_advanced_master/adv_master_simulation.py --database my_advanced_test

# Use different config file
python level_4_advanced_master/adv_master_simulation.py --config config_custom.json

# Override with fixed seasonal boost (percentage)
python level_4_advanced_master/adv_master_simulation.py --season 40

# Combine arguments
python level_4_advanced_master/adv_master_simulation.py --database test_db --season 25
```

### Argument Reference

| Argument | Default | Description |
|----------|---------|-------------|
| `--config` | `config_10year_advanced.json` | Configuration file to use |
| `--database` | From config | Override the database name |
| `--season` | From config | Seasonal boost percentage (e.g., 50 = 50% boost, 0 = no seasonality) |

## Configuration Files

Uses `../shared/configs/config_10year_advanced.json` by default

Available configs:
- `config_10year_advanced.json` - Full advanced simulation with all features
- `config_10year.json` - 10-year simulation without AR/late fees tracking

Edit config to set:
- Advanced tracking enabled/disabled
- Seasonal volatility
- Customer churn rates
- Business phase timeline
  }
}
```

## Schema Files

### schema_advanced_features.sql
Creates advanced tracking tables:
- `inventory_status`: Real-time inventory tracking
- `late_fees`: Late fee calculations and tracking
- `customer_ar`: Accounts receivable tracking
- `rental_status_tracking`: Rental lifecycle tracking
- `seasonality_log`: Seasonality adjustments
- Views: `late_fees_view` for business analysis

## File Structure

```
level_4_advanced_master/
├── adv_master_simulation.py         ← Main unified simulation (THE definitive tool)
└── README.md                        ← This file

archive/level_4_deprecated/
└── run_advanced_simulation.py       ← Legacy (archived)

../shared/configs/
├── config_10year_advanced.json      ← Level 4 config (10 years, all features)
└── config.json                      ← Level 1-3 config

../level_1_basic/
└── schema_base.sql                  ← Base schema with late_fees, customer_ar, inventory_status tables
```

## Output Statistics

A typical advanced 10-year simulation produces:
- **Weeks**: 520 (10 years)
- **Total Rentals**: 300,000+ (with seasonality)
- **Late Fees**: 15,000-25,000 (based on churn & returns)
- **Total AR**: $50,000-$100,000 (cumulative collections)
- **Customer Segments**: 150-300 customers in each segment
- **Business Phases**: Clear growth/plateau/decline/recovery story in data

## What's Different from Level 3?

| Feature | Level 3 | Level 4 |
|---------|---------|---------|
| Seasonality | None | Full annual cycle |
| Customer Segments | Generic | 4 segments w/ different behavior |
| Late Fees | No | Yes ($1.50/day) |
| AR Tracking | No | Yes (aging, status, collections) |
| Inventory Tracking | Basic | Advanced (status, audit trail) |
| Rental Lifecycle | Simple | Complex (active/overdue/lost) |
| Business Story | Generic growth | Multi-phase with reactivation |
| Data Realism | Good | Excellent (includes business challenges) |
| Student Use | Business cycles | Realistic business problems |

## Analysis Queries Included

After running, you can analyze:
- Late fees by customer aging bucket
- Top delinquent customers
- Films with highest return delays
- Seasonal demand variations by category
- Customer segment profitability
- Inventory utilization rates
- Collections success rates

## Common Tasks

```bash
# Run full advanced 10-year simulation (RECOMMENDED)
python level_4_advanced_master/adv_master_simulation.py

# Custom database
python level_4_advanced_master/adv_master_simulation.py --database my_10year_data

# View late fees summary
mysql -u root -p dvdrental_10year_advanced -e "
SELECT COUNT(*) as overdue_count, SUM(total_fee) as total_fees 
FROM late_fees WHERE paid = FALSE;
"

# Analyze AR aging
mysql -u root -p dvdrental_10year_advanced -e "
SELECT ar_status, COUNT(*) as customers, SUM(ar_balance) as total_owed
FROM customer_ar WHERE ar_balance > 0 
GROUP BY ar_status;
"

# Export data for BI tool
mysqldump -u root -p dvdrental_10year_advanced > backup_10year_advanced.sql
```

## Teaching with Level 4

### Concepts You Can Teach

1. **Business Lifecycle**: Model growth/plateau/decline in real data
2. **Seasonality**: Show how holidays/seasons affect rentals
3. **Customer Segmentation**: Different behavior patterns in actual queries
4. **Collections**: Real AR aging and late fees problem
5. **Inventory Management**: Stock levels across business phases
6. **Data Quality**: Overdue rentals and disputes in real data
7. **Business Analytics**: KPIs and metrics over multi-year period

### Sample Assignments

```sql
-- What segment has highest late fees?
SELECT 
    CASE WHEN r.rental_id IN (...premium...) THEN 'Premium'
         WHEN r.rental_id IN (...regular...) THEN 'Regular' 
         END as segment,
    SUM(lf.total_fee) as total_late_fees,
    COUNT(*) as fee_count
FROM late_fees lf
JOIN rental r ON lf.rental_id = r.rental_id
GROUP BY segment
ORDER BY total_late_fees DESC;

-- What percentage of rentals have late fees?
SELECT 
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM rental), 2) as pct_late_rentals
FROM late_fees;

-- AR aging distribution
SELECT 
    ar_aging_category,
    COUNT(*) as num_fees,
    SUM(remaining_balance) as total_owed
FROM late_fees_view
GROUP BY ar_aging_category
ORDER BY num_fees DESC;
```

## What Comes Next?

This is the final level! Level 4 creates production-ready epoch datasets for:
- Graduate-level databases courses
- Business intelligence demonstrations
- Advanced analytics training
- Real-world problem solving

## Key Concepts

✅ **Builds on Level 3**: Uses all Master Simulation features
✅ **Advanced Patterns**: Seasonality, segments, lifecycle
✅ **Business Problems**: Late fees, AR, collections
✅ **Epoch Datasets**: Complete 10-year stories with realistic challenges
✅ **Production Quality**: Suitable for graduate education and BI training
**Main Script:** `master_simulation.py` (unified Level 4 tool)
- **Base Generator:** `../generator.py` (Level 1)
- **Film System:** `../level_3_master_simulation/film_system/film_generator.py`
- **Inventory Manager:** `../enhanced_inventory_manager.py`
- **Configuration:** `../shared/configs/config_10year_advanced.json`

**Note:** `run_advanced_simulation.py` is deprecated. Use `master_simulation.py` instead.es
- Requires `run_advanced_simulation.py` (main orchestrator)
- Requires advanced_incremental_update.py for late fees
- Requires all config files
