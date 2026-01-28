# 10-Year DVD Rental Simulation - Performance Guide

## 📊 Simulation Overview

**Total Scale:**
- **520 weeks** (10 years)
- **968,740 total rentals**
- **~1GB database size**
- **3,420 weekly transactions** (final year)

**Growth Pattern:**
- **Year 1:** 612 transactions/week
- **Year 5:** 1,860 transactions/week  
- **Year 10:** 3,420 transactions/week
- **Total Growth:** 11.4x increase over 10 years

## ⚡ Performance Optimizations

### 1. Database Configuration

```sql
-- Enable performance optimizations
SET GLOBAL innodb_buffer_pool_size = 256M;  -- For 1GB database
SET GLOBAL innodb_log_file_size = 64M;
SET GLOBAL innodb_flush_method = O_DIRECT;
SET GLOBAL query_cache_size = 64M;
SET GLOBAL tmp_table_size = 64M;
SET GLOBAL max_heap_table_size = 64M;
```

### 2. Index Strategy

```sql
-- Essential indexes for large dataset performance
CREATE INDEX idx_rental_date ON rental(rental_date);
CREATE INDEX idx_rental_customer_id ON rental(customer_id);
CREATE INDEX idx_rental_inventory_id ON rental(inventory_id);
CREATE INDEX idx_rental_return_date ON rental(return_date);
CREATE INDEX idx_payment_rental_id ON payment(rental_id);
CREATE INDEX idx_payment_customer_id ON payment(customer_id);
CREATE INDEX idx_customer_activebool ON customer(activebool);
CREATE INDEX idx_inventory_film_id ON inventory(film_id);
CREATE INDEX idx_inventory_store_id ON inventory(store_id);
```

### 3. Optimized Configuration

```json
{
  "mysql": {
    "host": "localhost",
    "user": "root", 
    "password": "root",
    "database": "dvdrental_10year"
  },
  "simulation": {
    "start_date": "2001-12-30",
    "initial_weeks": 520
  },
  "generation": {
    "films_count": 500,                    // More films for variety
    "stores_count": 3,                     // More stores for realism
    "initial_customers": 100,              // Larger initial base
    "weekly_new_customers": 15,            // Higher growth rate
    "base_weekly_transactions": 400,       // Higher base volume
    "customer_churn_after_weeks": 8,       // Longer customer lifetime
    "churn_rate": 0.3,                     // Lower churn rate
    "loyal_customer_rate": 0.25,           // More loyal customers
    "rental_duration_min": 2,
    "rental_duration_max": 10,             // Wider rental range
    "spike_day_probability": 0.08,         // More spike days
    "spike_day_multiplier": 3              // Lower spike multiplier
  },
  "performance": {
    "batch_size": 1000,                    // Batch inserts
    "commit_frequency": 5000,              // Commit every 5k records
    "disable_autocommit": true,            // Manual transaction control
    "use_prepared_statements": true,       // Prepared statement optimization
    "enable_bulk_inserts": true            // Bulk insert optimization
  }
}
```

## 🚀 Generation Strategy

### Option 1: Full 10-Year Generation (Recommended)

```bash
# Create optimized database
mysql -u root -p -e "CREATE DATABASE dvdrental_10year CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# Run full simulation
python master_simulation.py --config config_10year.json
```

### Option 2: Incremental Generation

```bash
# Generate in chunks to monitor progress
python incremental_update.py 52 --database dvdrental_10year  # Year 1
python incremental_update.py 52 --database dvdrental_10year  # Year 2
# ... repeat for each year
```

### Option 3: Parallel Generation

```bash
# Generate different years in parallel (requires separate databases)
python master_simulation.py --config config_year1.json &
python master_simulation.py --config config_year2.json &
# ... run multiple instances
```

## 📈 Performance Monitoring

### Real-time Progress Tracking

```python
# Add to generator.py for progress monitoring
def log_progress(week_num, total_weeks, transactions_this_week):
    progress = (week_num / total_weeks) * 100
    print(f"Progress: {progress:.1f}% | Week {week_num}/{total_weeks} | "
          f"Transactions: {transactions_this_week:,}")
```

