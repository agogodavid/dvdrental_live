# Inventory Purchases Analysis Guide

## Overview

The `inventory_purchases` table **is automatically created and populated** when you run `master_simulation.py`. This table links every inventory purchase decision to the staff member who made it, enabling analysis of individual employee purchasing effectiveness.

## Table Structure

```sql
CREATE TABLE inventory_purchases (
    purchase_id INT AUTO_INCREMENT PRIMARY KEY,
    film_id INT NOT NULL,
    inventory_id INT,
    staff_id INT,
    purchase_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (film_id) REFERENCES film(film_id),
    FOREIGN KEY (inventory_id) REFERENCES inventory(inventory_id),
    FOREIGN KEY (staff_id) REFERENCES staff(staff_id),
    INDEX idx_film_id (film_id),
    INDEX idx_staff_id (staff_id),
    INDEX idx_purchase_date (purchase_date)
);
```

### Columns:
- **purchase_id**: Unique identifier for each purchase record
- **film_id**: The film that was purchased/added to inventory
- **inventory_id**: Reference to the specific inventory item created
- **staff_id**: The staff member who decided to purchase this inventory
- **purchase_date**: When the purchase was made
- **created_at**: Timestamp when the record was created

## How It Works

### 1. **Initial Setup (Week 0)**
- Seed films are added during database initialization with randomized staff assignment
- Each inventory copy is linked to a random staff member in the `inventory_purchases` table

### 2. **During Simulation (Weeks 1+)**
Each time inventory is added (based on the seasonal schedule):
- Random films are selected for purchase
- Random stores are chosen for stocking
- A random staff member is assigned as the "purchaser"
- The purchase decision is recorded in `inventory_purchases` table

Example flow for "Q1 Growth - 50 items":
```
Week 13 → Add 50 inventory items
├─ 50 items to random films
├─ Distributed across stores
├─ Each assigned to random staff member
└─ All recorded in inventory_purchases with staff_id
```

### 3. **Automatic Tracking**
In `level_3_master_simulation/master_simulation.py` (lines 310-343):
```python
# Record inventory purchases
purchase_records = []
for i in range(len(inventory)):
    inventory_id = first_inventory_id + i
    # For periodic inventory additions, link to staff member
    staff_id = inventory[i][3] if inventory[i][3] else None
    film_id = inventory[i][0]
    purchase_records.append((film_id, inventory_id, staff_id, purchase_date))

cursor.executemany("""
    INSERT INTO inventory_purchases (film_id, inventory_id, staff_id, purchase_date)
    VALUES (%s, %s, %s, %s)
""", purchase_records)
```

## Student Analysis Opportunities

### Analysis 1: Individual Staff Performance - Revenue Per Purchase Decision
```sql
-- Which staff member's purchasing decisions generated the most revenue?
SELECT 
    s.staff_id,
    s.first_name,
    s.last_name,
    COUNT(DISTINCT ip.purchase_id) as total_purchases,
    COUNT(DISTINCT ip.inventory_id) as inventory_items_purchased,
    COUNT(DISTINCT CASE WHEN r.rental_id IS NOT NULL THEN r.rental_id END) as rentals_from_purchases,
    SUM(p.amount) as total_revenue_from_purchases,
    ROUND(AVG(p.amount), 2) as avg_rental_rate,
    ROUND(SUM(p.amount) / COUNT(DISTINCT ip.purchase_id), 2) as revenue_per_purchase_decision
FROM staff s
LEFT JOIN inventory_purchases ip ON s.staff_id = ip.staff_id
LEFT JOIN inventory i ON ip.inventory_id = i.inventory_id
LEFT JOIN rental r ON i.inventory_id = r.inventory_id
LEFT JOIN payment p ON r.rental_id = p.rental_id
GROUP BY s.staff_id, s.first_name, s.last_name
ORDER BY total_revenue_from_purchases DESC;
```

### Analysis 2: Purchase Effectiveness - Hit Rate
```sql
-- How many of each staff member's inventory purchases actually got rented?
SELECT 
    s.staff_id,
    CONCAT(s.first_name, ' ', s.last_name) as staff_name,
    COUNT(DISTINCT ip.inventory_id) as total_items_purchased,
    COUNT(DISTINCT CASE WHEN r.rental_id IS NOT NULL THEN i.inventory_id END) as items_that_were_rented,
    ROUND(
        100 * COUNT(DISTINCT CASE WHEN r.rental_id IS NOT NULL THEN i.inventory_id END) 
        / COUNT(DISTINCT ip.inventory_id), 
        1
    ) as rental_hit_rate_percent,
    COUNT(DISTINCT r.rental_id) as total_rentals
FROM staff s
LEFT JOIN inventory_purchases ip ON s.staff_id = ip.staff_id
LEFT JOIN inventory i ON ip.inventory_id = i.inventory_id
LEFT JOIN rental r ON i.inventory_id = r.inventory_id
GROUP BY s.staff_id, s.first_name, s.last_name
ORDER BY rental_hit_rate_percent DESC;
```

