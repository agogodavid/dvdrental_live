-- Late Fees View for Analysts
-- Calculates late fees for overdue rentals based on rental duration and return date
-- Late fee rate: $1.50 per day overdue

CREATE OR REPLACE VIEW v_late_fees AS
SELECT 
    r.rental_id,
    r.customer_id,
    c.first_name,
    c.last_name,
    c.email,
    f.title,
    f.rental_duration,
    r.rental_date,
    DATE_ADD(r.rental_date, INTERVAL f.rental_duration DAY) as due_date,
    r.return_date,
    CASE 
        WHEN r.return_date IS NULL THEN DATEDIFF(CURDATE(), DATE_ADD(r.rental_date, INTERVAL f.rental_duration DAY))
        ELSE DATEDIFF(r.return_date, DATE_ADD(r.rental_date, INTERVAL f.rental_duration DAY))
    END as days_overdue,
    CASE 
        WHEN r.return_date IS NULL THEN DATEDIFF(CURDATE(), DATE_ADD(r.rental_date, INTERVAL f.rental_duration DAY)) * 1.50
        ELSE DATEDIFF(r.return_date, DATE_ADD(r.rental_date, INTERVAL f.rental_duration DAY)) * 1.50
    END as late_fee_amount,
    CASE 
        WHEN r.return_date IS NULL THEN 'Overdue'
        WHEN DATEDIFF(r.return_date, DATE_ADD(r.rental_date, INTERVAL f.rental_duration DAY)) > 0 THEN 'Late Return'
        ELSE 'On Time'
    END as rental_status
FROM rental r
JOIN customer c ON r.customer_id = c.customer_id
JOIN inventory i ON r.inventory_id = i.inventory_id
JOIN film f ON i.film_id = f.film_id
WHERE (
    -- Include rentals that are currently overdue (not returned yet)
    r.return_date IS NULL
    OR 
    -- Include rentals that were returned late
    DATEDIFF(r.return_date, DATE_ADD(r.rental_date, INTERVAL f.rental_duration DAY)) > 0
)
AND DATEDIFF(
    COALESCE(r.return_date, CURDATE()), 
    DATE_ADD(r.rental_date, INTERVAL f.rental_duration DAY)
) > 0;

-- Summary view for customer late fees
CREATE OR REPLACE VIEW v_customer_late_fees AS
SELECT 
    customer_id,
    first_name,
    last_name,
    email,
    COUNT(*) as total_overdue_rentals,
    SUM(days_overdue) as total_days_overdue,
    SUM(late_fee_amount) as total_late_fees,
    MAX(days_overdue) as max_days_overdue,
    MAX(late_fee_amount) as max_late_fee
FROM v_late_fees
GROUP BY customer_id, first_name, last_name, email
HAVING total_late_fees > 0
ORDER BY total_late_fees DESC;

-- Inventory status view
CREATE OR REPLACE VIEW v_inventory_status AS
SELECT 
    i.inventory_id,
    f.title,
    i.store_id,
    CASE 
        WHEN r.rental_id IS NOT NULL AND r.return_date IS NULL THEN 'Rented'
        ELSE 'Available'
    END as current_status,
    r.rental_date,
    r.customer_id,
    c.first_name as customer_first_name,
    c.last_name as customer_last_name
FROM inventory i
JOIN film f ON i.film_id = f.film_id
LEFT JOIN rental r ON i.inventory_id = r.inventory_id AND r.return_date IS NULL
LEFT JOIN customer c ON r.customer_id = c.customer_id;

