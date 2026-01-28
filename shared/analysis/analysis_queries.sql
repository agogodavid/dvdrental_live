-- DVD Rental Live Database Analysis Queries
-- Use these queries to analyze trends and data patterns

-- 1. Transaction Volume by Week and Day
SELECT 
  WEEK(rental_date) as week,
  DAYNAME(rental_date) as day_name,
  DAY(rental_date) as day,
  COUNT(*) as transactions,
  ROUND(AVG(DATEDIFF(return_date, rental_date)), 1) as avg_rental_days
FROM rental
WHERE return_date IS NOT NULL
GROUP BY WEEK(rental_date), DATE(rental_date)
ORDER BY week, DATE(rental_date);

-- 2. Customer Acquisition and Churn
SELECT 
  WEEK(create_date) as week_added,
  COUNT(DISTINCT customer_id) as new_customers,
  ROUND(COUNT(DISTINCT CASE WHEN activebool = 1 THEN customer_id END) / 
    COUNT(DISTINCT customer_id) * 100, 1) as active_percentage
FROM customer
GROUP BY WEEK(create_date)
ORDER BY week_added;

-- 3. Revenue by Week
SELECT 
  WEEK(payment_date) as week,
  COUNT(DISTINCT payment_id) as total_payments,
  ROUND(SUM(amount), 2) as total_revenue,
  ROUND(AVG(amount), 2) as avg_payment,
  COUNT(DISTINCT customer_id) as unique_customers
FROM payment
GROUP BY WEEK(payment_date)
ORDER BY week;

-- 4. Top Films by Rentals
SELECT 
  f.film_id,
  f.title,
  COUNT(r.rental_id) as total_rentals,
  ROUND(AVG(f.rental_rate), 2) as rental_rate
FROM film f
LEFT JOIN inventory i ON f.film_id = i.film_id
LEFT JOIN rental r ON i.inventory_id = r.inventory_id
GROUP BY f.film_id, f.title
ORDER BY total_rentals DESC
LIMIT 20;

-- 5. Customer Activity (Active vs Inactive)
SELECT 
  CASE 
    WHEN activebool = 1 THEN 'Active'
    ELSE 'Inactive'
  END as status,
  COUNT(*) as customer_count,
  ROUND(AVG(DATEDIFF(NOW(), create_date)), 0) as avg_days_with_company,
  COUNT(DISTINCT c.customer_id) as customers_with_rentals
FROM customer c
LEFT JOIN rental r ON c.customer_id = r.customer_id
GROUP BY activebool;

-- 6. Store Performance
SELECT 
  s.store_id,
  COUNT(DISTINCT c.customer_id) as total_customers,
  COUNT(DISTINCT r.rental_id) as total_rentals,
  ROUND(SUM(p.amount), 2) as total_revenue,
  ROUND(AVG(p.amount), 2) as avg_transaction_value
FROM store s
LEFT JOIN customer c ON s.store_id = c.store_id
LEFT JOIN inventory i ON s.store_id = i.store_id
LEFT JOIN rental r ON i.inventory_id = r.inventory_id
LEFT JOIN payment p ON r.rental_id = p.rental_id
GROUP BY s.store_id;

-- 7. Rental Return Time Analysis
SELECT 
  CASE 
    WHEN DATEDIFF(return_date, rental_date) <= 3 THEN '3 days or less'
    WHEN DATEDIFF(return_date, rental_date) <= 5 THEN '4-5 days'
    WHEN DATEDIFF(return_date, rental_date) <= 7 THEN '6-7 days'
    ELSE 'More than 7 days'
  END as rental_duration_bucket,
  COUNT(*) as count,
  ROUND(COUNT(*) / (SELECT COUNT(*) FROM rental WHERE return_date IS NOT NULL) * 100, 1) as percentage
FROM rental
WHERE return_date IS NOT NULL
GROUP BY rental_duration_bucket
ORDER BY COUNT(*) DESC;

-- 8. Spike Day Detection (days with unusually high transaction volume)
SELECT 
  DATE(rental_date) as rental_date,
  COUNT(*) as transactions,
  ROUND(COUNT(*) / (SELECT AVG(daily_count) FROM (
    SELECT COUNT(*) as daily_count FROM rental GROUP BY DATE(rental_date)
  ) t) * 100, 0) as vs_avg_percentage
FROM rental
GROUP BY DATE(rental_date)
HAVING COUNT(*) > (SELECT AVG(daily_count) * 3 FROM (
  SELECT COUNT(*) as daily_count FROM rental GROUP BY DATE(rental_date)
) t)
ORDER BY transactions DESC;

-- 9. Customer Lifetime Value Analysis
SELECT 
  c.customer_id,
  CONCAT(c.first_name, ' ', c.last_name) as customer_name,
  COUNT(r.rental_id) as total_rentals,
  COUNT(p.payment_id) as total_payments,
  ROUND(SUM(p.amount), 2) as lifetime_value,
  DATEDIFF(NOW(), c.create_date) as days_with_company,
  ROUND(SUM(p.amount) / NULLIF(DATEDIFF(NOW(), c.create_date), 0), 4) as daily_value
FROM customer c
LEFT JOIN rental r ON c.customer_id = r.customer_id
LEFT JOIN payment p ON r.rental_id = p.rental_id
WHERE c.create_date IS NOT NULL
GROUP BY c.customer_id, c.first_name, c.last_name
ORDER BY lifetime_value DESC
LIMIT 20;

-- 10. Weekly Transaction Trend (for detecting business pattern shifts)
SELECT 
  CONCAT('Week ', WEEK(rental_date)) as week,
  MIN(DATE(rental_date)) as week_start,
  MAX(DATE(rental_date)) as week_end,
  COUNT(*) as total_transactions,
  ROUND(COUNT(*) / 7, 0) as avg_daily_transactions,
  SUM(CASE WHEN DAYOFWEEK(rental_date) IN (6, 7) THEN 1 ELSE 0 END) as weekend_transactions,
  SUM(CASE WHEN DAYOFWEEK(rental_date) IN (2, 3, 4, 5, 6) THEN 1 ELSE 0 END) as weekday_transactions
FROM rental
GROUP BY WEEK(rental_date)
ORDER BY WEEK(rental_date);
