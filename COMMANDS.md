# DVD Rental Live - Command Reference

## 🚀 Getting Started

### Initial Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Create database and populate with initial data
python generator.py

# Verify setup was successful
python validate.py
```

---

## 📊 Data Management

### Add New Transaction Data
```bash
# Add 1 week of data
python incremental_update.py

# Add multiple weeks
python incremental_update.py 1   # 1 week
python incremental_update.py 4   # 4 weeks
python incremental_update.py 52  # 1 year
```

### Database Maintenance
```bash
# Show database statistics
python maintain.py stats

# Show business growth metrics
python maintain.py growth

# Check data integrity
python maintain.py integrity

# Optimize all tables for performance
python maintain.py optimize

# Analyze table statistics
python maintain.py analyze

# Show potential slow queries
python maintain.py slow

# Create backup
python maintain.py backup

# Run all checks and optimization
python maintain.py full
```

---

## 🔍 Analysis & Queries

### Quick Validation
```bash
python validate.py
```

### View Pre-built Analysis
```bash
# Show all 10 analysis queries
cat analysis_queries.sql

# Run analysis queries in MySQL
mysql -u root -p dvdrental_live < analysis_queries.sql
```

### Manual MySQL Queries
```bash
# Connect to database
mysql -u root -p dvdrental_live

# View recent rentals
SELECT * FROM rental ORDER BY rental_date DESC LIMIT 10;

# Count transactions per week
SELECT WEEK(rental_date), COUNT(*) FROM rental GROUP BY WEEK(rental_date);

# Customer count
SELECT COUNT(*) FROM customer;

# Revenue summary
SELECT SUM(amount) as total_revenue FROM payment;
```

---

## 🛠️ Database Operations

### Backup & Restore
```bash
# Create backup (automatic filename)
python maintain.py backup

# Manual backup (all data)
mysqldump -u root -p dvdrental_live > backup_$(date +%Y%m%d).sql

# Manual backup (specific table)
mysqldump -u root -p dvdrental_live rental > rental_backup.sql

# Restore from backup
mysql -u root -p dvdrental_live < backup_20260125.sql
```

### Database Inspection
```bash
# List all tables
mysql -u root -p -e "use dvdrental_live; SHOW TABLES;"

# Show table structure
mysql -u root -p -e "use dvdrental_live; DESCRIBE rental;"

# Show all databases
mysql -u root -p -e "SHOW DATABASES;"

# Count records in all tables
mysql -u root -p dvdrental_live -e "
  SELECT 'Customers' as table_name, COUNT(*) as count FROM customer
  UNION ALL SELECT 'Films', COUNT(*) FROM film
  UNION ALL SELECT 'Rentals', COUNT(*) FROM rental
  UNION ALL SELECT 'Payments', COUNT(*) FROM payment;"
```

---

## 📈 Analysis Queries

### 1. Transaction Volume by Week
```sql
SELECT 
  WEEK(rental_date) as week,
  COUNT(*) as transactions
FROM rental
GROUP BY WEEK(rental_date)
ORDER BY week;
```

### 2. Customer Acquisition
```sql
SELECT 
  WEEK(create_date) as week,
  COUNT(*) as new_customers
FROM customer
GROUP BY WEEK(create_date)
ORDER BY week;
```

### 3. Revenue Trend
```sql
SELECT 
  DATE(payment_date) as date,
  SUM(amount) as daily_revenue,
  COUNT(*) as transactions
FROM payment
GROUP BY DATE(payment_date)
ORDER BY date DESC;
```

### 4. Top Films
```sql
SELECT 
  f.title,
  COUNT(r.rental_id) as rentals
FROM film f
LEFT JOIN inventory i ON f.film_id = i.film_id
LEFT JOIN rental r ON i.inventory_id = r.inventory_id
GROUP BY f.film_id, f.title
ORDER BY rentals DESC
LIMIT 20;
```

### 5. Active Customers
```sql
SELECT 
  COUNT(*) as active_customers,
  AVG(DATEDIFF(NOW(), create_date)) as avg_days_customer
FROM customer
WHERE activebool = TRUE;
```

### 6. Store Performance
```sql
SELECT 
  s.store_id,
  COUNT(DISTINCT c.customer_id) as customers,
  COUNT(DISTINCT r.rental_id) as rentals,
  SUM(p.amount) as revenue
FROM store s
LEFT JOIN customer c ON s.store_id = c.store_id
LEFT JOIN rental r ON s.store_id IN (
  SELECT store_id FROM inventory 
  WHERE inventory_id = r.inventory_id
)
LEFT JOIN payment p ON r.rental_id = p.rental_id
GROUP BY s.store_id;
```

### 7. Rental Duration Analysis
```sql
SELECT 
  CASE 
    WHEN DATEDIFF(return_date, rental_date) <= 3 THEN '3 days or less'
    WHEN DATEDIFF(return_date, rental_date) <= 5 THEN '4-5 days'
    ELSE '6+ days'
  END as duration,
  COUNT(*) as count
FROM rental
WHERE return_date IS NOT NULL
GROUP BY duration;
```

### 8. Spike Days (4x normal volume)
```sql
SELECT 
  DATE(rental_date) as date,
  COUNT(*) as volume
