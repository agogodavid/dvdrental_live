# 🎓 DVD Rental Live - Progressive Database Simulation System

A **4-level progressive learning system** for database design, data engineering, business intelligence, and advanced analytics. From simple SQL fundamentals to sophisticated 10-year business lifecycle simulations.

---

## 🚀 Quick Start: Level 4 (Recommended for 10-Year Simulations)

```bash
# Generate complete 10-year dataset with all advanced features
python level_4_advanced_master/master_simulation.py
```

**What you get:**
- 520 weeks (10 years) of transaction data (~200,000+ rentals)
- Complete business lifecycle (growth → plateau → decline → reactivation)
- Customer segmentation and churn modeling
- Late fees and accounts receivable (AR) tracking
- Inventory status management
- Film releases and strategic inventory purchasing

**📖 Read:** [QUICKSTART_LEVEL4.md](QUICKSTART_LEVEL4.md) | [LEVEL_ARCHITECTURE.md](LEVEL_ARCHITECTURE.md)

---

## 📚 All Levels

### **Level 1: Basic Foundations**
```bash
python generator.py
```
Simple starter database for SQL learning (100 films, 200 customers, basic transactions)

### **Level 2: Incremental Growth**
```bash
python level_2_incremental/incremental_update.py 10 --database dvdrental_live
```
Add weeks incrementally with growth multipliers and seasonal variations

### **Level 3: Master Simulation (5 Years)**
```bash
python level_3_master_simulation/master_simulation.py
```
Multi-year simulation with film releases and inventory strategies

### **Level 4: Advanced Master (10 Years)** ⭐
```bash
python level_4_advanced_master/master_simulation.py
```
**Complete enterprise-grade business simulation** - THE DEFINITIVE TOOL

---

## 🎯 Common Arguments (All Levels)

```bash
# Override database name
--database my_custom_db

# Control seasonality (percentage boost)
--season 50      # 50% seasonal boost
--season 0       # No seasonality

# Level 4 specific: Custom config
--config config_10year_advanced.json

# Examples:
python level_4_advanced_master/master_simulation.py --database my_10year_data
python level_2_incremental/incremental_update.py 5 --seasonal 30 --database dvdrental_live
```

---

## 📖 Documentation

| Document | Purpose |
|----------|---------|
| **[QUICKSTART_LEVEL4.md](QUICKSTART_LEVEL4.md)** | Get started immediately with Level 4 |
| **[LEVEL_ARCHITECTURE.md](LEVEL_ARCHITECTURE.md)** | Complete system overview and narrative |
| [FILM_GENERATOR_README.md](FILM_GENERATOR_README.md) | Film generation system |
| [MASTER_SIMULATION_GUIDE.md](MASTER_SIMULATION_GUIDE.md) | Level 3/4 deep dive |
| [INVENTORY_QUICKSTART.md](INVENTORY_QUICKSTART.md) | Inventory management |

## Repository Structure

```
📁 dvdrental_live/
├── 📚 docs/
│   ├── START_HERE.md ⭐ Read this first
│   ├── guides/
│   └── archive/ (legacy docs)
│
├── 🎓 level_1_basic/ (12 weeks, simple)
│   ├── generator.py
│   ├── schema_base.sql
│   └── README.md
│
├── 🔄 level_2_incremental/ (add weeks)
│   ├── incremental_update.py
│   └── README.md
│
├── 📈 level_3_master_simulation/ (10 years, film releases)
│   ├── master_simulation.py
│   ├── schema_film_releases.sql
│   ├── film_system/
│   ├── inventory_system/
│   └── README.md
│
├── 🚀 level_4_advanced_master/ (10 years, seasonality, business story)
## Common Commands

```bash
# Verify setup
python shared/validate.py

# Database maintenance
python shared/maintain.py stats
python shared/maintain.py optimize
python shared/maintain.py backup

