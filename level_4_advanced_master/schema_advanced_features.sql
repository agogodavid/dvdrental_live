-- Advanced Features Schema
-- LEVEL 4: ADVANCED MASTER SIMULATION
-- Includes seasonality tracking, inventory status, late fees, and customer AR
-- Used by run_advanced_simulation.py for sophisticated business modeling

-- Inventory Status Tracking
CREATE TABLE IF NOT EXISTS inventory_status (
    status_id INT AUTO_INCREMENT PRIMARY KEY,
    inventory_id INT NOT NULL,
    status ENUM('available', 'rented', 'damaged', 'missing', 'maintenance') DEFAULT 'available',
    status_date DATETIME NOT NULL,
    notes VARCHAR(255),
    checked_by_staff_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (inventory_id) REFERENCES inventory(inventory_id),
    FOREIGN KEY (checked_by_staff_id) REFERENCES staff(staff_id),
    
    INDEX idx_inventory_id (inventory_id),
    INDEX idx_status (status),
    INDEX idx_status_date (status_date)
) ENGINE=InnoDB CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Late Fees Tracking
CREATE TABLE IF NOT EXISTS late_fees (
    late_fee_id INT AUTO_INCREMENT PRIMARY KEY,
    rental_id INT NOT NULL,
    customer_id INT NOT NULL,
    inventory_id INT NOT NULL,
    days_overdue INT,
    daily_rate DECIMAL(5,2) DEFAULT 1.50,
    total_fee DECIMAL(8,2),
    fee_date DATE NOT NULL,
    paid BOOLEAN DEFAULT FALSE,
    paid_date DATETIME,
    paid_amount DECIMAL(8,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (rental_id) REFERENCES rental(rental_id),
    FOREIGN KEY (customer_id) REFERENCES customer(customer_id),
    FOREIGN KEY (inventory_id) REFERENCES inventory(inventory_id),
    
    INDEX idx_customer_id (customer_id),
    INDEX idx_fee_date (fee_date),
    INDEX idx_paid (paid),
    UNIQUE KEY uk_rental_fee (rental_id)
) ENGINE=InnoDB CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Customer Accounts Receivable
CREATE TABLE IF NOT EXISTS customer_ar (
    ar_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    total_owed DECIMAL(10,2) DEFAULT 0,
    total_paid DECIMAL(10,2) DEFAULT 0,
    ar_balance DECIMAL(10,2) DEFAULT 0,
    last_payment_date DATETIME,
    days_past_due INT,
    ar_status ENUM('current', '30_days', '60_days', '90_days_plus', 'written_off') DEFAULT 'current',
    ar_notes VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (customer_id) REFERENCES customer(customer_id),
    
    INDEX idx_customer_id (customer_id),
    INDEX idx_ar_status (ar_status),
    INDEX idx_ar_balance (ar_balance),
    UNIQUE KEY uk_customer_ar (customer_id)
) ENGINE=InnoDB CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Rental Status Tracking
CREATE TABLE IF NOT EXISTS rental_status_tracking (
    tracking_id INT AUTO_INCREMENT PRIMARY KEY,
    rental_id INT NOT NULL,
    rental_status ENUM('active', 'overdue', 'completed', 'lost', 'dispute') DEFAULT 'active',
    status_date DATETIME NOT NULL,
    days_since_rental INT,
    expected_return_date DATE,
    is_overdue BOOLEAN DEFAULT FALSE,
    overdue_days INT DEFAULT 0,
    notes VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (rental_id) REFERENCES rental(rental_id),
    
    INDEX idx_rental_id (rental_id),
    INDEX idx_rental_status (rental_status),
    INDEX idx_status_date (status_date),
    UNIQUE KEY uk_rental_tracking (rental_id)
) ENGINE=InnoDB CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Late Fees View for Business Analysis
CREATE OR REPLACE VIEW late_fees_view AS
SELECT 
    lf.late_fee_id,
    lf.rental_id,
    c.customer_id,
    CONCAT(c.first_name, ' ', c.last_name) as customer_name,
    c.email,
    i.inventory_id,
    f.title as film_title,
    r.rental_date,
    r.return_date,
    lf.days_overdue,
    lf.daily_rate,
    lf.total_fee,
    lf.fee_date,
    lf.paid,
    lf.paid_date,
    lf.paid_amount,
    (lf.total_fee - COALESCE(lf.paid_amount, 0)) as remaining_balance,
    DATEDIFF(CURDATE(), lf.fee_date) as days_since_fee,
    CASE 
        WHEN lf.paid THEN 'Paid'
        WHEN DATEDIFF(CURDATE(), lf.fee_date) > 90 THEN '90+ Days Overdue'
        WHEN DATEDIFF(CURDATE(), lf.fee_date) > 60 THEN '60-90 Days Overdue'
        WHEN DATEDIFF(CURDATE(), lf.fee_date) > 30 THEN '30-60 Days Overdue'
        ELSE 'Current'
    END as ar_aging_category
FROM late_fees lf
JOIN rental r ON lf.rental_id = r.rental_id
JOIN customer c ON lf.customer_id = c.customer_id
JOIN inventory i ON lf.inventory_id = i.inventory_id
JOIN film f ON i.film_id = f.film_id
ORDER BY lf.fee_date DESC;

-- Seasonality Adjustment Log
CREATE TABLE IF NOT EXISTS seasonality_log (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    week_number INT,
    simulation_date DATE,
    business_phase VARCHAR(50),
    volume_modifier DECIMAL(6,4),
    seasonal_multiplier DECIMAL(6,4),
    adjusted_transaction_volume INT,
    actual_transactions INT,
    notes VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_week_number (week_number),
    INDEX idx_simulation_date (simulation_date),
    INDEX idx_business_phase (business_phase)
) ENGINE=InnoDB CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
