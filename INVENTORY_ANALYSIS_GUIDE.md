# Inventory Analysis Guide

## Overview
The updated inventory system now tracks:
- **date_purchased**: When the inventory batch was purchased (enables aging analysis)
- **staff_id**: Which staff member processed the purchase (enables staff performance analysis)

This enables comprehensive profitability analysis of inventory purchase batches.

---

## Key Analysis Queries

### 1. Inventory Batch Profitability Analysis

**Revenue by Purchase Batch:**
```sql
SELECT 
    i.date_purchased,
    s.first_name,
    s.last_name,
    f.title,
    COUNT(DISTINCT i.inventory_id) as copies_in_batch,
    COUNT(DISTINCT r.rental_id) as total_rentals,
    ROUND(SUM(f.rental_rate) * COUNT(r.rental_id), 2) as batch_revenue,
    ROUND(DATEDIFF(CURDATE(), i.date_purchased) / 7) as weeks_in_stock,
    ROUND(SUM(f.rental_rate) * COUNT(r.rental_id) / (DATEDIFF(CURDATE(), i.date_purchased) + 1) * 7, 2) as weekly_revenue,
    f.replacement_cost,
    ROUND(SUM(f.rental_rate) * COUNT(r.rental_id) - (f.replacement_cost * COUNT(DISTINCT i.inventory_id)), 2) as net_profit
FROM inventory i
JOIN film f ON i.film_id = f.film_id
JOIN staff s ON i.staff_id = s.staff_id
LEFT JOIN rental r ON i.inventory_id = r.inventory_id
GROUP BY i.date_purchased, i.staff_id, i.film_id
ORDER BY batch_revenue DESC;
```

### 2. Inventory Aging Analysis

**Identify slow-moving inventory:**
```sql
SELECT 
    i.inventory_id,
    f.title,
    f.category_id,
    i.date_purchased,
    st.store_id,
    DATEDIFF(CURDATE(), i.date_purchased) as days_in_stock,
    COUNT(r.rental_id) as total_rentals,
    CASE 
        WHEN COUNT(r.rental_id) = 0 THEN 'Never Rented'
        WHEN COUNT(r.rental_id) < 3 THEN 'Low Activity'
        WHEN COUNT(r.rental_id) < 10 THEN 'Moderate Activity'
        ELSE 'High Activity'
    END as performance_tier,
    MAX(r.rental_date) as last_rental_date
FROM inventory i
JOIN film f ON i.film_id = f.film_id
JOIN store st ON i.store_id = st.store_id
LEFT JOIN rental r ON i.inventory_id = r.inventory_id
GROUP BY i.inventory_id, i.date_purchased
HAVING days_in_stock > 30
ORDER BY total_rentals ASC, days_in_stock DESC;
```

### 3. Staff Performance Analysis

**Which staff members sourced the most profitable inventory:**
```sql
SELECT 
    s.staff_id,
    CONCAT(s.first_name, ' ', s.last_name) as staff_member,
    COUNT(DISTINCT i.inventory_id) as total_inventory_added,
    COUNT(DISTINCT DATE(i.date_purchased)) as purchase_dates,
    ROUND(SUM(f.rental_rate) * COUNT(DISTINCT r.rental_id), 2) as total_revenue,
    ROUND(AVG(f.rental_rate) * COUNT(DISTINCT r.rental_id) / COUNT(DISTINCT i.inventory_id), 2) as avg_revenue_per_item,
    ROUND(SUM(f.rental_rate) * COUNT(DISTINCT r.rental_id) - (SUM(f.replacement_cost) * COUNT(DISTINCT i.inventory_id)), 2) as total_profit,
    ROUND(COUNT(DISTINCT r.rental_id) / NULLIF(COUNT(DISTINCT i.inventory_id), 0), 2) as rental_ratio
FROM staff s
JOIN inventory i ON s.staff_id = i.staff_id
JOIN film f ON i.film_id = f.film_id
LEFT JOIN rental r ON i.inventory_id = r.inventory_id
GROUP BY s.staff_id, s.first_name, s.last_name
ORDER BY total_profit DESC;
```

