# Level 3: Master Simulation

## Purpose
**Create a realistic 3-10 year dataset with scheduled film releases and inventory management**

Extends Level 1 with business lifecycle scheduling. Perfect for teaching:
- Multi-year business patterns
- Inventory management
- Periodic product releases (film catalog expansion)
- Business growth cycles

## What It Adds Beyond Level 1

### Film Release Scheduling (schema_film_releases.sql)
Tracks when films are added to the catalog:
- `film_releases` table: Quarterly film releases (schedule in config)
- `inventory_purchases` table: When inventory was purchased for films
- Automatic film generation for new categories
- Controllable release schedule

### Inventory Management
- Periodic inventory additions (growth phase: aggressive, plateau: moderate, decline: minimal)
- Inventory purchased by staff members
- Links film releases to inventory additions
- Tracks inventory aging and purchase history

### Business Lifecycle Phases
- **Growth** (Years 1-2): Aggressive inventory growth
- **Plateau** (Years 3-6): Moderate growth, stable operations
- **Decline** (Years 7-8): Conservative inventory additions
- **Reactivation** (Years 9-10): Strategic focused growth

## Quick Start

### 1. Run Simulation
```bash
cd level_3_master_simulation
python master_simulation.py
```

### 2. Verify
```bash
python ../shared/validate.py
```

## Command-Line Arguments

```bash
# Default: loads config.json, database 'dvdrental_live'
python master_simulation.py

# Override database name
python master_simulation.py --database master_10year

# Override with fixed seasonal boost (percentage)
python master_simulation.py --season 50

# Combine arguments
python master_simulation.py --database my_test --season 30
```

### Argument Reference

| Argument | Default | Description |
|----------|---------|-------------|
| `--database` | From config | Override the database name |
| `--season` | From date | Seasonal boost percentage (e.g., 50 = 50% boost, 0 = no seasonality) |

## Configuration File

Uses `../shared/configs/config.json` by default (or `../shared/configs/config_10year.json` for full 10-year run)

Edit config to set:
- Simulation start date
- Duration (weeks)  
- Inventory strategy
- Business phases

## Schema Files

### schema_film_releases.sql
Creates supplemental tables for:
- Film release scheduling
- Inventory purchase tracking

## File Structure

```
level_3_master_simulation/
├── master_simulation.py          ← Main orchestration script
├── config_master.json            ← Configuration
├── schema_film_releases.sql      ← Film release tables
├── film_system/
│   ├── film_generator.py         ← Generate new films
│   └── templates/                ← Film template files
├── inventory_system/
│   ├── inventory_manager.py      ← Manage inventory additions
│   └── (inventory scheduler)
└── README.md
```

## Output Statistics

A typical 10-year (520-week) simulation produces:
- **Weeks**: 520 (10 years)
- **Total Rentals**: 250,000+
- **Customers**: 1,000-2,000
- **Films**: 1,200-1,500 (including releases)
- **Inventory Items**: 5,000-10,000

## What's Different from Level 1?

| Feature | Level 1 | Level 3 |
|---------|---------|---------|
| Duration | 12 weeks | 3-10 years |
| Film Releases | No | Yes (quarterly) |
| Inventory Management | Basic | Scheduled additions |
| Business Lifecycle | None | Growth/Plateau/Decline |
| Data Volume | Small | Large |
| Teaching Use | Basics | Business cycles |

## Common Tasks

```bash
# Run full 10-year simulation
python master_simulation.py config_10year.json

# Run 3-year simulation for class demo
python master_simulation.py config_3year.json

# Monitor progress during run
tail -f simulation.log

# Analyze results after completion
python ../validate.py
mysql -u root -p dvdrental_master < ../shared/analysis/sample_queries.sql
```

## What Comes Next?

Once Level 3 is working:
- **Level 4**: Add seasonality, customer behavior patterns, and "story" to create realistic epoch datasets

## Key Concepts

✅ **Extends Level 1**: Uses same core rental logic
✅ **Scheduled Extensions**: Film releases on predictable schedule
✅ **Business Lifecycle**: Models growth/plateau/decline phases
✅ **Student-Ready**: Perfect for teaching business cycles and inventory management

## Dependencies

- Level 1 basic generator must work
- Requires film templates in `film_system/templates/`
- Requires inventory_manager.py
