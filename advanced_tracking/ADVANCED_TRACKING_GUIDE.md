# Advanced Incremental Update - Usage Guide

## Overview

`advanced_incremental_update.py` is an **independent tracking system** that extends the DVD rental database with:

- **Late Fee Calculations** - Automatically compute overdue charges ($1.50/day)
- **Inventory Status Tracking** - Real-time availability monitoring (available/rented/damaged/missing)
- **Customer AR (Accounts Receivable)** - Track outstanding balances and payment obligations
- **Rental Status Views** - Easy queries for active/overdue/completed rentals
- **Audit Trails** - Complete history of inventory status changes

**Key Principle:** This system runs **independently** alongside your main `generator.py` and `incremental_update.py` without modifying existing logic.

---

## Installation & Setup

### 1. Install Dependencies

```bash
pip install mysql-connector-python
```

### 2. Initialize Tracking Tables (First Run)

```bash
python advanced_incremental_update.py --init
```

**What it does:**
- ✅ Adds `status` column to inventory table (if not exists)
- ✅ Creates `inventory_audit` table
- ✅ Creates `v_rental_status` view
- ✅ Creates `late_fees` table
- ✅ Creates `customer_account` table
- ✅ Calculates initial late fees for all overdue rentals

**This is idempotent** - safe to run multiple times without duplication.

---

## Usage Modes

### Mode 1: Update Tracking Data + Generate Reports

```bash
python advanced_incremental_update.py --update
```

Runs:
1. Updates inventory status (rented/available/damaged)
2. Recalculates late fees for all overdue rentals
3. Reconciles customer account balances
4. Generates late fee report (top 20 overdue)
5. Generates AR report (customers with outstanding balance)

### Mode 2: Daily Reconciliation

```bash
python advanced_incremental_update.py --daily
```

Same as `--update` - designed to be scheduled as a daily cron job:

```bash
# Add to crontab for daily 2 AM reconciliation
0 2 * * * /usr/bin/python3 /path/to/advanced_incremental_update.py --daily
```

### Mode 3: Initialize Only

```bash
python advanced_incremental_update.py --init
```

Just creates tables without calculating late fees. Use if you want to defer calculations.

### Mode 4: Default (Init + Update)

```bash
python advanced_incremental_update.py
```

Initializes tables AND updates tracking data in one command.

---

## Configuration

Configuration is read from `config.json`:

```json
{
  "mysql": {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "dvdrental_live"
  },
  "simulation": {
    "start_date": "2025-12-30",
    "initial_weeks": 12
  }
}
```

### Customizing Late Fee Rate

To change late fee calculation (default $1.50/day):

```bash
# Edit advanced_incremental_update.py, line ~23
LATE_FEE_RATE_PER_DAY = 2.00  # Change to your rate
```

---

## Database Schema Changes

### Tables Created

#### 1. **late_fees** Table
Tracks late fee calculations for each unreturned rental:

```sql
CREATE TABLE late_fees (
  late_fee_id INT AUTO_INCREMENT PRIMARY KEY,
  rental_id INT NOT NULL UNIQUE,
  customer_id INT NOT NULL,
  days_overdue INT DEFAULT 0,
  fee_amount DECIMAL(10,2) DEFAULT 0.00,
  fee_paid DECIMAL(10,2) DEFAULT 0.00,
  fee_status ENUM('pending', 'partially_paid', 'paid', 'written_off') DEFAULT 'pending',
  FOREIGN KEY (rental_id) REFERENCES rental(rental_id),
  FOREIGN KEY (customer_id) REFERENCES customer(customer_id)
);
```

#### 2. **customer_account** Table
AR tracking by customer:

```sql
CREATE TABLE customer_account (
  account_id INT AUTO_INCREMENT PRIMARY KEY,
  customer_id INT NOT NULL UNIQUE,
  balance DECIMAL(10,2) DEFAULT 0.00,
  total_rentals INT DEFAULT 0,
  unreturned_rentals INT DEFAULT 0,
  overdue_rentals INT DEFAULT 0,
  total_late_fees DECIMAL(10,2) DEFAULT 0.00,
  paid_late_fees DECIMAL(10,2) DEFAULT 0.00,
  status ENUM('good_standing', 'past_due', 'at_risk', 'suspended', 'closed') DEFAULT 'good_standing',
  FOREIGN KEY (customer_id) REFERENCES customer(customer_id)
);
```

#### 3. **inventory_audit** Table
Audit trail for inventory status changes:

