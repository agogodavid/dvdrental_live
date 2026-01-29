# Film Releases Analysis Guide

## Overview
The `film_releases` table is **automatically created and populated** when you run `master_simulation.py`. This enables students to analyze which films were released during the simulation and which inventory decisions were made.

## Table Structure

```sql
CREATE TABLE film_releases (
    release_id INT AUTO_INCREMENT PRIMARY KEY,
    film_id INT NOT NULL,
    release_quarter VARCHAR(10) NOT NULL,
    release_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (film_id) REFERENCES film(film_id)
);
```

### Columns:
- **release_id**: Unique identifier for each release record
- **film_id**: Reference to the film that was released
- **release_quarter**: Quarter format (Q1 2001, Q2 2001, etc.)
- **release_date**: Exact date the film was released/added to inventory
- **created_at**: Timestamp when the record was created

## How It Works

### 1. **When master_simulation.py Runs:**
   - During each simulation week, new films are added according to the `hot_categories` schedule in `config.json`
   - Every new film is:
     - Added to the `film` table with title, rating, year, etc.
     - Added to the `inventory` table (5-7 copies per store)
     - **Recorded in `film_releases` table** with the simulation date

### 2. **Hot Categories Schedule (from config.json):**
```json
"hot_categories": [
  {
    "category": "Action",
    "weeks": [4, 8, 12, 16, 20, 24],
    "weekly_releases": 4
  },
  {
    "category": "Comedy", 
    "weeks": [5, 9, 13, 17, 21, 25],
    "weekly_releases": 4
  }
]
```

Each time a hot category week occurs, the specified number of films are added and recorded.

### 3. **Automatic Tracking:**
In `level_3_master_simulation/film_system/film_generator.py` (lines 553-557):
```python
# Record film release
release_quarter = self.get_quarter_for_date(film_date)

self.cursor.execute("""
    INSERT INTO film_releases (film_id, release_quarter, release_date)
    VALUES (%s, %s, %s)
""", (film_id, release_quarter, film_date))
```

## Student Analysis Opportunities

### Analysis 1: What Films Were Released?
```sql
-- See all films released during the simulation
SELECT 
    fr.release_date,
    f.film_id,
    f.title,
    f.rating,
    c.name as category
FROM film_releases fr
JOIN film f ON fr.film_id = f.film_id
LEFT JOIN film_category fc ON f.film_id = fc.film_id
LEFT JOIN category c ON fc.category_id = c.category_id
ORDER BY fr.release_date;
```

### Analysis 2: Which Released Films Were Purchased (Added to Inventory)?
```sql
-- Compare film releases to actual inventory purchases
SELECT 
    fr.release_date,
    f.title,
    CASE 
        WHEN i.film_id IS NOT NULL THEN 'PURCHASED'
        ELSE 'NOT PURCHASED'
    END as purchase_status,
    COUNT(i.inventory_id) as copies_purchased,
    GROUP_CONCAT(DISTINCT s.store_id) as stores
FROM film_releases fr
JOIN film f ON fr.film_id = f.film_id
LEFT JOIN inventory i ON f.film_id = i.film_id
LEFT JOIN store s ON i.store_id = s.store_id
GROUP BY fr.film_id, f.title, fr.release_date
ORDER BY fr.release_date;
```

### Analysis 3: Released Films That Were NOT Purchased
```sql
-- Identify films that were released but NOT added to inventory
SELECT 
    f.title,
    f.rating,
    c.name as category,
    fr.release_date,
    COUNT(DISTINCT r.rental_id) as times_rented
FROM film_releases fr
JOIN film f ON fr.film_id = f.film_id
LEFT JOIN film_category fc ON f.film_id = fc.film_id
LEFT JOIN category c ON fc.category_id = c.category_id
LEFT JOIN rental r ON f.film_id IN (
    SELECT film_id FROM inventory WHERE inventory_id = r.inventory_id
)
WHERE f.film_id NOT IN (
    SELECT DISTINCT film_id FROM inventory 
    WHERE date_purchased <= DATE_ADD(fr.release_date, INTERVAL 7 DAY)
)
GROUP BY f.film_id
ORDER BY times_rented DESC;
```