FROM rental
GROUP BY DATE(rental_date)
HAVING COUNT(*) > (
  SELECT AVG(daily_count) * 3 FROM (
    SELECT COUNT(*) as daily_count 
    FROM rental 
    GROUP BY DATE(rental_date)
  ) t
)
ORDER BY volume DESC;
```

### 9. Top Customers by Revenue
```sql
SELECT 
  CONCAT(c.first_name, ' ', c.last_name) as customer,
  COUNT(p.payment_id) as payments,
  SUM(p.amount) as total_spent
FROM customer c
LEFT JOIN rental r ON c.customer_id = r.customer_id
LEFT JOIN payment p ON r.rental_id = p.rental_id
WHERE p.payment_id IS NOT NULL
GROUP BY c.customer_id
ORDER BY total_spent DESC
LIMIT 20;
```

### 10. Business Summary
```sql
SELECT 
  'Total Customers' as metric, COUNT(DISTINCT customer_id) as value FROM customer
UNION ALL
SELECT 'Total Rentals', COUNT(*) FROM rental
UNION ALL
SELECT 'Total Revenue', CAST(SUM(amount) as CHAR) FROM payment
UNION ALL
SELECT 'Avg Rental Duration', CAST(AVG(DATEDIFF(return_date, rental_date)) as CHAR)
FROM rental WHERE return_date IS NOT NULL;
```

---

## 🔧 Configuration

### Edit Configuration File
```bash
# View current configuration
cat config.json

# Edit configuration (update MySQL credentials, business parameters)
nano config.json    # or your preferred editor
```

### Common Configuration Changes

**Change MySQL password:**
```json
"mysql": {
  "password": "your_new_password"
}
```

**Increase transaction volume:**
```json
"generation": {
  "base_weekly_transactions": 1000  // Instead of 500
}
```

**Increase churn rate:**
```json
"generation": {
  "churn_rate": 0.6  // Instead of 0.4 (60% vs 40%)
}
```

---

## 📝 Logging & Troubleshooting

### Check for Errors
```bash
python validate.py
```

### Reset Database (Start Over)
```bash
# Delete database
mysql -u root -p -e "DROP DATABASE dvdrental_live;"

# Create fresh
python generator.py
```

### View MySQL Error Log
```bash
# Ubuntu/Linux
sudo tail -f /var/log/mysql/error.log

# macOS
tail -f /usr/local/var/mysql/$(hostname).err
```

### Test MySQL Connection
```bash
mysql -u root -p -e "SELECT 'MySQL is working!';"
```

---

## 🤖 Automation

### Add Weekly Data Automatically (Linux/macOS)

#### Option 1: Cron Job (Runs Every Monday at 2 AM)
```bash
crontab -e
```
Add this line:
```
0 2 * * MON /usr/bin/python3 /full/path/to/incremental_update.py
```

#### Option 2: Shell Script
```bash
#!/bin/bash
cd /path/to/dvdrental_live
python incremental_update.py 1
python maintain.py backup
```

Make executable and run on schedule:
```bash
chmod +x update_db.sh
```

---

## 📊 Export Data

### Export to CSV
```bash
# Export rentals to CSV
mysql -u root -p dvdrental_live -e "
  SELECT * FROM rental;" > rentals.csv

# Export with headers
mysql -u root -p dvdrental_live -e "
  SELECT * FROM rental \G" > rentals.csv
```

### Export Entire Database
```bash
mysqldump -u root -p dvdrental_live > full_backup.sql
```

### Export Specific Table
```bash
mysqldump -u root -p dvdrental_live rental > rental_table.sql
mysqldump -u root -p dvdrental_live payment > payment_table.sql
```

---

## 🔗 Connect External Tools

### Python Application
```python
import mysql.connector

config = {
  'host': 'localhost',
  'user': 'root',
  'password': 'root',
  'database': 'dvdrental_live'
}

conn = mysql.connector.connect(**config)
cursor = conn.cursor()
cursor.execute("SELECT * FROM rental LIMIT 5")
for row in cursor:
    print(row)
```

### Node.js Application
```javascript
const mysql = require('mysql2/promise');

async function query() {
  const conn = await mysql.createConnection({
    host: 'localhost',
    user: 'root',
    password: 'root',
    database: 'dvdrental_live'
  });
  
  const [rows] = await conn.execute('SELECT * FROM rental LIMIT 5');
  console.log(rows);
}
```

### Tableau/Power BI
1. Create new data source → MySQL
2. Server: `localhost`
3. User: `root`
4. Password: `root`
5. Database: `dvdrental_live`
6. Select tables to analyze

---

## 📚 Help & Documentation

```bash
# Quick start
cat README.md

# Complete setup guide
cat SETUP_GUIDE.md

# Command reference
cat QUICK_REFERENCE.md

# Implementation details
cat IMPLEMENTATION_SUMMARY.md

# View all available commands
python maintain.py        # Shows help
python generator.py       # Shows help
python incremental_update.py  # Shows help
```

---

## ✅ Checklist

- [ ] Installed MySQL
- [ ] Installed Python requirements: `pip install -r requirements.txt`
- [ ] Initialized database: `python generator.py`
- [ ] Verified setup: `python validate.py`
- [ ] Reviewed documentation: `cat README.md`
- [ ] Added more data: `python incremental_update.py`
- [ ] Explored analysis: `python maintain.py growth`
- [ ] Backed up database: `python maintain.py backup`

---

**For detailed information, see [QUICK_REFERENCE.md](QUICK_REFERENCE.md) or [SETUP_GUIDE.md](SETUP_GUIDE.md)**