### Analysis 3: Film Category Preferences by Staff
```sql
-- Which film categories does each staff member tend to purchase?
SELECT 
    s.staff_id,
    CONCAT(s.first_name, ' ', s.last_name) as staff_name,
    c.name as category,
    COUNT(DISTINCT ip.purchase_id) as purchases_in_category,
    SUM(p.amount) as revenue_from_category,
    ROUND(
        100 * COUNT(DISTINCT ip.purchase_id) 
        / (SELECT COUNT(DISTINCT ip2.purchase_id) FROM inventory_purchases ip2 WHERE ip2.staff_id = s.staff_id),
        1
    ) as percent_of_staff_purchases
FROM staff s
LEFT JOIN inventory_purchases ip ON s.staff_id = ip.staff_id
LEFT JOIN film f ON ip.film_id = f.film_id
LEFT JOIN film_category fc ON f.film_id = fc.film_id
LEFT JOIN category c ON fc.category_id = c.category_id
LEFT JOIN inventory i ON ip.inventory_id = i.inventory_id
LEFT JOIN rental r ON i.inventory_id = r.inventory_id
LEFT JOIN payment p ON r.rental_id = p.rental_id
WHERE c.name IS NOT NULL
GROUP BY s.staff_id, s.first_name, s.last_name, c.name
ORDER BY s.staff_id, revenue_from_category DESC;
```

### Analysis 4: Purchase Decision Quality - Revenue Per Item
```sql
-- Who makes the best purchasing decisions on a per-item basis?
SELECT 
    s.staff_id,
    CONCAT(s.first_name, ' ', s.last_name) as staff_name,
    COUNT(DISTINCT ip.inventory_id) as items_purchased,
    COUNT(DISTINCT r.rental_id) as times_rented,
    SUM(p.amount) as total_revenue,
    ROUND(SUM(p.amount) / COUNT(DISTINCT ip.inventory_id), 2) as revenue_per_item_purchased,
    ROUND(AVG(p.amount), 2) as avg_rental_amount
FROM staff s
LEFT JOIN inventory_purchases ip ON s.staff_id = ip.staff_id
LEFT JOIN inventory i ON ip.inventory_id = i.inventory_id
LEFT JOIN rental r ON i.inventory_id = r.inventory_id
LEFT JOIN payment p ON r.rental_id = p.rental_id
GROUP BY s.staff_id
HAVING COUNT(DISTINCT ip.inventory_id) > 0
ORDER BY revenue_per_item_purchased DESC;
```

### Analysis 5: Timing of Purchases - When Do Good Decisions Get Made?
```sql
-- Do staff members make better purchase decisions at certain times?
SELECT 
    s.staff_id,
    CONCAT(s.first_name, ' ', s.last_name) as staff_name,
    QUARTER(ip.purchase_date) as purchase_quarter,
    YEAR(ip.purchase_date) as purchase_year,
    COUNT(DISTINCT ip.purchase_id) as purchases,
    SUM(p.amount) as revenue,
    ROUND(SUM(p.amount) / COUNT(DISTINCT ip.purchase_id), 2) as revenue_per_purchase
FROM staff s
LEFT JOIN inventory_purchases ip ON s.staff_id = ip.staff_id
LEFT JOIN inventory i ON ip.inventory_id = i.inventory_id
LEFT JOIN rental r ON i.inventory_id = r.inventory_id
LEFT JOIN payment p ON r.rental_id = p.rental_id
GROUP BY s.staff_id, QUARTER(ip.purchase_date), YEAR(ip.purchase_date)
ORDER BY s.staff_id, purchase_year, purchase_quarter;
```

### Analysis 6: Risky Decisions - Items That Never Rented
```sql
-- Which staff members made the most expensive purchases that never rented?
SELECT 
    s.staff_id,
    CONCAT(s.first_name, ' ', s.last_name) as staff_name,
    f.title,
    f.replacement_cost,
    ip.purchase_date,
    COUNT(r.rental_id) as times_rented,
    CASE WHEN r.rental_id IS NULL THEN 'Never rented' ELSE 'Rented' END as status
FROM staff s
LEFT JOIN inventory_purchases ip ON s.staff_id = ip.staff_id
LEFT JOIN inventory i ON ip.inventory_id = i.inventory_id
LEFT JOIN film f ON ip.film_id = f.film_id
LEFT JOIN rental r ON i.inventory_id = r.inventory_id
WHERE r.rental_id IS NULL OR COUNT(r.rental_id) = 0
GROUP BY ip.inventory_id
ORDER BY s.staff_id, f.replacement_cost DESC;
```