-- Rental performance summary
CREATE OR REPLACE VIEW v_rental_performance AS
SELECT 
    DATE(r.rental_date) as rental_date,
    COUNT(*) as total_rentals,
    SUM(CASE WHEN r.return_date IS NULL THEN 1 ELSE 0 END) as currently_rented,
    SUM(CASE WHEN r.return_date IS NOT NULL AND DATEDIFF(r.return_date, DATE_ADD(r.rental_date, INTERVAL f.rental_duration DAY)) > 0 THEN 1 ELSE 0 END) as late_returns,
    SUM(CASE WHEN r.return_date IS NOT NULL AND DATEDIFF(r.return_date, DATE_ADD(r.rental_date, INTERVAL f.rental_duration DAY)) <= 0 THEN 1 ELSE 0 END) as on_time_returns,
    ROUND(
        AVG(CASE WHEN r.return_date IS NOT NULL THEN DATEDIFF(r.return_date, DATE_ADD(r.rental_date, INTERVAL f.rental_duration DAY)) ELSE NULL END), 
        2
    ) as avg_days_late
FROM rental r
JOIN inventory i ON r.inventory_id = i.inventory_id
JOIN film f ON i.film_id = f.film_id
GROUP BY DATE(r.rental_date)
ORDER BY rental_date DESC;