### Database Size Monitoring

```sql
-- Monitor database growth
SELECT 
    table_name,
    ROUND(((data_length + index_length) / 1024 / 1024), 2) AS 'Size in MB'
FROM information_schema.tables 
WHERE table_schema = 'dvdrental_10year'
ORDER BY (data_length + index_length) DESC;
```

### Performance Benchmarks

**Expected Performance:**
- **Generation Time:** 2-4 hours (depending on hardware)
- **Insert Rate:** 500-1000 records/second
- **Query Performance:** <1 second for most views
- **Memory Usage:** 200-500MB during generation

## 🔧 Troubleshooting

### Memory Issues

```python
# Add memory optimization to generator.py
import gc

def optimize_memory():
    gc.collect()  # Force garbage collection
    # Add periodic memory cleanup
```

### Slow Performance

```sql
-- Disable indexes during bulk insert, re-enable after
ALTER TABLE rental DISABLE KEYS;
-- ... bulk insert ...
ALTER TABLE rental ENABLE KEYS;
```

### Disk Space

```bash
# Monitor disk usage
df -h /var/lib/mysql/

# Clean up old binary logs
PURGE BINARY LOGS BEFORE DATE(NOW() - INTERVAL 7 DAY);
```

## 📊 Analysis Capabilities

### Business Intelligence Queries

```sql
-- Annual growth analysis
SELECT 
    YEAR(rental_date) as year,
    COUNT(*) as total_rentals,
    AVG(DATEDIFF(return_date, rental_date)) as avg_rental_duration,
    COUNT(CASE WHEN return_date IS NULL THEN 1 END) as overdue_rentals
FROM rental 
GROUP BY YEAR(rental_date)
ORDER BY year;

-- Customer lifetime value
SELECT 
    customer_id,
    COUNT(*) as total_rentals,
    SUM(amount) as total_spent,
    AVG(amount) as avg_transaction,
    MAX(rental_date) - MIN(rental_date) as customer_lifetime_days
FROM rental r
JOIN payment p ON r.rental_id = p.rental_id
GROUP BY customer_id
ORDER BY total_spent DESC;
```

### Late Fee Analysis

```sql
-- Late fee revenue over time
SELECT 
    DATE(rental_date) as date,
    COUNT(*) as rentals,
    SUM(CASE WHEN return_date IS NOT NULL AND 
               DATEDIFF(return_date, DATE_ADD(rental_date, INTERVAL rental_duration DAY)) > 0 
          THEN DATEDIFF(return_date, DATE_ADD(rental_date, INTERVAL rental_duration DAY)) * 1.50 
          ELSE 0 END) as late_fee_revenue
FROM rental r
JOIN inventory i ON r.inventory_id = i.inventory_id
JOIN film f ON i.film_id = f.film_id
GROUP BY DATE(rental_date)
ORDER BY date DESC;
```

## 🎯 Recommendations

### For Maximum Realism:
1. **Use full 10-year generation** for complete business lifecycle
2. **Enable all performance optimizations** for smooth operation
3. **Monitor database growth** to ensure adequate storage
4. **Use the late fees views** for comprehensive business analysis

### For Performance Testing:
1. **Generate in chunks** to test scalability
2. **Monitor query performance** across different time periods
3. **Test concurrent access** with multiple users
4. **Benchmark different configurations**

### For Business Analysis:
1. **Use the comprehensive views** for trend analysis
2. **Track customer behavior** over the full 10-year period
3. **Analyze seasonal patterns** and business cycles
4. **Calculate ROI** and business metrics

## 📋 Success Criteria

✅ **Database Size:** ~1GB (manageable)
✅ **Generation Time:** 2-4 hours (reasonable)
✅ **Query Performance:** <1 second (excellent)
✅ **Data Quality:** Realistic business patterns
✅ **Analysis Capabilities:** Comprehensive BI views

The 10-year simulation is **highly feasible** and will provide excellent data for business analysis, performance testing, and academic research!