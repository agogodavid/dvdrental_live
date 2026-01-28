# Configuration Files Guide

## Overview

Configuration files control how each level creates and manages databases. All levels use files in this folder.

## Configuration Files

### config.json (Default / Level 1 & 2)
**For**: Basic generator and incremental updates
**Use Case**: Simple demos, learning, small datasets

```json
{
  "mysql": {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "dvdrental_live"
  },
  "simulation": {
    "start_date": "2001-10-01",
    "initial_weeks": 12
  },
  "generation": {
    "base_weekly_transactions": 500
  }
}
```

### config_10year.json (Level 3 - Master Simulation)
**For**: Master simulation with film releases and inventory scheduling
**Use Case**: 3-10 year business datasets with product releases

```json
{
  "mysql": {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "dvdrental_master"
  },
  "simulation": {
    "start_date": "2002-01-01",
    "initial_weeks": 12,
    "total_weeks": 520
  },
  "generation": {
    "base_weekly_transactions": 500,
    "film_releases": {
      "enabled": true,
      "quarterly": true,
      "films_per_quarter": 20
    }
  }
}
```

### config_10year_advanced.json (Level 4 - Advanced Master Simulation)
**For**: Advanced simulation with seasonality, segments, and business story
**Use Case**: Realistic 10-year epoch datasets with customer behavior and challenges

```json
{
  "mysql": {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "dvdrental_advanced"
  },
  "simulation": {
    "start_date": "2002-01-01",
    "total_weeks": 520
  },
  "generation": {
    "base_weekly_transactions": 500,
    "business_lifecycle": {
      "growth_phase_weeks": 104,
      "plateau_phase_weeks": 208,
      "decline_phase_weeks": 104,
      "reactivation_weeks": 104
    },
    "volume_modifiers": {
      "growth_factor": 0.02,
      "plateau_factor": 0.01,
      "decline_factor": -0.01,
      "reactivation_factor": 0.005
    },
    "seasonal_volatility": 0.1
  }
}
```

## How to Use

### Using Default Configuration

```bash
# Uses config.json automatically
python ../level_1_basic/generator.py
python ../level_2_incremental/incremental_update.py
```

### Using Command-Line Arguments

All scripts support these optional arguments:

```bash
# Override database name
python ../level_1_basic/generator.py --database test_db

# Seasonal boost percentage (e.g., 50 for 50% boost)
python ../level_3_master_simulation/master_simulation.py --season 50

# No seasonality
python ../level_4_advanced_master/run_advanced_simulation.py --season 0

# Combine arguments
python ../level_4_advanced_master/run_advanced_simulation.py --database custom_db --season 30

# Level 4 with custom config
python ../level_4_advanced_master/run_advanced_simulation.py --config config_10year.json
```

### Argument Reference

| Argument | Levels | Default | Description |
|----------|--------|---------|-------------|
| `--database` | All | From config | Override database name |
| `--season` | L1, L3, L4 | From config | Seasonal boost percentage (e.g., 50 = 50% boost, 0 = no seasonality) |
| `--config` | L4 only | config_10year_advanced.json | Configuration file to use |

## Customization Guide

### Change Database Name

Edit any config file:
```json
"mysql": {
  "database": "my_custom_db_name"
}
```

### Change MySQL Credentials

```json
"mysql": {
  "host": "localhost",     // or your server IP
  "user": "your_user",     // your MySQL user
  "password": "your_pass", // your MySQL password
  "database": "dbname"
}
```

### Change Simulation Duration (Level 3)

```json
"simulation": {
  "total_weeks": 156  // 3 years (52 weeks × 3)
  "total_weeks": 260  // 5 years
  "total_weeks": 520  // 10 years
}
```

### Change Film Release Schedule (Level 3)

```json
"generation": {
  "film_releases": {
    "enabled": true,
    "quarterly": true,           // true for quarterly, false for yearly
    "films_per_quarter": 20,     // films added per release
    "release_categories": [      // optional: mix of categories
      "Action", "Drama", "Comedy"
    ]
  }
}
```

### Adjust Seasonality (Level 4)

```json
"generation": {
  "seasonal_volatility": 0.1,  // 0.1 = ±10% variation
  "monthly_multipliers": {      // override defaults
    "summer": 1.30,
    "winter": 1.15,
    "spring": 1.05,
    "fall": 1.10
  }
}
```

### Adjust Customer Segments (Level 4)

```json
"generation": {
  "customer_segments": {
    "premium": {
      "percentage": 0.15,       // 15% of customers
      "churn_rate": 0.10,       // 10% monthly churn
      "activity_multiplier": 2, // 2x activity vs baseline
      "lifetime_weeks": 12      // average 12 weeks active
    },
    "regular": {
      "percentage": 0.40,
      "churn_rate": 0.40,
      "activity_multiplier": 1,
      "lifetime_weeks": 5
    }
  }
}
```

## Creating Custom Configurations

Create a new config file for specific scenarios:

```bash
# Copy a template
cp config_10year.json config_my_class.json

# Edit for your class
nano config_my_class.json

# Use it
cd level_3_master_simulation
python master_simulation.py ../shared/configs/config_my_class.json
```

## Configuration Precedence

Scripts look for config in this order:

1. **Command-line argument** (if provided)
   ```bash
   python script.py /path/to/custom_config.json
   ```

2. **Environment variable** (if set)
   ```bash
   export CONFIG_FILE=/path/to/config.json
   ```

3. **Default location** (`../shared/configs/config.json`)
   ```bash
   python script.py
   ```

## Troubleshooting

### "Config file not found"
- Check file path is correct
- Verify file exists: `ls shared/configs/`

### "MySQL connection failed"
- Verify MySQL is running: `mysql -u root -p`
- Check credentials in config
- Check host address (localhost vs 127.0.0.1)

### "Database already exists"
- Change database name in config, OR
- Drop existing: `mysql -u root -p -e "DROP DATABASE old_db;"`

### "Transaction count too low"
- Increase `base_weekly_transactions` in config
- Increase `total_weeks` for longer simulation

## Quick Reference

| Config File | Use For | Database | Duration |
|-------------|---------|----------|----------|
| config.json | Level 1, 2 | dvdrental_live | 12 weeks |
| config_10year.json | Level 3 | dvdrental_master | 520 weeks (10 years) |
| config_10year_advanced.json | Level 4 | dvdrental_advanced | 520 weeks (10 years) |

## Environment Variables

You can override config values via environment variables:

```bash
# Override database name
export DATABASE_NAME=my_custom_db

# Override MySQL user
export MYSQL_USER=my_user

# Override MySQL password
export MYSQL_PASSWORD=my_pass

# Then run script
python generator.py
```

## For Instructors

### Creating Variant Configurations

```bash
# Create multiple configs for different student groups
cp config_10year.json config_group_1.json
cp config_10year.json config_group_2.json
cp config_10year.json config_group_3.json

# Modify each
# group_1: smaller dataset
# group_2: medium dataset with more films
# group_3: full 10-year with all features

# Distribute to students with instructions
```

### Creating Epoch Datasets

```bash
# For teaching specific concepts
cp config_10year_advanced.json config_seasonality_demo.json
# Increase seasonal_volatility to 0.3 for exaggerated effect

cp config_10year_advanced.json config_churn_demo.json
# Increase churn rates for customer retention problems

cp config_10year_advanced.json config_growth_demo.json
# Extend to 1000+ weeks for multi-decade story
```

---

**Need help?** Check the level-specific README files for more details.
