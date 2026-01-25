# DVD Rental Live Database

A realistic DVD rental transaction database that grows over time with business logic for customer lifecycle, transaction patterns, and operational trends.

## Features

- **MySQL database** with complete DVD rental schema
- **Realistic transaction patterns**:
  - Initial bias toward weekend transactions, shifting to weekdays over time
  - ~10 new customers added weekly
  - ~40% customer churn after 5 weeks, ~15% loyal customers
  - ~500 transactions/week base volume with 2% growth per week
  - Random spike days (4x transaction volume)
  - Rental durations 3-7 days with returns biased toward early week
  
- **Incremental data generation**: Add weeks of data one at a time
- **Configurable parameters** via `config.json`

## Prerequisites

- MySQL Server (8.0+)
- Python 3.7+
- pip

## Installation

### 1. Install MySQL (if not already installed)

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y mysql-server
sudo service mysql start
```

**macOS:**
```bash
brew install mysql
brew services start mysql
```

### 2. Configure MySQL

Set a root password (replace 'root' with your desired password):
```bash
mysql -u root -e "ALTER USER 'root'@'localhost' IDENTIFIED BY 'root';"
```

Or update `config.json` with your MySQL credentials.

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

## Quick Start

### Initialize Database

```bash
python generator.py
```

This will:
1. Create the `dvdrental_live` database
2. Create all tables with proper schema
3. Seed reference data (countries, cities, languages, categories, actors, films)
4. Create 2 stores with staff
5. Generate initial 12 weeks of transaction data

### Add More Weeks

```bash
# Add 1 week
python incremental_update.py

# Add 4 weeks
python incremental_update.py 4
```

## Database Schema

### Reference Tables
- **country** - Countries
- **city** - Cities with country relationship
- **address** - Physical addresses
- **language** - Film languages
- **category** - Film categories
- **actor** - Actors
- **film** - Films with metadata
- **film_actor** - Many-to-many: Films and Actors
- **film_category** - Many-to-many: Films and Categories

### Operational Tables
- **store** - Rental stores
- **staff** - Store employees
- **customer** - Customers with lifecycle tracking
- **inventory** - Film copies per store
- **rental** - Rental transactions
- **payment** - Payments for rentals

## Configuration

Edit `config.json` to customize:

```json
{
  "mysql": {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "dvdrental_live"
  },
  "generation": {
    "initial_weeks": 12,
    "weekly_new_customers": 10,
    "base_weekly_transactions": 500,
    "customer_churn_after_weeks": 5,
    "churn_rate": 0.4,
    "loyal_customer_rate": 0.15,
    "spike_day_probability": 0.05,
    "spike_day_multiplier": 4
  }
}
```

## Business Logic

### Transaction Patterns

**Week 1-8 (Initial Phase):**
- Weekend-heavy: Friday 15%, Saturday 20%, Sunday 15%
- Weekdays: Monday-Thursday 10% each

**Week 8+ (Transition Phase):**
- Gradual shift to weekday-heavy over 16 weeks
- After week 24: Mostly weekday transactions

### Customer Lifecycle

- **Acquisition**: ~10 new customers per week
- **Retention**: After 5 weeks, 40% churn out
- **Loyal**: 15% of customers are loyal throughout
- **Growth**: Transaction volume grows 2% per week

### Transaction Volume

- **Base**: 500 transactions/week
- **Growth**: +2% per week
- **Spikes**: 5% chance of 4x volume on any day

### Rental Behavior

- **Duration**: Random 3-7 days (bias toward shorter)
- **Returns**: 70% return within rental period, 30% extended
- **Early Week Returns**: Returns biased toward Monday-Wednesday

## Usage Examples

### Check Database Status

```bash
mysql -u root -p dvdrental_live -e "
SELECT 'Customers' as entity, COUNT(*) as count FROM customer
UNION ALL
SELECT 'Films', COUNT(*) FROM film
UNION ALL
SELECT 'Rentals', COUNT(*) FROM rental
UNION ALL
SELECT 'Payments', COUNT(*) FROM payment;
"
```

### View Transaction Trends

```bash
mysql -u root -p dvdrental_live -e "
SELECT 
  WEEK(rental_date) as week,
  DAYNAME(rental_date) as day,
  COUNT(*) as transactions
FROM rental
GROUP BY WEEK(rental_date), DAYNAME(rental_date)
ORDER BY week, FIELD(day, 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday');
"
```

### Export Data

```bash
mysqldump -u root -p dvdrental_live > backup.sql
```

## Troubleshooting

### Connection Error
```
Error connecting to MySQL
```
- Ensure MySQL is running: `sudo service mysql start`
- Verify credentials in `config.json`
- Check MySQL user exists and has permissions

### Database Already Exists
```
Database {db_name} already exists
```
- The script will drop and recreate the database
- Or manually drop: `mysql -u root -p -e "DROP DATABASE dvdrental_live;"`

### No Active Customers
```
No active customers in week
```
- This is normal early on, or if churn is very high
- The system tracks customer lifecycle automatically

## Performance Tips

- Add indexes as needed for large datasets
- Consider partitioning by date for very large datasets (2+ years)
- Monitor disk space for transaction volume growth

## Next Steps

1. Connect to the database in your application
2. Run `incremental_update.py` weekly to keep data fresh
3. Monitor transaction patterns in your analytics
4. Adjust `config.json` parameters based on your needs

## License

See LICENSE file for details