### 4. Purchase Batch Comparison

**Compare profitability across purchase dates:**
```sql
SELECT 
    DATE_FORMAT(i.date_purchased, '%Y-%m-%d') as purchase_date,
    COUNT(DISTINCT i.inventory_id) as items_purchased,
    COUNT(DISTINCT i.film_id) as unique_films,
    COUNT(DISTINCT i.staff_id) as staff_involved,
    ROUND(SUM(f.replacement_cost * 1), 2) as total_cost,
    ROUND(SUM(f.rental_rate) * COUNT(DISTINCT r.rental_id), 2) as total_revenue,
    ROUND(AVG(f.rental_rate) * COUNT(DISTINCT r.rental_id) / COUNT(DISTINCT i.inventory_id), 2) as avg_revenue_per_item,
    ROUND(SUM(f.rental_rate) * COUNT(DISTINCT r.rental_id) - SUM(f.replacement_cost) * COUNT(DISTINCT i.inventory_id), 2) as batch_profit
FROM inventory i
JOIN film f ON i.film_id = f.film_id
LEFT JOIN rental r ON i.inventory_id = r.inventory_id
GROUP BY DATE(i.date_purchased)
ORDER BY purchase_date DESC;
```

### 5. ROI by Inventory Batch

**Calculate Return on Investment for each batch:**
```sql
SELECT 
    i.date_purchased,
    CONCAT(s.first_name, ' ', s.last_name) as sourced_by,
    COUNT(DISTINCT i.inventory_id) as units_purchased,
    ROUND(SUM(f.replacement_cost), 2) as total_investment,
    ROUND(SUM(f.rental_rate) * COUNT(DISTINCT r.rental_id), 2) as total_revenue,
    ROUND((SUM(f.rental_rate) * COUNT(DISTINCT r.rental_id) - SUM(f.replacement_cost)) / NULLIF(SUM(f.replacement_cost), 0) * 100, 2) as roi_percent,
    DATEDIFF(CURDATE(), i.date_purchased) as days_since_purchase,
    ROUND((SUM(f.rental_rate) * COUNT(DISTINCT r.rental_id) - SUM(f.replacement_cost)) / NULLIF(DATEDIFF(CURDATE(), i.date_purchased) + 1, 0) * 30, 2) as monthly_profit
FROM inventory i
JOIN film f ON i.film_id = f.film_id
JOIN staff s ON i.staff_id = s.staff_id
LEFT JOIN rental r ON i.inventory_id = r.inventory_id
GROUP BY i.date_purchased, i.staff_id, s.staff_id
ORDER BY roi_percent DESC;
```

### 6. Store Performance by Purchase Batch

**Which store locations profit most from specific purchase batches:**
```sql
SELECT 
    i.date_purchased,
    st.store_id,
    a.city,
    COUNT(DISTINCT i.inventory_id) as inventory_from_batch,
    ROUND(SUM(f.rental_rate) * COUNT(DISTINCT r.rental_id), 2) as revenue_from_batch,
    ROUND(SUM(f.rental_rate) * COUNT(DISTINCT r.rental_id) - SUM(f.replacement_cost) * COUNT(DISTINCT i.inventory_id), 2) as profit_from_batch,
    ROUND(COUNT(DISTINCT r.rental_id) / NULLIF(COUNT(DISTINCT i.inventory_id), 0), 2) as utilization_rate
FROM inventory i
JOIN store st ON i.store_id = st.store_id
JOIN address a ON st.address_id = a.address_id
JOIN film f ON i.film_id = f.film_id
LEFT JOIN rental r ON i.inventory_id = r.inventory_id
GROUP BY i.date_purchased, st.store_id, a.city
ORDER BY i.date_purchased DESC, profit_from_batch DESC;
```

### 7. Breakeven Analysis

