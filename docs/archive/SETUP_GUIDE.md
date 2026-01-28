# DVD Rental Live - Complete Setup Guide

## Overview

This is a comprehensive guide to set up and use the DVD Rental Live database system. The system generates realistic transaction data for a DVD rental business with authentic business patterns.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation Steps](#installation-steps)
3. [First Run](#first-run)
4. [Understanding the Data](#understanding-the-data)
5. [Advanced Usage](#advanced-usage)
6. [Troubleshooting](#troubleshooting)
7. [File Structure](#file-structure)

---

## Prerequisites

Before starting, ensure you have:

- **MySQL Server** (8.0 or higher)
- **Python** (3.7 or higher)
- **pip** (Python package manager)
- At least 1GB free disk space
- Terminal/Command line access

### Verify Prerequisites

```bash
# Check MySQL
mysql --version

# Check Python
python --version
python -m pip --version
```

---

## Installation Steps

### Step 1: Install MySQL Server

#### On Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install -y mysql-server
sudo service mysql start

# Verify it's running
sudo service mysql status
```

#### On macOS
```bash
brew install mysql
brew services start mysql
```

#### On Windows
1. Download from https://dev.mysql.com/downloads/mysql/
2. Run the installer and follow prompts
3. MySQL service will start automatically

### Step 2: Configure MySQL Root User

```bash
# Set/change root password
mysql -u root -e "ALTER USER 'root'@'localhost' IDENTIFIED BY 'root';"

# Verify connection
mysql -u root -p
# Enter password: root
# Type: exit
```

If you use a different password, update `config.json` accordingly.

### Step 3: Clone/Download Project

```bash
cd /path/to/your/projects
git clone <repository-url>
cd dvdrental_live
```

### Step 4: Install Python Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `mysql-connector-python` - MySQL database driver
- `python-dateutil` - Date utilities

### Step 5: Verify Setup

```bash
python validate.py
```

Expected output:
```
✓ Configuration loaded from config.json
✓ MySQL connection successful
✓ Database 'dvdrental_live' does not exist
```

This is normal if it's the first time running.

---

## First Run

### Initialize the Database

Run this command to create the database and populate with initial data:

```bash
python generator.py
```

This will:
1. Create the MySQL database `dvdrental_live`
2. Create all 14 tables with proper schema
3. Seed reference data:
   - 8 countries
   - 10 cities
   - 100 actors
   - 5 languages
   - 8 film categories
   - 100 films (each assigned to 3-8 actors and 1-3 categories)
4. Create 2 stores with managers
5. Generate 12 weeks of transaction data (6000+ transactions)

**Duration:** 30-60 seconds

**Output:**
```
2026-01-25 10:30:15 - INFO - Connected to MySQL successfully
2026-01-25 10:30:15 - INFO - Database dvdrental_live created successfully
2026-01-25 10:30:16 - INFO - Schema created successfully
...
2026-01-25 10:30:45 - INFO - Database initialized and seeded successfully!
```

### Verify Success

```bash
python validate.py
```

Expected output now shows database statistics:
```
✓ All 14 required tables exist

Database Statistics:
  country: 8 records
  city: 10 records
  actor: 100 records
  film: 100 records
  ...
  rental: 6,247 records
  payment: 5,682 records

✓ Setup is complete and database is populated!
```

---

## Understanding the Data

### Data Structure

The database follows a star schema pattern:

```
                    DIMENSIONAL TABLES
                    
    country ─── city ─── address
    language            actor ─── film ─── category
                                   │
    FACT TABLES ──────────────────┘
    
    store ─── staff
    customer (linked to store)
    
    rental (main transaction)
    ├─ inventory (from store)
    ├─ customer
    ├─ staff
    └─ return_date
    
    payment (from rental)
```

### Key Tables

#### Core Transaction Tables
- **rental** - DVD rental events with dates
- **payment** - Payment records for rentals
- **inventory** - Physical DVD copies per store

#### Customer Tables
- **customer** - Customer information with lifecycle tracking
- **store** - Rental stores

#### Content Tables
- **film** - Films with metadata (rating, duration, rental rate)
- **actor** - Actors in films
- **category** - Film categories

#### Reference Tables
- **country**, **city**, **address** - Location hierarchy
- **language** - Languages for films
- **staff** - Store employees

### Sample Data Characteristics

**Week 1 Data:**
- Rentals: ~500
- New customers: 10
- Weekend bias: 50% of transactions
- Rental duration: 3-7 days average
- Return date: Biased toward early week

**Week 12 Data:**
- Rentals: ~620 (2% weekly growth)
- Customer churn: Starting to be visible
- Transaction pattern: Still weekend-heavy, beginning shift
- Same rental behavior

---

## Advanced Usage

### Adding New Weeks of Data

Add a single week:
```bash
python incremental_update.py
```

Add multiple weeks:
```bash
python incremental_update.py 4
```

This adds 4 weeks while:
- Adding ~10 new customers per week
- Maintaining realistic churn (40% after 5 weeks)
- Growing transaction volume by 2% per week
- Tracking customer lifecycle

### Analyzing the Data

Use the analysis queries to understand trends:

```bash
# View all analysis queries
cat analysis_queries.sql

# Run a specific analysis
mysql -u root -p dvdrental_live < analysis_queries.sql
```

Key analyses available:
1. **Transaction Volume by Week and Day** - See how patterns shift
2. **Customer Acquisition and Churn** - Understand customer lifecycle
3. **Revenue by Week** - Track financial growth
4. **Top Films by Rentals** - Which films are popular
5. **Store Performance** - Compare stores
6. **Rental Duration Analysis** - How long do customers keep films
7. **Spike Day Detection** - Find unusual high-volume days
8. **Customer Lifetime Value** - Identify valuable customers

### Custom Queries

Connect to the database and run SQL queries:

```bash
mysql -u root -p dvdrental_live

# Example queries
SELECT 
  WEEK(rental_date) as week,
  COUNT(*) as rentals,
  SUM(p.amount) as revenue
FROM rental r
LEFT JOIN payment p ON r.rental_id = p.rental_id
GROUP BY WEEK(rental_date)
ORDER BY week;
```

### Export Data

Export entire database:
```bash
mysqldump -u root -p dvdrental_live > backup_$(date +%Y%m%d).sql
```

Export specific table:
```bash
mysqldump -u root -p dvdrental_live rental > rental_backup.sql
```

### Connect from Applications

**Python:**
```python
import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='root',
    database='dvdrental_live'
)
cursor = conn.cursor()
cursor.execute("SELECT * FROM rental LIMIT 5")
for row in cursor:
    print(row)
```

**Node.js:**
```javascript
const mysql = require('mysql2/promise');

const conn = await mysql.createConnection({
    host: 'localhost',
    user: 'root',
    password: 'root',
    database: 'dvdrental_live'
});

const [rows] = await conn.execute('SELECT * FROM rental LIMIT 5');
console.log(rows);
```

---

## Troubleshooting

### MySQL Connection Issues

**Error:** `Can't connect to MySQL server on 'localhost'`

**Solutions:**
1. Verify MySQL is running:
   ```bash
   # Ubuntu/Linux
   sudo service mysql status
   
   # macOS
   brew services list
   ```

2. Start MySQL if stopped:
   ```bash
   # Ubuntu/Linux
   sudo service mysql start
   
   # macOS
   brew services start mysql
   ```

3. Check credentials in `config.json`

### Python Connection Issues

**Error:** `mysql.connector.errors.ProgrammingError: 1045 (28000): Access denied`

**Solutions:**
1. Verify username and password in `config.json`
2. Reset MySQL root password:
   ```bash
   sudo mysql -u root
   ALTER USER 'root'@'localhost' IDENTIFIED BY 'root';
   FLUSH PRIVILEGES;
   exit;
   ```

### Database Already Exists

**Error:** `Database dvdrental_live already exists`

**Solutions:**
1. Drop existing database:
   ```bash
   mysql -u root -p -e "DROP DATABASE dvdrental_live;"
   ```
   Then run `python generator.py` again

2. Or, keep existing data and add new weeks:
   ```bash
   python incremental_update.py
   ```

### No Data Generated

**Problem:** Database created but no transactions

**Causes:**
1. Generator crashed silently - check MySQL connection
2. Incorrect credentials - verify `config.json`
3. MySQL service stopped - restart it

**Solution:**
```bash
python validate.py
# Check for errors in output
```

### Performance Issues

**Problem:** Generator running slowly

**Solutions:**
1. Increase MySQL buffer pool:
   ```sql
   SET GLOBAL innodb_buffer_pool_size = 2147483648;
   ```

2. Disable foreign key checks during generation (if safe):
   ```sql
   SET FOREIGN_KEY_CHECKS = 0;
   ```

---

## File Structure

```
dvdrental_live/
├── schema.sql                 # Database schema creation script
├── generator.py               # Main data generation program
├── incremental_update.py      # Add new weeks of data
├── validate.py                # Verify setup
├── config.json                # Configuration file
├── requirements.txt           # Python dependencies
├── analysis_queries.sql       # SQL analysis queries
├── setup.sh                   # Quick setup script
├── README.md                  # Quick reference
└── SETUP_GUIDE.md            # This file
```

### Key Files Explained

**schema.sql** - Defines all 14 tables with:
- Primary keys and constraints
- Foreign key relationships
- Indexes for performance
- Data types and defaults

**generator.py** - Main program with classes for:
- Database connection management
- Schema creation
- Seed data generation
- Transaction generation with business logic
- Customer lifecycle management

**incremental_update.py** - Adds new weeks of data while:
- Maintaining customer churn patterns
- Growing transaction volume
- Tracking business metrics

**config.json** - Centralizes all configuration:
- MySQL connection details
- Business parameters (churn rates, volumes)
- Generation settings

---

## Next Steps

1. ✅ Install MySQL and Python
2. ✅ Run `python generator.py` for initial setup
3. ✅ Verify with `python validate.py`
4. Run analysis queries: `mysql -u root -p dvdrental_live < analysis_queries.sql`
5. Set up a cron job to add new weeks automatically:
   ```bash
   # Add to crontab (runs every week at 2 AM)
   0 2 * * MON python /path/to/dvdrental_live/incremental_update.py
   ```
6. Connect your BI tools (Tableau, Power BI, etc.) to the database
7. Build dashboards and analytics on top of the data

---

## Support

For issues:
1. Check [Troubleshooting](#troubleshooting) section
2. Verify all files exist: `ls -la`
3. Run validate script: `python validate.py`
4. Check MySQL logs: `grep error /var/log/mysql/error.log` (Ubuntu)

---

## License

See LICENSE file for details.

Happy analyzing! 📊
