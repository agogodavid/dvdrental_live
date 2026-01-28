# DVD Rental Live - Data Quality & Discrepancies Report

## Current Implementation ✅

### Unreturned Rentals
**Status:** Working as designed
- 30% of rentals intentionally left with `NULL` return_date
- Simulates movies still checked out by customers
- Perfect for analyzing outstanding rentals

### Query Examples for Unreturned Movies

```sql
-- Find all unreturned rentals
SELECT 
  r.rental_id,
  c.first_name,
  c.last_name,
  f.title,
  r.rental_date,
  DATEDIFF(NOW(), r.rental_date) as days_out
FROM rental r
JOIN customer c ON r.customer_id = c.customer_id
JOIN inventory i ON r.inventory_id = i.inventory_id
JOIN film f ON i.film_id = f.film_id
WHERE r.return_date IS NULL
ORDER BY r.rental_date ASC;

-- Count unreturned rentals by film
SELECT 
  f.title,
  COUNT(*) as unreturned_count
FROM rental r
JOIN inventory i ON r.inventory_id = i.inventory_id
JOIN film f ON i.film_id = f.film_id
WHERE r.return_date IS NULL
GROUP BY f.film_id, f.title
ORDER BY unreturned_count DESC;

-- Find overdue rentals (out > 7 days)
SELECT 
  r.rental_id,
  c.first_name,
  c.last_name,
  f.title,
  r.rental_date,
  DATEDIFF(NOW(), r.rental_date) as days_overdue,
  (DATEDIFF(NOW(), r.rental_date) - 7) * f.rental_rate as potential_late_fee
FROM rental r
JOIN customer c ON r.customer_id = c.customer_id
JOIN inventory i ON r.inventory_id = i.inventory_id
JOIN film f ON i.film_id = f.film_id
WHERE r.return_date IS NULL
  AND DATEDIFF(NOW(), r.rental_date) > 7
ORDER BY days_overdue DESC;
```

---

## ⚠️ Identified Discrepancies for Analyst Resolution

### 1. **CRITICAL: Inventory Status Not Tracked**

**Issue:** 
- Inventory table has no `status` column (e.g., 'available', 'rented', 'damaged', 'missing')
- Cannot determine actual availability from unreturned rentals
- No way to flag items as missing or needing maintenance