### Analysis 4: Profitability of Released Films
```sql
-- Analyze revenue from released films vs. non-released films
SELECT 
    CASE 
        WHEN fr.film_id IS NOT NULL THEN 'RELEASED'
        ELSE 'NOT RELEASED'
    END as film_status,
    COUNT(DISTINCT f.film_id) as num_films,
    COUNT(r.rental_id) as total_rentals,
    SUM(p.amount) as total_revenue,
    AVG(p.amount) as avg_rental_revenue,
    AVG(f.rental_rate) as avg_rental_rate
FROM film f
LEFT JOIN film_releases fr ON f.film_id = fr.film_id
LEFT JOIN inventory i ON f.film_id = i.film_id
LEFT JOIN rental r ON i.inventory_id = r.inventory_id
LEFT JOIN payment p ON r.rental_id = p.rental_id
WHERE p.payment_date IS NOT NULL
GROUP BY film_status
ORDER BY total_revenue DESC;
```

### Analysis 5: Hot Category Performance
```sql
-- Compare performance of different hot categories
SELECT 
    c.name as category,
    COUNT(DISTINCT fr.film_id) as films_released,
    COUNT(DISTINCT i.inventory_id) as inventory_items,
    COUNT(DISTINCT r.rental_id) as total_rentals,
    SUM(p.amount) as total_revenue
FROM film_releases fr
JOIN film f ON fr.film_id = f.film_id
LEFT JOIN film_category fc ON f.film_id = fc.film_id
LEFT JOIN category c ON fc.category_id = c.category_id
LEFT JOIN inventory i ON f.film_id = i.film_id
LEFT JOIN rental r ON i.inventory_id = r.inventory_id
LEFT JOIN payment p ON r.rental_id = p.rental_id
WHERE c.name IS NOT NULL
GROUP BY c.name
ORDER BY total_revenue DESC;
```

## How to View Film Releases

### Method 1: Using check_film_releases.py
```bash
python check_film_releases.py
```

This script provides multiple viewing options:
- Show all film releases
- Show film releases with inventory purchase status
- Show profit metrics for released films

### Method 2: Direct MySQL Query
```bash
mysql -u root -proot dvdrental_live -e "
SELECT 
    release_date,
    COUNT(*) as films_released
FROM film_releases
GROUP BY DATE(release_date)
ORDER BY release_date;
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
    fr.release_date,
    f.title,
    COUNT(i.inventory_id) as copies_purchased
FROM film_releases fr
JOIN film f ON fr.film_id = f.film_id
LEFT JOIN inventory i ON f.film_id = i.film_id
GROUP BY fr.film_id
ORDER BY fr.release_date
""")

for row in cursor.fetchall():
    print(f"{row['release_date']}: {row['title']} ({row['copies_purchased']} copies)")

cursor.close()
conn.close()
```

## Key Learning Opportunities for Students

1. **Inventory Management**: Which released films should have been purchased?
2. **Category Strategy**: Do certain categories perform better than others?
3. **Timing Decisions**: Should films be purchased immediately on release or wait?
4. **Stock Optimization**: What's the optimal number of copies per store?
5. **Profitability Analysis**: How does film selection impact overall revenue?
6. **Demand Forecasting**: Were there unreleased films that should have been added to inventory?

## Implementation Timeline

- **Week 0 (Initial Setup)**: 500 films seeded (1991-2000 release years)
- **Week 4, 8, 12, etc.**: Hot category films released according to schedule
- **Throughout Simulation**: Students can observe which films are released vs. purchased

## Notes

- The `film_releases` table only tracks films released **during the simulation**
- Initial seed films (Weeks 0-3) are **not** in `film_releases` (they're pre-existing catalog)
- Each run of `master_simulation.py` creates a fresh `film_releases` record for that run
- The table persists across weeks for historical analysis
