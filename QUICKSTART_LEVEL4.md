# 🎯 DVD Rental Simulation - Quick Start

## For 10-Year Advanced Simulation (Recommended) ⭐

```bash
# Generate complete 10-year dataset with all advanced features
python level_4_advanced_master/adv_master_simulation.py
```

**Output:** `dvdrental_10year_advanced` database with:
- 520 weeks (10 years) of transaction data
- Business lifecycle modeling (growth/plateau/decline/reactivation)
- Customer segmentation and churn
- Late fees and AR tracking
- ~200,000+ rental transactions

---

## Quick Command Reference

### Level 4 (Advanced Master - 10 Years)
```bash
# Default run
python level_4_advanced_master/adv_master_simulation.py

# Custom database
python level_4_advanced_master/adv_master_simulation.py --database my_10year_db

# Override seasonality
python level_4_advanced_master/adv_master_simulation.py --season 50  # 50% boost
```

### Level 3 (Master Simulation - 5 Years)
```bash
# Default run
python level_3_master_simulation/master_simulation.py

# Custom database
python level_3_master_simulation/master_simulation.py --database my_5year_db
```

### Level 2 (Incremental Updates)
```bash
# Add 10 weeks to existing database
python level_2_incremental/incremental_update.py 10 --database dvdrental_live

# Add weeks with seasonal boost
python level_2_incremental/incremental_update.py 5 --seasonal 30
```

### Level 1 (Basic Setup)
```bash
# Simple starter database
python generator.py
```

---

## Configuration Files

- **Level 1-3:** `shared/configs/config.json`
- **Level 4:** `shared/configs/config_10year_advanced.json`

---

## What Makes Level 4 Special?

**Level 4 is the ONLY tool you need for complete 10-year simulations:**

✅ Everything from Levels 1-3  
✅ Business lifecycle (4 phases over 10 years)  
✅ Customer segmentation (Super Loyal/Loyal/Average/Occasional)  
✅ Late fees tracking ($1.50/day default)  
✅ Accounts receivable (AR) with aging buckets  
✅ Inventory status management  
✅ Customer churn and reactivation  

---

## Documentation

- **Complete Guide:** [LEVEL_ARCHITECTURE.md](LEVEL_ARCHITECTURE.md)
- **Film System:** [FILM_GENERATOR_README.md](FILM_GENERATOR_README.md)
- **Inventory:** [INVENTORY_QUICKSTART.md](INVENTORY_QUICKSTART.md)
- **Master Sim:** [MASTER_SIMULATION_GUIDE.md](MASTER_SIMULATION_GUIDE.md)

---

## Typical Workflow

1. **Generate 10 years of data:**
   ```bash
   python level_4_advanced_master/adv_master_simulation.py
   ```

2. **Connect and analyze:**
   ```bash
   mysql -u root -p dvdrental_10year_advanced
   ```

3. **Run business queries:**
   ```sql
   -- AR aging analysis
   SELECT ar_status, COUNT(*), SUM(ar_balance)
   FROM customer_ar
   WHERE ar_balance > 0
   GROUP BY ar_status;
   
   -- Yearly performance
   SELECT YEAR(rental_date) as year, 
          COUNT(*) as rentals,
          COUNT(DISTINCT customer_id) as customers
   FROM rental
   GROUP BY YEAR(rental_date);
   ```

---

## Need Help?

- **Level progression:** See [LEVEL_ARCHITECTURE.md](LEVEL_ARCHITECTURE.md)
- **Feature flags:** Edit `config_10year_advanced.json`
- **Film templates:** See `film_templates/*.txt`

**For most users: Just run Level 4!** 🚀
