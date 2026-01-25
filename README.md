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

# Add 4 weeks with 50% seasonal increase (holiday season)
python incremental_update.py 4 --seasonal 50

# Add 4 weeks with 50% seasonal decrease (summer slump)
python incremental_update.py 4 --seasonal -50
```

#### Seasonal Drift Argument

The `--seasonal` argument lets you adjust transaction volume for seasonal effects:

```bash
python incremental_update.py <num_weeks> --seasonal <percent>
```

- `50` = 50% increase in transaction volume
- `-50` = 50% decrease in transaction volume
- `0` = no change (default)

**Example scenarios:**
- Holiday season: `--seasonal 75`
- Summer slump: `--seasonal -40`
- New marketing campaign: `--seasonal 25`
- Store closure: `--seasonal -90`

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

## Recent Changes

### Fixed: Database Connection Issue
- **Issue**: `incremental_update.py` would fail with "No database selected" error
- **Fix**: Updated `generator.py` `connect()` method to include `database` parameter in MySQL connection string
- **Impact**: `incremental_update.py` and `advanced_incremental_update.py` now work correctly
- **Files Modified**: `generator.py` (line ~33-45)

### New Feature: Seasonal Drift for Transaction Volume
- **Feature**: Add `--seasonal` argument to `incremental_update.py` to simulate seasonal demand changes
- **Usage**: `python incremental_update.py 4 --seasonal 50` for 50% increase
- **Examples**:
  - Holiday season: `--seasonal 75`
  - Summer slump: `--seasonal -40`
  - Store closure: `--seasonal -90`
- **How it works**: Multiplies expected transaction volume by (1 + seasonal_drift/100)
- **Files Modified**: 
  - `incremental_update.py` (main() and add_incremental_week() functions)
  - `generator.py` (DVDRentalDataGenerator class and add_week_of_transactions() method)

### Added: Advanced Tracking System
- **Location**: `/advanced_tracking/` subfolder
- **Features**: Late fee calculation, inventory status tracking, customer AR management
- **Components**: 7 files with 1,304 lines of code + 2,200+ lines of documentation
- **See**: [advanced_tracking/README.md](advanced_tracking/README.md) for details

## License

See LICENSE file for details