**How long does each batch take to break even on investment:**
```sql
SELECT 
    i.date_purchased,
    CONCAT(s.first_name, ' ', s.last_name) as staff,
    COUNT(DISTINCT i.inventory_id) as items,
    ROUND(SUM(f.replacement_cost), 2) as investment,
    ROUND(SUM(f.rental_rate), 2) as total_rental_rate,
    CEIL(SUM(f.replacement_cost) / NULLIF(SUM(f.rental_rate), 0)) as rentals_to_breakeven,
    ROUND(COUNT(DISTINCT r.rental_id) / NULLIF(CEIL(SUM(f.replacement_cost) / NULLIF(SUM(f.rental_rate), 0)), 0) * 100, 2) as breakeven_percent
FROM inventory i
JOIN film f ON i.film_id = f.film_id
JOIN staff s ON i.staff_id = s.staff_id
LEFT JOIN rental r ON i.inventory_id = r.inventory_id
GROUP BY i.date_purchased, i.staff_id, s.staff_id
ORDER BY breakeven_percent DESC;
```

---

## Analysis Insights You Can Discover

### For Students:

1. **Inventory Turnover**: Identify which purchase batches have the fastest turnover
2. **Staff Performance**: See which staff members source the most profitable inventory
3. **Aging Inventory**: Identify slow-moving stock that might need attention
4. **ROI Comparison**: Compare profitability across different purchase dates
5. **Store Performance**: Understand which locations benefit most from specific batches
6. **Risk Management**: Identify items that haven't generated revenue
7. **Demand Patterns**: Correlate purchase dates with seasonal demand

### Learning Objectives:

Students can learn:
- How to analyze profitability at the batch level
- The importance of inventory tracking
- Staff accountability and performance measurement
- Decision-making based on data (when to purchase, what to purchase)
- SQL aggregate functions and complex joins
- Business metrics (ROI, utilization, breakeven)

---

## Using the Data in Your Application

### Example: Add inventory with specific staff and date
```python
from inventory_manager import InventoryManager
from datetime import date, timedelta

manager = InventoryManager(config)
manager.connect()

# Add inventory from a specific purchase date
purchase_date = date(2024, 1, 15)
staff_id = 1  # Staff member ID

quantity = 50
manager.add_fixed_quantity(
    quantity=quantity,
    date_purchased=purchase_date,
    staff_id=staff_id
)
```

### Example: Monthly batch analysis
```sql
-- Generate a monthly profitability report
SELECT 
    DATE_FORMAT(i.date_purchased, '%Y-%m') as month,
    COUNT(DISTINCT i.inventory_id) as items_purchased,
    ROUND(SUM(f.replacement_cost), 2) as investment,
    ROUND(SUM(f.rental_rate) * COUNT(DISTINCT r.rental_id), 2) as revenue,
    ROUND(SUM(f.rental_rate) * COUNT(DISTINCT r.rental_id) - SUM(f.replacement_cost) * COUNT(DISTINCT i.inventory_id), 2) as profit
FROM inventory i
JOIN film f ON i.film_id = f.film_id
LEFT JOIN rental r ON i.inventory_id = r.inventory_id
GROUP BY DATE_FORMAT(i.date_purchased, '%Y-%m')
ORDER BY month DESC;
```

---

## Creating Custom Analysis Views

You can create views for easier analysis:

```sql
-- Batch profitability view
CREATE VIEW v_batch_profitability AS
SELECT 
    i.date_purchased,
    CONCAT(s.first_name, ' ', s.last_name) as staff_member,
    COUNT(DISTINCT i.inventory_id) as batch_size,
    ROUND(SUM(f.rental_rate) * COUNT(DISTINCT r.rental_id), 2) as revenue,
    ROUND(SUM(f.replacement_cost), 2) as cost,
    ROUND(SUM(f.rental_rate) * COUNT(DISTINCT r.rental_id) - SUM(f.replacement_cost), 2) as profit
FROM inventory i
JOIN film f ON i.film_id = f.film_id
JOIN staff s ON i.staff_id = s.staff_id
LEFT JOIN rental r ON i.inventory_id = r.inventory_id
GROUP BY i.date_purchased, i.staff_id;
```

---

## Next Steps

1. **Use the queries** to analyze your current inventory data
2. **Create dashboards** or reports from the results
3. **Track metrics over time** to identify trends
4. **Make data-driven decisions** about future inventory purchases