**Impact:**
- Overbooking possible (system thinks items available when they're rented)
- No damage/loss tracking
- Inventory audits impossible

**Analyst Action Required:**
```sql
-- Current problem: Can't tell if inventory is available
SELECT COUNT(*) as total_copies FROM inventory WHERE film_id = 1;
-- Returns 5, but 2 are checked out - which 2?

-- Need to add status tracking
ALTER TABLE inventory ADD COLUMN status ENUM('available', 'rented', 'damaged', 'missing') DEFAULT 'available';

-- Then update based on rentals
UPDATE inventory i 
SET status = 'rented'
WHERE inventory_id IN (
  SELECT DISTINCT inventory_id FROM rental 
  WHERE return_date IS NULL
);
```

---

### 2. **CRITICAL: Missing Payment for Unreturned Rentals**

**Issue:**
- Payments only generated for returned rentals (`WHERE return_date IS NOT NULL`)
- Unreturned rentals have no payment records
- No outstanding AR (Accounts Receivable) tracking
- 30% of revenue potentially not recorded

**Impact:**
- Revenue underreported
- No tracking of customer payment obligations
- Accounts receivable invisible in reports

**Analyst Action Required:**
```sql
-- Find unreturned rentals with missing payments
SELECT 
  r.rental_id,
  c.first_name,
  c.last_name,
  f.title,
  f.rental_rate,
  r.rental_date,
  'NO PAYMENT RECORDED' as status
FROM rental r
JOIN customer c ON r.customer_id = c.customer_id
JOIN inventory i ON r.inventory_id = i.inventory_id
JOIN film f ON i.film_id = f.film_id
LEFT JOIN payment p ON r.rental_id = p.rental_id
WHERE r.return_date IS NULL
  AND p.payment_id IS NULL;

-- Calculate potential outstanding revenue
SELECT 
  SUM(f.rental_rate) as total_outstanding_revenue,
  COUNT(DISTINCT r.customer_id) as customers_owing,
  COUNT(*) as unreturned_rentals
FROM rental r
JOIN inventory i ON r.inventory_id = i.inventory_id
JOIN film f ON i.film_id = f.film_id
LEFT JOIN payment p ON r.rental_id = p.rental_id
WHERE r.return_date IS NULL
  AND p.payment_id IS NULL;
```

---

### 3. **HIGH: No Late Fee Tracking**

**Issue:**
- Rental table has no due_date or expected_return_date
- Cannot calculate late fees
- No overdue tracking mechanism
- Business logic for penalties missing

**Impact:**
- No late fee revenue captured
- Cannot identify problem customers
- No incentive model for timely returns

**Analyst Action Required:**
```sql
-- Calculate what late fees should have been
SELECT 
  r.rental_id,
  c.first_name,
  c.last_name,
  r.rental_date,
  DATE_ADD(r.rental_date, INTERVAL f.rental_duration DAY) as expected_return_date,
  DATEDIFF(NOW(), DATE_ADD(r.rental_date, INTERVAL f.rental_duration DAY)) as days_late,
  CASE 
    WHEN DATEDIFF(NOW(), DATE_ADD(r.rental_date, INTERVAL f.rental_duration DAY)) > 0
    THEN DATEDIFF(NOW(), DATE_ADD(r.rental_date, INTERVAL f.rental_duration DAY)) * 1.50
    ELSE 0
  END as calculated_late_fee
FROM rental r
JOIN inventory i ON r.inventory_id = i.inventory_id
JOIN film f ON i.film_id = f.film_id
JOIN customer c ON r.customer_id = c.customer_id
WHERE r.return_date IS NULL
  AND DATEDIFF(NOW(), DATE_ADD(r.rental_date, INTERVAL f.rental_duration DAY)) > 0;
```

**Recommendation:** Add to rental table:
```sql
ALTER TABLE rental ADD COLUMN due_date DATE GENERATED ALWAYS AS 
  (DATE_ADD(rental_date, INTERVAL (SELECT rental_duration FROM film WHERE film_id = (
    SELECT film_id FROM inventory WHERE inventory_id = rental.inventory_id
  )) DAY))
STORED;
```

---

### 4. **MEDIUM: No Rental Status Column**

**Issue:**
- Cannot distinguish between:
  - Rentals in progress (checked out, expected back)
  - Rentals overdue (not returned by due date)
  - Rentals completed (returned)
  - Rentals cancelled/lost

**Impact:**
- Reporting is confusing
- Cannot run "current active rentals" queries easily
- Business metrics hard to extract

**Analyst Action Required:**
```sql
-- Add rental status
ALTER TABLE rental ADD COLUMN status ENUM('active', 'overdue', 'completed', 'lost') 
  GENERATED ALWAYS AS (
    CASE 
      WHEN return_date IS NOT NULL THEN 'completed'
      WHEN return_date IS NULL AND DATEDIFF(NOW(), DATE_ADD(rental_date, INTERVAL 7 DAY)) > 0 THEN 'overdue'
      WHEN return_date IS NULL THEN 'active'
      ELSE 'unknown'
    END
  ) STORED;

-- Then use in queries
SELECT status, COUNT(*) FROM rental GROUP BY status;
```

---

### 5. **MEDIUM: Inventory Audit Trail Missing**

**Issue:**
- No way to track inventory history
- Cannot see when items became 'missing'
- No audit of physical vs. system counts
- Cannot identify systematic loss

**Impact:**
- Shrinkage invisible
- Cannot reconcile physical count to database
- Loss trends not detectable

**Analyst Action Required:**
```sql
-- Create inventory audit trail
CREATE TABLE inventory_audit (
  audit_id INT AUTO_INCREMENT PRIMARY KEY,
  inventory_id INT NOT NULL,
  status_from VARCHAR(20),
  status_to VARCHAR(20),
  audit_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  notes TEXT,
  FOREIGN KEY (inventory_id) REFERENCES inventory(inventory_id)
);

-- Query for shrinkage
SELECT 
  f.title,
  COUNT(*) as items_missing
FROM inventory i
JOIN film f ON i.film_id = f.film_id
WHERE status = 'missing'
GROUP BY f.film_id, f.title
ORDER BY items_missing DESC;
```

---

### 6. **MEDIUM: Customer Credit Balance Not Tracked**

**Issue:**
- No way to see customer account balance
- Unpaid rentals not isolated
- Cannot identify customers in arrears

**Impact:**
- Collections impossible
- Customer creditworthiness unknown
- AR aging impossible

**Analyst Action Required:**
```sql
-- Calculate customer balances (what they owe)
SELECT 
  c.customer_id,
  CONCAT(c.first_name, ' ', c.last_name) as customer_name,
  COUNT(r.rental_id) as active_rentals,
  SUM(f.rental_rate) as amount_owing,
  MAX(r.rental_date) as oldest_rental_date
FROM customer c
JOIN rental r ON c.customer_id = r.customer_id
JOIN inventory i ON r.inventory_id = i.inventory_id
JOIN film f ON i.film_id = f.film_id
LEFT JOIN payment p ON r.rental_id = p.rental_id
WHERE r.return_date IS NULL
  AND p.payment_id IS NULL
GROUP BY c.customer_id, c.first_name, c.last_name
HAVING SUM(f.rental_rate) > 0
ORDER BY amount_owing DESC;

-- Create customer_account table
CREATE TABLE customer_account (
  account_id INT AUTO_INCREMENT PRIMARY KEY,
  customer_id INT NOT NULL UNIQUE,
  balance DECIMAL(10,2) DEFAULT 0,
  last_payment_date DATETIME,
  status ENUM('good_standing', 'past_due', 'closed') DEFAULT 'good_standing',
  FOREIGN KEY (customer_id) REFERENCES customer(customer_id)
);
```

---

### 7. **LOW: No Return Condition Assessment**

**Issue:**
- No field for condition of returned item (scratched, damaged, etc.)
- Cannot track damage-related write-offs
- Cannot correlate damage with replacement costs

**Impact:**
- Damage costs buried in inventory shrinkage
- No incentive tracking
- Unexpected replacement costs

**Analyst Action Required:**
```sql
-- Add condition tracking
ALTER TABLE rental ADD COLUMN return_condition ENUM('excellent', 'good', 'damaged', 'missing') DEFAULT NULL;

-- Query for damages
SELECT 
  f.title,
  COUNT(*) as damaged_count,
  SUM(f.replacement_cost) as total_replacement_value
FROM rental r
JOIN inventory i ON r.inventory_id = i.inventory_id
JOIN film f ON i.film_id = f.film_id
WHERE r.return_condition = 'damaged'
GROUP BY f.film_id, f.title
ORDER BY total_replacement_value DESC;
```

---

## ✅ What's Working Well

1. **NULL return_date for unreturned items** - Perfect for analysis
2. **Realistic rental patterns** - 30% unreturned matches real business
3. **Payment recording for completed rentals** - Good practice
4. **Separate rental and payment tables** - Proper normalization
5. **Customer tracking** - Can see who owes what

---

## 📋 Recommended Fixes (Priority Order)

| Priority | Issue | Fix Type | Effort |
|----------|-------|----------|--------|
| CRITICAL | Inventory status not tracked | Add status column | Low |
| CRITICAL | Unreturned rentals missing payments | Generate "pending" payments | Medium |
| HIGH | No late fee calculation | Add due_date logic | Low |
| HIGH | No rental status field | Add computed status | Low |
| MEDIUM | Inventory audit trail | Create new table | Medium |
| MEDIUM | Customer AR tracking | Create account table | Medium |
| LOW | Return condition not recorded | Add enum field | Low |

---

## Summary

**The current design is GOOD for analysis** but needs analyst attention to:
1. ✅ Keep NULL return_date for unreturned items
2. ⚠️ Add inventory status tracking
3. ⚠️ Generate pending payment records for unreturned rentals
4. ⚠️ Implement late fee calculations
5. ⚠️ Add audit trails for accountability

**This is realistic!** Real businesses have exactly these problems - the data looks good but needs reconciliation. An analyst would need to periodically:
- Reconcile physical inventory to system records
- Investigate old unreturned items (lost vs. in progress)
- Calculate and collect outstanding payments
- Track inventory shrinkage
- Monitor customer AR aging