### Analysis 7: Staff Collaboration - Who Buys What Others Don't?
```sql
-- Identify unique films purchased by specific staff members
SELECT 
    s.staff_id,
    CONCAT(s.first_name, ' ', s.last_name) as staff_name,
    f.title,
    f.rating,
    c.name as category,
    COUNT(DISTINCT ip.purchase_id) as purchases_by_this_staff,
    (SELECT COUNT(DISTINCT staff_id) FROM inventory_purchases ip2 
     WHERE ip2.film_id = f.film_id) as how_many_staff_bought_this
FROM staff s
LEFT JOIN inventory_purchases ip ON s.staff_id = ip.staff_id
LEFT JOIN film f ON ip.film_id = f.film_id
LEFT JOIN film_category fc ON f.film_id = fc.film_id
LEFT JOIN category c ON fc.category_id = c.category_id
WHERE f.film_id IS NOT NULL
GROUP BY f.film_id, s.staff_id
HAVING how_many_staff_bought_this = 1
ORDER BY s.staff_id, f.title;
```

## How to View Inventory Purchases

### Method 1: Using check_film_releases.py
```bash
python check_film_releases.py
```

Option: "Show inventory purchases"
- Displays all inventory purchases with staff names
- Shows revenue metrics per staff member
- Displays profit summaries

### Method 2: Direct MySQL Query
```bash
mysql -u root -proot dvdrental_live -e "
SELECT 
    s.first_name,
    s.last_name,
    COUNT(*) as purchases,
    SUM(CASE WHEN r.rental_id IS NOT NULL THEN 1 ELSE 0 END) as rented
FROM inventory_purchases ip
JOIN staff s ON ip.staff_id = s.staff_id
LEFT JOIN inventory i ON ip.inventory_id = i.inventory_id
LEFT JOIN rental r ON i.inventory_id = r.inventory_id
GROUP BY ip.staff_id
ORDER BY rented DESC;
"
```

### Method 3: Python Analysis
```python
import mysql.connector
import json

with open('config.json') as f:
    config = json.load(f)

conn = mysql.connector.connect(**config['mysql'])
cursor = conn.cursor(dictionary=True)

cursor.execute("""
SELECT 
    s.first_name,
    s.last_name,
    COUNT(DISTINCT ip.purchase_id) as purchases,
    SUM(p.amount) as revenue
FROM inventory_purchases ip
JOIN staff s ON ip.staff_id = s.staff_id
LEFT JOIN inventory i ON ip.inventory_id = i.inventory_id
LEFT JOIN rental r ON i.inventory_id = r.inventory_id
LEFT JOIN payment p ON r.rental_id = p.rental_id
GROUP BY s.staff_id
ORDER BY revenue DESC
""")

for row in cursor.fetchall():
    print(f"{row['first_name']} {row['last_name']}: {row['purchases']} purchases, ${row['revenue']:.2f} revenue")

cursor.close()
conn.close()
```

## Key Learning Opportunities for Students

1. **Decision Quality**: Whose purchasing decisions are most profitable?
2. **Risk Assessment**: Who tends to make risky purchases (low hit rates)?
3. **Category Expertise**: Does any staff member specialize in certain categories?
4. **Timing**: Are certain seasons better for purchasing decisions?
5. **Profitability**: Compare revenue generated per purchase decision
6. **Conservative vs. Aggressive**: Who takes more risks vs. plays it safe?
7. **Learning Over Time**: Do staff members improve their decisions as time goes on?
8. **Collaboration**: Can combining different staff strategies improve results?

## Inventory Purchase Schedule

The simulation follows a seasonal inventory addition pattern:

| Phase | Weeks | Quantity | Goal |
|-------|-------|----------|------|
| **Growth** | 13-104 | 50 items/quarter | Rapid inventory expansion |
| **Plateau** | 104-312 | 30 items/4-months | Maintain inventory levels |
| **Decline** | 312-416 | 15 items/5-months | Minimal new purchases |
| **Reactivation** | 416+ | 25 items/quarter | Strategic growth |

Each purchase wave is recorded with the responsible staff member linked to it.

## Data Quality Notes

- **Staff Assignment**: Randomly assigned during simulation (represents delegation/decision-making)
- **Purchase Timing**: Uses actual simulation dates (not real-time)
- **Film Selection**: Random selection from all available films
- **Store Distribution**: Random distribution across stores
- **Persistence**: Data persists for full analysis after simulation completes

## Integration with Other Tables

```
inventory_purchases
├── film_id → film (what was purchased)
├── inventory_id → inventory (the actual item)
├── staff_id → staff (who decided to purchase)
└── purchase_date → date dimension
    └── Correlates with film_releases to compare
        "what was released" vs "what was purchased"
```

This enables analysis of:
- Whether staff purchase released films
- Portfolio overlap (diversity of purchasing)
- Reaction time to releases