-- Film popularity with late return analysis
CREATE OR REPLACE VIEW v_film_late_analysis AS
SELECT 
    f.title,
    f.rental_duration,
    f.rental_rate,
    COUNT(r.rental_id) as total_rentals,
    SUM(CASE WHEN r.return_date IS NULL THEN 1 ELSE 0 END) as currently_rented,
    SUM(CASE WHEN r.return_date IS NOT NULL AND DATEDIFF(r.return_date, DATE_ADD(r.rental_date, INTERVAL f.rental_duration DAY)) > 0 THEN 1 ELSE 0 END) as late_returns,
    ROUND(
        (SUM(CASE WHEN r.return_date IS NOT NULL AND DATEDIFF(r.return_date, DATE_ADD(r.rental_date, INTERVAL f.rental_duration DAY)) > 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(r.rental_id)), 
        2
    ) as late_return_percentage,
    ROUND(
        AVG(CASE WHEN r.return_date IS NOT NULL THEN DATEDIFF(r.return_date, DATE_ADD(r.rental_date, INTERVAL f.rental_duration DAY)) ELSE NULL END), 
        2
    ) as avg_days_late
FROM film f
JOIN inventory i ON f.film_id = i.film_id
JOIN rental r ON i.inventory_id = r.inventory_id
GROUP BY f.film_id, f.title, f.rental_duration, f.rental_rate
ORDER BY total_rentals DESC;

-- Customer behavior analysis
CREATE OR REPLACE VIEW v_customer_behavior AS
SELECT 
    c.customer_id,
    c.first_name,
    c.last_name,
    c.email,
    COUNT(r.rental_id) as total_rentals,
    SUM(CASE WHEN r.return_date IS NULL THEN 1 ELSE 0 END) as currently_rented,
    SUM(CASE WHEN r.return_date IS NOT NULL AND DATEDIFF(r.return_date, DATE_ADD(r.rental_date, INTERVAL f.rental_duration DAY)) > 0 THEN 1 ELSE 0 END) as late_returns,
    ROUND(
        (SUM(CASE WHEN r.return_date IS NOT NULL AND DATEDIFF(r.return_date, DATE_ADD(r.rental_date, INTERVAL f.rental_duration DAY)) > 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(r.rental_id)), 
        2
    ) as late_return_percentage,
    ROUND(
        AVG(CASE WHEN r.return_date IS NOT NULL THEN DATEDIFF(r.return_date, DATE_ADD(r.rental_date, INTERVAL f.rental_duration DAY)) ELSE NULL END), 
        2
    ) as avg_days_late,
    MAX(r.rental_date) as last_rental_date
FROM customer c
JOIN rental r ON c.customer_id = r.customer_id
JOIN inventory i ON r.inventory_id = i.inventory_id
JOIN film f ON i.film_id = f.film_id
GROUP BY c.customer_id, c.first_name, c.last_name, c.email
ORDER BY total_rentals DESC;

-- Store performance with late fee analysis
CREATE OR REPLACE VIEW v_store_performance AS
SELECT 
    s.store_id,
    COUNT(r.rental_id) as total_rentals,
    SUM(CASE WHEN r.return_date IS NULL THEN 1 ELSE 0 END) as currently_rented,
    SUM(CASE WHEN r.return_date IS NOT NULL AND DATEDIFF(r.return_date, DATE_ADD(r.rental_date, INTERVAL f.rental_duration DAY)) > 0 THEN 1 ELSE 0 END) as late_returns,
    ROUND(
        (SUM(CASE WHEN r.return_date IS NOT NULL AND DATEDIFF(r.return_date, DATE_ADD(r.rental_date, INTERVAL f.rental_duration DAY)) > 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(r.rental_id)), 
        2
    ) as late_return_percentage,
    ROUND(
        AVG(CASE WHEN r.return_date IS NOT NULL THEN DATEDIFF(r.return_date, DATE_ADD(r.rental_date, INTERVAL f.rental_duration DAY)) ELSE NULL END), 
        2
    ) as avg_days_late,
    COUNT(DISTINCT c.customer_id) as unique_customers
FROM store s
JOIN inventory i ON s.store_id = i.store_id
JOIN rental r ON i.inventory_id = r.inventory_id
JOIN customer c ON r.customer_id = c.customer_id
JOIN film f ON i.film_id = f.film_id
GROUP BY s.store_id
ORDER BY total_rentals DESC;

-- Daily late fee revenue potential
CREATE OR REPLACE VIEW v_daily_late_revenue AS
SELECT 
    DATE(r.rental_date) as rental_date,
    COUNT(*) as rentals_that_day,
    SUM(CASE WHEN r.return_date IS NULL THEN DATEDIFF(CURDATE(), DATE_ADD(r.rental_date, INTERVAL f.rental_duration DAY)) * 1.50 ELSE 0 END) as potential_late_revenue,
    SUM(CASE WHEN r.return_date IS NOT NULL AND DATEDIFF(r.return_date, DATE_ADD(r.rental_date, INTERVAL f.rental_duration DAY)) > 0 THEN DATEDIFF(r.return_date, DATE_ADD(r.rental_date, INTERVAL f.rental_duration DAY)) * 1.50 ELSE 0 END) as actual_late_revenue,
    SUM(CASE WHEN r.return_date IS NULL THEN DATEDIFF(CURDATE(), DATE_ADD(r.rental_date, INTERVAL f.rental_duration DAY)) * 1.50 ELSE 0 END) + 
    SUM(CASE WHEN r.return_date IS NOT NULL AND DATEDIFF(r.return_date, DATE_ADD(r.rental_date, INTERVAL f.rental_duration DAY)) > 0 THEN DATEDIFF(r.return_date, DATE_ADD(r.rental_date, INTERVAL f.rental_duration DAY)) * 1.50 ELSE 0 END) as total_late_revenue
FROM rental r
JOIN inventory i ON r.inventory_id = i.inventory_id
JOIN film f ON i.film_id = f.film_id
GROUP BY DATE(r.rental_date)
ORDER BY rental_date DESC;

-- Usage Instructions
/*
To use these views for analysis:

1. Check current late fees:
   SELECT * FROM v_late_fees WHERE rental_status = 'Overdue' ORDER BY days_overdue DESC;

2. Customer late fee summary:
   SELECT * FROM v_customer_late_fees ORDER BY total_late_fees DESC LIMIT 20;

3. Inventory status:
   SELECT * FROM v_inventory_status WHERE current_status = 'Rented';

4. Rental performance trends:
   SELECT * FROM v_rental_performance ORDER BY rental_date DESC LIMIT 30;

5. Film late return analysis:
   SELECT * FROM v_film_late_analysis ORDER BY late_return_percentage DESC;

6. Customer behavior patterns:
   SELECT * FROM v_customer_behavior WHERE late_return_percentage > 20 ORDER BY total_rentals DESC;

7. Store performance:
   SELECT * FROM v_store_performance ORDER BY late_return_percentage DESC;

8. Daily late fee revenue:
   SELECT * FROM v_daily_late_revenue ORDER BY rental_date DESC LIMIT 30;
*/