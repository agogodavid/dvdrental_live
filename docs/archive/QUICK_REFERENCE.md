# DVD Rental Live - Quick Reference

## Files Created

### 📊 Core Files
| File | Purpose |
|------|---------|
| `schema.sql` | MySQL database schema (14 tables) |
| `generator.py` | Main program to initialize database and generate data |
| `incremental_update.py` | Add new weeks of transaction data |
| `config.json` | Configuration (MySQL credentials, business parameters) |

### 🛠️ Utilities
| File | Purpose |
|------|---------|
| `validate.py` | Verify database setup and show statistics |
| `maintain.py` | Database maintenance (optimize, backup, integrity) |
| `analysis_queries.sql` | 10 pre-built SQL analysis queries |

### 📚 Documentation
| File | Purpose |
|------|---------|
| `README.md` | Quick start guide |
| `SETUP_GUIDE.md` | Comprehensive setup instructions |
| `requirements.txt` | Python package dependencies |
| `setup.sh` | Automated setup script |

---

## Quick Start Commands

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Create Database & Initial Data
```bash
python generator.py
```
Creates database with 12 weeks of data (~6,000 transactions)

### 3. Verify Setup
```bash
python validate.py
```

### 4. Add More Data
```bash
# Add 1 week
python incremental_update.py

# Add 4 weeks
python incremental_update.py 4
```

### 5. Analyze Data
```bash
python maintain.py stats
python maintain.py growth
python maintain.py integrity
mysql -u root -p dvdrental_live < analysis_queries.sql
```

---

## Database Schema Overview

### Transaction Tables
- **rental** - DVD rentals (rental_date, return_date, customer_id, inventory_id)
- **payment** - Payments for rentals (amount, payment_date)
- **inventory** - DVD copies per store (film_id, store_id)

### Reference Tables
- **customer** - Customers (lifecycle tracking)
- **film** - Films with metadata
- **actor** - Actors
- **category** - Film categories
- **store** - Rental stores
- **staff** - Store employees

### Location Tables
- **country**, **city**, **address**

### Junction Tables
- **film_actor** - Many-to-many: Films ↔ Actors
- **film_category** - Many-to-many: Films ↔ Categories

---

## Business Logic Built In

### Transaction Patterns
- **Week 1-8:** Weekend-heavy (Fri 15%, Sat 20%, Sun 15%)
- **Week 8+:** Gradual shift to weekday-heavy over 16 weeks
- **Spikes:** 5% chance of 4x volume on any day

### Customer Lifecycle
- **Acquisition:** ~10 new customers/week
- **Churn:** 40% after 5 weeks
- **Loyal:** 15% stay throughout

### Growth
- **Base Volume:** 500 rentals/week
- **Growth Rate:** +2% per week
- **Rental Duration:** 3-7 days (weighted toward shorter)

---

## Maintenance Commands

```bash
# Show statistics
python maintain.py stats

# Optimize tables
python maintain.py optimize

# Check data integrity
python maintain.py integrity

# Create backup
python maintain.py backup

# Run all checks
python maintain.py full
```

---

## Analysis Queries Available

1. **Transaction Volume by Week/Day** - Patterns over time
2. **Customer Acquisition & Churn** - Customer lifecycle
3. **Revenue by Week** - Financial metrics
4. **Top Films** - Popularity analysis
5. **Customer Activity** - Active vs inactive
6. **Store Performance** - Compare stores
7. **Rental Duration Analysis** - How long rentals are kept
8. **Spike Day Detection** - Unusual high-volume days
9. **Customer Lifetime Value** - Top customers
10. **Weekly Transaction Trends** - Business pattern shifts

---

## Configuration

Edit `config.json` to customize:

```json
{
  "mysql": {
    "host": "localhost",
    "user": "root",
    "password": "root"
  },
  "generation": {
    "initial_weeks": 12,
    "weekly_new_customers": 10,
    "base_weekly_transactions": 500,
    "customer_churn_after_weeks": 5,
    "churn_rate": 0.4,
    "loyal_customer_rate": 0.15
  }
}
```

---

## Troubleshooting

### MySQL Not Running
```bash
sudo service mysql start          # Linux
brew services start mysql         # macOS
```

### Connection Error
- Check `config.json` credentials
- Verify MySQL root user exists
- Reset password: `sudo mysql -u root` then `ALTER USER 'root'@'localhost' IDENTIFIED BY 'root';`

### Database Already Exists
```bash
mysql -u root -p -e "DROP DATABASE dvdrental_live;"
python generator.py
```

### No Data Generated
```bash
python validate.py    # Check for errors
```

---

## Example Queries

### View Weekly Transactions
```sql
SELECT 
  WEEK(rental_date) as week,
  COUNT(*) as transactions
FROM rental
GROUP BY WEEK(rental_date)
ORDER BY week;
```

### Top 10 Customers by Rentals
```sql
SELECT 
  CONCAT(c.first_name, ' ', c.last_name) as customer,
  COUNT(r.rental_id) as rentals
FROM customer c
LEFT JOIN rental r ON c.customer_id = r.customer_id
GROUP BY c.customer_id
ORDER BY rentals DESC
LIMIT 10;
```

### Revenue Trend
```sql
SELECT 
  DATE(payment_date) as date,
  SUM(amount) as daily_revenue
FROM payment
GROUP BY DATE(payment_date)
ORDER BY date;
```

---

## Next Steps

1. ✅ Run `python generator.py` to initialize
2. ✅ Verify with `python validate.py`
3. ✅ Review `SETUP_GUIDE.md` for detailed information
4. ✅ Run analysis queries to understand patterns
5. ✅ Add new weeks regularly: `python incremental_update.py`
6. ✅ Connect BI tools (Tableau, Power BI, etc.)
7. ✅ Build dashboards on top of the data

---

## Support Files

- **README.md** - Quick reference
- **SETUP_GUIDE.md** - Complete installation guide
- **analysis_queries.sql** - 10 analysis examples
- **config.json** - All configuration options

For detailed setup instructions, see `SETUP_GUIDE.md`