```sql
CREATE TABLE inventory_audit (
  audit_id INT AUTO_INCREMENT PRIMARY KEY,
  inventory_id INT NOT NULL,
  status_from VARCHAR(20),
  status_to VARCHAR(20),
  audit_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  notes TEXT,
  FOREIGN KEY (inventory_id) REFERENCES inventory(inventory_id)
);
```

### Column Added to Existing Table

#### inventory.status
Tracks current inventory state (added via ALTER TABLE):

```sql
ALTER TABLE inventory 
ADD COLUMN status ENUM('available', 'rented', 'damaged', 'missing') 
DEFAULT 'available';
```

### Views Created

#### v_rental_status View
Easy querying of rental status with calculated fields:

```sql
SELECT 
  r.rental_id,
  r.customer_id,
  c.first_name,
  c.last_name,
  f.title,
  r.rental_date,
  f.rental_duration,
  DATE_ADD(r.rental_date, INTERVAL f.rental_duration DAY) as due_date,
  r.return_date,
  CASE 
    WHEN r.return_date IS NOT NULL THEN 'completed'
    WHEN DATEDIFF(NOW(), DATE_ADD(r.rental_date, INTERVAL f.rental_duration DAY)) > 0 THEN 'overdue'
    WHEN r.return_date IS NULL THEN 'active'
  END as status,
  DATEDIFF(NOW(), DATE_ADD(r.rental_date, INTERVAL f.rental_duration DAY)) as days_overdue
FROM rental r
JOIN customer c ON r.customer_id = c.customer_id
JOIN inventory i ON r.inventory_id = i.inventory_id
JOIN film f ON i.film_id = f.film_id;
```

---

## Useful Queries

### Find All Overdue Rentals

```sql
SELECT 
  c.first_name,
  c.last_name,
  f.title,
  vrs.days_overdue,
  lf.fee_amount
FROM v_rental_status vrs
JOIN customer c ON vrs.customer_id = c.customer_id
JOIN film f ON vrs.film_id = f.film_id
LEFT JOIN late_fees lf ON vrs.rental_id = lf.rental_id
WHERE vrs.status = 'overdue'
ORDER BY vrs.days_overdue DESC;
```

### Calculate Total AR by Customer

```sql
SELECT 
  c.first_name,
  c.last_name,
  ca.balance,
  ca.unreturned_rentals,
  ca.overdue_rentals,
  ca.status
FROM customer_account ca
JOIN customer c ON ca.customer_id = c.customer_id
WHERE ca.balance > 0
ORDER BY ca.balance DESC;
```

### Get Inventory Status Summary

```sql
SELECT 
  status,
  COUNT(*) as count,
  ROUND(COUNT(*) / (SELECT COUNT(*) FROM inventory) * 100, 1) as percentage
FROM inventory
GROUP BY status;
```

### Find High-Risk Customers (Overdue > 3 Items)

```sql
SELECT 
  c.first_name,
  c.last_name,
  ca.overdue_rentals,
  ca.balance,
  ca.status
FROM customer_account ca
JOIN customer c ON ca.customer_id = c.customer_id
WHERE ca.overdue_rentals > 3
ORDER BY ca.overdue_rentals DESC;
```

### Generate Late Fee Revenue Report

```sql
SELECT 
  DATE_FORMAT(lf.calculated_date, '%Y-%m') as month,
  COUNT(*) as fee_count,
  SUM(lf.fee_amount) as total_fees,
  SUM(lf.fee_paid) as fees_collected,
  SUM(lf.fee_amount) - SUM(lf.fee_paid) as uncollected
FROM late_fees lf
GROUP BY DATE_FORMAT(lf.calculated_date, '%Y-%m')
ORDER BY month DESC;
```

### Track Inventory Shrinkage

```sql
SELECT 
  status,
  COUNT(*) as count
FROM inventory
WHERE status IN ('damaged', 'missing')
GROUP BY status;
```

---

## Output Examples

### Late Fee Report Sample

```
📋 Late Fee Report

Customer             Film                 Days   Amount   Status
───────────────────────────────────────────────────────────────────
John Doe             The Dark Knight      7      $10.50   pending
Jane Smith           Inception            14     $21.00   pending
Bob Johnson          Interstellar         5      $7.50    pending
Alice Brown          Avatar               18     $27.00   pending
───────────────────────────────────────────────────────────────────
TOTAL PENDING FEES:                              $75.00
```