# Analyze data
mysql -u root -p dvdrental_live < shared/analysis/analysis_queries.sql
```

## Learning Paths

### Path 1: Teaching SQL (4 weeks)
- Week 1: Level 1 setup & schema exploration
- Week 2: SQL SELECT queries
- Week 3: JOINs and aggregations  
- Week 4: Subqueries and optimization

### Path 2: Data Engineering (6 weeks)
- Weeks 1-2: Level 1 understanding
- Weeks 3-4: Level 2 incremental loading
- Weeks 5-6: Build ETL pipeline

### Path 3: Business Modeling (8 weeks)
- Weeks 1-2: Level 1 core concepts
- Weeks 3-4: Level 3 setup
- Weeks 5-7: Analyze film releases & inventory
- Week 8: Build KPI dashboard

### Path 4: Advanced Analytics (10 weeks)
- Weeks 1-2: Level 1
- Weeks 3-4: Level 3
- Weeks 5-7: Level 4 advanced simulation
- Weeks 8-9: AR aging, late fees analysis
- Week 10: Final project

## Troubleshooting

### MySQL connection error
```bash
mysql -u root -p -e "SELECT 1"
# Verify credentials in shared/configs/config.json
```

### Python dependencies missing
```bash
pip install -r requirements.txt
```

### Database already exists
```bash
# Change database name in config, or
mysql -u root -p -e "DROP DATABASE old_name;"
```

## 📖 Documentation

- **START HERE**: [`docs/START_HERE.md`](docs/START_HERE.md) ⭐
- **Level 1**: [`level_1_basic/README.md`](level_1_basic/README.md)
- **Level 2**: [`level_2_incremental/README.md`](level_2_incremental/README.md)
- **Level 3**: [`level_3_master_simulation/README.md`](level_3_master_simulation/README.md)
- **Level 4**: [`level_4_advanced_master/README.md`](level_4_advanced_master/README.md)
- **Configs**: [`shared/configs/README.md`](shared/configs/README.md)

## 🚀 Next Steps

**New to this repo?** Start here: [`docs/START_HERE.md`](docs/START_HERE.md)

For instructors and advanced users, each level has comprehensive README files explaining what's included and how to use it.

## Usage Examples

**Level 1: Basic 12-Week Generator**:
```bash
cd level_1_basic

# Default: creates dvdrental_live database
python generator.py

# Custom database
python generator.py --database my_test_db

# With 50% seasonal boost
python generator.py --season 50 --database my_test_db

# No seasonal boost
python generator.py --season 0
```

**Level 2: Incremental Updates**:
```bash
cd level_2_incremental

# Add 4 weeks to default database
python incremental_update.py 4

# Add 4 weeks to custom database
python incremental_update.py 4 --database my_custom_db
```

**Level 3: Master Simulation (10 years)**:
```bash
cd level_3_master_simulation

# Default: interactive with automatic seasonality
python master_simulation.py

# Custom database
python master_simulation.py --database master_10year

# Override with fixed 30% seasonal boost
python master_simulation.py --season 30
```

**Level 4: Advanced 10-Year Simulation**:
```bash
cd level_4_advanced_master

# Default: loads config_10year_advanced.json
python run_advanced_simulation.py

# Custom database override
python run_advanced_simulation.py --database advanced_test

# Use different config file
python run_advanced_simulation.py --config config_10year.json

# Combine options with 40% seasonal boost
python run_advanced_simulation.py --config config_10year.json --database my_db --season 40
```

## Features

- Database creation with schema
- Realistic transaction patterns
- Seasonal demand fluctuations
- Customer lifecycle simulation
- Inventory management
- Payment tracking

## Troubleshooting

1. **Database Connection Errors**:
   - Verify MySQL server is running
   - Check credentials in `config.json`
   - Ensure MySQL user has CREATE/DROP privileges

2. **Missing Dependencies**:
   - Run `pip install -r requirements.txt`

3. **Permission Issues**:
   - Use `sudo` if needed for system-wide installations
   - Verify file permissions for `schema.sql`