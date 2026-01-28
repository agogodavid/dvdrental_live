# 🎓 DVD Rental Live - A Progressive Learning System

## Welcome!

This is a **4-level progressive database system** designed for teaching and learning:

- **Level 1**: Basic generator for learning SQL fundamentals
- **Level 2**: Incremental updates for understanding data growth
- **Level 3**: Master simulation with business lifecycle and scheduling
- **Level 4**: Advanced simulation with seasonality and business "story"

Choose your level based on what you want to learn or demonstrate.

---

## 🚀 Quick Navigation

### I want to learn/teach basic database concepts
→ **Start with [Level 1: Basic Generator](level_1_basic/README.md)**
- Learn core SQL
- Understand relational design
- Build simple dashboards
- 12 weeks of sample data

### I want to grow data incrementally
→ **Use [Level 2: Incremental Updates](level_2_incremental/README.md)**
- Add weeks at a time
- Understand temporal data
- Perfect for testing ETL
- Works with Level 1

### I want multi-year business scenarios with film releases
→ **Use [Level 3: Master Simulation](level_3_master_simulation/README.md)**
- 3-10 year datasets
- Quarterly film releases
- Inventory scheduling
- Business growth phases
- ~250,000 transactions

### I want realistic business challenges for advanced students
→ **Use [Level 4: Advanced Master Simulation](level_4_advanced_master/README.md)**
- 10-year datasets with seasonality
- Customer segmentation
- Late fees and collections (AR)
- ~300,000 transactions
- Real business problems to solve

---

## 📊 Level Comparison

| Feature | L1 | L2 | L3 | L4 |
|---------|----|----|----|----|
| **Duration** | 12 weeks | Incremental | 3-10 years | 10 years |
| **Complexity** | Simple | Simple | Intermediate | Advanced |
| **Film Releases** | ❌ | ❌ | ✅ | ✅ |
| **Seasonality** | ❌ | ❌ | ❌ | ✅ |
| **Late Fees** | ❌ | ❌ | ❌ | ✅ |
| **AR Tracking** | ❌ | ❌ | ❌ | ✅ |
| **Transactions** | ~6K | Variable | ~250K | ~300K |
| **Ideal For** | Basics | Growth | Cycles | BI/Analytics |

---

## 🎯 Choose Your Path

### Path 1: Teaching Database Fundamentals (4 weeks)

```
Week 1:  Level 1 - Create & explore
Week 2:  Level 1 - Write SQL queries
Week 3:  Level 1 - Design analysis dashboard
Week 4:  Level 1 - Optimize queries
```

**Output**: Students understand relational design, normalization, basic BI

---

### Path 2: Teaching Data Engineering (6 weeks)

```
Week 1-2:  Level 1 - Understand schema
Week 3-4:  Level 2 - Incremental updates
Week 5:    Level 2 - Build ETL pipeline
Week 6:    Level 2 - Analyze growth patterns
```

**Output**: Students understand incremental data loading, temporal analysis, ETL

---

### Path 3: Teaching Business Data Modeling (8 weeks)

```
Week 1-2:  Level 1 - Core concepts
Week 3-4:  Level 3 - Multi-year simulation
Week 5-6:  Level 3 - Film release modeling
Week 7-8:  Level 3 - Build business metrics dashboard
```

**Output**: Students understand business cycles, product releases, inventory strategy

---

### Path 4: Teaching Advanced Analytics (10 weeks)

```
Week 1-2:   Level 1 - Core concepts
Week 3-4:   Level 3 - Business models
Week 5-7:   Level 4 - Run advanced simulation
Week 8-9:   Level 4 - Collections & AR analysis
Week 10:    Level 4 - Present business insights
```

**Output**: Students understand seasonality, customer segmentation, business challenges, collections

---

## ⚡ 5-Minute Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Level 1 (Basic)
```bash
cd level_1_basic
python ../generator.py
```

### 3. Verify Setup
```bash
python ../validate.py
```

**That's it!** You now have a DVD rental database with 12 weeks of data.

---

## 📁 Repository Structure

```
dvdrental_live/
│
├── 📚 docs/                          ← Documentation (you are here)
│   ├── START_HERE.md                ← This file
│   ├── guides/                       ← Feature-specific guides
│   └── archive/                      ← Legacy documentation
│
├── 🎓 level_1_basic/                ← START HERE if learning basics
│   ├── generator.py                 ← Create database
│   ├── schema_base.sql              ← 14 core tables
│   └── README.md
│
├── 🔄 level_2_incremental/          ← Add weeks incrementally
│   ├── incremental_update.py
│   └── README.md
│
├── 📈 level_3_master_simulation/    ← Multi-year with scheduling
│   ├── master_simulation.py
│   ├── schema_film_releases.sql
│   ├── film_system/
│   │   ├── film_generator.py
│   │   └── templates/
│   ├── inventory_system/
│   │   └── inventory_manager.py
│   └── README.md
│
├── 🚀 level_4_advanced_master/      ← Seasonality & business story
│   ├── run_advanced_simulation.py
│   ├── schema_advanced_features.sql
│   ├── tracking_system/
│   │   └── advanced_incremental_update.py
│   └── README.md
│
├── 🔧 shared/                        ← Shared utilities
│   ├── configs/
│   │   ├── config.json
│   │   ├── config_10year.json
│   │   └── config_10year_advanced.json
│   ├── analysis/
│   │   └── sample_queries.sql
│   └── validate.py
│
├── 📋 tests/                         ← Testing utilities
├── requirements.txt
└── README.md
```