### Customer AR Report Sample

```
👥 Customer Accounts Receivable Report

Customer             Rentals  Unreturned  Balance    Status
────────────────────────────────────────────────────────────
Alice Brown          8        3           $52.50     past_due
Jane Smith           5        1           $45.00     past_due
John Doe             12       2           $30.00     at_risk
────────────────────────────────────────────────────────────
TOTAL AR:                                 $127.50
```

---

## Data Quality Checks

Run these queries to validate data integrity:

### Check for Orphaned Late Fees

```sql
-- Should return 0 rows
SELECT COUNT(*) FROM late_fees lf
WHERE lf.rental_id NOT IN (SELECT rental_id FROM rental);
```

### Verify Inventory Status Consistency

```sql
-- Check that 'rented' items match unreturned rentals
SELECT 
  i.inventory_id,
  i.status,
  COUNT(r.rental_id) as unreturned_count
FROM inventory i
LEFT JOIN rental r ON i.inventory_id = r.inventory_id AND r.return_date IS NULL
GROUP BY i.inventory_id, i.status
HAVING (i.status = 'rented' AND unreturned_count = 0)
   OR (i.status = 'available' AND unreturned_count > 0);
```

### Validate Late Fees Accuracy

```sql
-- Check that late fees only exist for unreturned rentals
SELECT COUNT(*) as inconsistencies
FROM late_fees lf
JOIN rental r ON lf.rental_id = r.rental_id
WHERE r.return_date IS NOT NULL;
```

---

## Troubleshooting

### Script Errors

**Error:** `Can't connect to MySQL server`
- **Solution:** Ensure MySQL is running and config.json has correct credentials

**Error:** `Table already exists`
- **Solution:** This is normal. The script uses `CREATE TABLE IF NOT EXISTS`. If it exists, it skips creation.

**Error:** `Duplicate entry for rental_id`
- **Solution:** Late fees use `ON DUPLICATE KEY UPDATE` to recalculate. This is expected behavior - just means fees are being updated.

### Data Issues

**Problem:** Late fees showing for returned rentals
- **Root Cause:** Script ran before rental was updated with return_date
- **Fix:** Run script again after data is fully reconciled

**Problem:** Inventory status not updating
- **Root Cause:** Rental table may not have been updated yet
- **Fix:** Ensure new rentals are fully inserted before running update

---

## Integration with Main System

### Workflow

```
1. generator.py creates initial data
   ↓
2. incremental_update.py adds new weeks
   ↓
3. advanced_incremental_update.py calculates tracking
   ↓
4. Analysts run queries to monitor AR & fees
```

### Coordination

- **Main generators** create rental/inventory changes
- **Advanced tracker** reads those changes and calculates metrics
- **No conflicts** - advanced tracker only writes to its own tables
- **Idempotent** - safe to run multiple times

### Scheduling Recommendations

```bash
# Immediate use (manual)
python advanced_incremental_update.py --update

# Scheduled daily reconciliation (add to crontab)
0 2 * * * cd /path/to/dvdrental_live && python advanced_incremental_update.py --daily

# Weekly comprehensive audit
0 3 * * 0 cd /path/to/dvdrental_live && python advanced_incremental_update.py --init
```

---

## Performance Considerations

### Query Performance

For large datasets (100k+ rentals), add indexes:

```sql
-- Already created by schema, but verify:
CREATE INDEX idx_late_fees_status ON late_fees(fee_status);
CREATE INDEX idx_rental_status_due ON v_rental_status(due_date);
CREATE INDEX idx_customer_ar_balance ON customer_account(balance);
```

### Update Duration

Expected runtime by dataset size:

| Rentals | Time    |
|---------|---------|
| 1,000   | < 1 sec |
| 10,000  | 2-3 sec |
| 100,000 | 15-20 sec |
| 1M+     | 1-2 min |

Optimize with:
```bash
# Run with production MySQL settings
mysql_config_editor set --login-path=production --user=root --password
python advanced_incremental_update.py --config config_prod.json
```

---

## Demo & Testing

Run the demo without a live database:

```bash
python advanced_incremental_update_demo.py
```

This shows the complete workflow with mock data.

---

## Support & Documentation

- **Main Documentation:** [DATA_QUALITY_NOTES.md](DATA_QUALITY_NOTES.md)
- **Code Comments:** See `advanced_incremental_update.py` for detailed method documentation
- **Examples:** Check `analysis_queries.sql` for additional query patterns