---

## 🔧 Configuration

All levels use `shared/configs/config.json` for:
- MySQL host, user, password
- Database name
- Default parameters

### Customize Config

```json
{
  "mysql": {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "dvdrental_live"
  },
  "simulation": {
    "start_date": "2002-01-01",
    "initial_weeks": 12
  }
}
```

---

## 📊 Common Commands

### Level 1: Basic
```bash
# Initialize database
python level_1_basic/../generator.py

# Verify setup
python validate.py
```

### Level 2: Incremental
```bash
# Add 1 week
python level_2_incremental/../incremental_update.py

# Add 4 weeks
python level_2_incremental/../incremental_update.py 4
```

### Level 3: Master Simulation
```bash
# Run 10-year simulation
cd level_3_master_simulation
python master_simulation.py

# Or with custom config
python master_simulation.py config_master.json
```

### Level 4: Advanced Master
```bash
# Run advanced 10-year simulation
cd level_4_advanced_master
python run_advanced_simulation.py

# Calculate late fees
cd tracking_system
python advanced_incremental_update.py --update
```

---

## 📈 Recommended Learning Sequence

### For Students (First-Time Users)

1. **Start**: Read [Level 1 README](level_1_basic/README.md)
2. **Do**: Run `generator.py` to create database
3. **Learn**: Explore schema with `SELECT * FROM information_schema.tables`
4. **Practice**: Write SQL queries from [analysis_queries.sql](shared/analysis/sample_queries.sql)
5. **Build**: Create a simple dashboard

### For Educators

1. **Prepare**: Decide which level(s) you'll use
2. **Test**: Run each level to understand output
3. **Configure**: Edit configs for your course timeline
4. **Teach**: Use level-specific README for class content
5. **Assign**: Give students queries to answer business questions

### For Data Engineers

1. **Understand**: Review all 4 levels
2. **Design**: Choose implementation level(s)
3. **Build**: Create datasets for your students
4. **Deploy**: Use Level 3-4 for production scenarios
5. **Monitor**: Track simulation progress

---

## 🎓 Teaching Examples

### SQL Query Writing (Level 1)
```sql
-- Which films are most popular?
SELECT f.title, COUNT(*) as rental_count
FROM film f
JOIN inventory i ON f.film_id = i.film_id
JOIN rental r ON i.inventory_id = r.inventory_id
GROUP BY f.film_id
ORDER BY rental_count DESC
LIMIT 10;
```

### Temporal Analysis (Level 2)
```sql
-- Weekly rental growth
SELECT 
    DATE_FORMAT(rental_date, '%Y-%m-%d') as week,
    COUNT(*) as rentals
FROM rental
GROUP BY WEEK(rental_date)
ORDER BY week;
```

### Business Metrics (Level 3)
```sql
-- Revenue by quarter
SELECT 
    QUARTER(payment_date) as quarter,
    YEAR(payment_date) as year,
    SUM(amount) as revenue
FROM payment
GROUP BY year, quarter
ORDER BY year, quarter;
```

### Advanced Analytics (Level 4)
```sql
-- Customer AR aging and collections
SELECT 
    ar_aging_category,
    COUNT(*) as num_customers,
    SUM(remaining_balance) as total_owed
FROM late_fees_view
GROUP BY ar_aging_category
ORDER BY FIELD(ar_aging_category, 
    'Current', '30_days', '60_days', '90_days_plus');
```

---

## 🐛 Troubleshooting

### MySQL Connection Error
```bash
# Check if MySQL is running
mysql -u root -p -e "SELECT 1"

# Verify credentials in config.json
```

### generator.py fails
```bash
# Check Python version (need 3.7+)
python --version

# Install dependencies
pip install -r requirements.txt
```

### Validate.py shows 0 rows
```bash
# Check database was created
mysql -u root -p -e "SHOW DATABASES"

# Check tables exist
mysql -u root -p dvdrental_live -e "SHOW TABLES"
```

### Need help?
- Check level-specific README
- Review config.json
- Check MySQL error log
- See docs/guides/ for detailed topics

---

## 📞 Support

- **Documentation**: See [docs/guides/](docs/guides/) for feature-specific help
- **Troubleshooting**: Check README files in each level folder
- **Questions**: Review configuration in `shared/configs/config.json`
- **Database Issues**: Check [docs/guides/](docs/guides/) for data quality notes

---

## 🎯 Next Steps

**Choose your starting level:**

1. **[Level 1: Basic Generator](level_1_basic/README.md)** - Start here if you're new
2. **[Level 2: Incremental Updates](level_2_incremental/README.md)** - For data growth patterns
3. **[Level 3: Master Simulation](level_3_master_simulation/README.md)** - For business cycles
4. **[Level 4: Advanced Master](level_4_advanced_master/README.md)** - For complex analytics

---

**Ready? [Start with Level 1 →](level_1_basic/README.md)**
