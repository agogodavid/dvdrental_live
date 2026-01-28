-- Film Releases Tracking Schema
-- LEVEL 3: FILM RELEASE SCHEDULING
-- Tracks when films are released/added to the system
-- Used by master_simulation.py to schedule quarterly film releases

CREATE TABLE IF NOT EXISTS film_releases (
    release_id INT AUTO_INCREMENT PRIMARY KEY,
    film_id INT NOT NULL,
    release_date DATE NOT NULL,
    release_quarter VARCHAR(10),
    release_year INT,
    category VARCHAR(50),
    description VARCHAR(255),
    num_copies_added INT DEFAULT 5,
    added_by_staff_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (film_id) REFERENCES film(film_id),
    FOREIGN KEY (added_by_staff_id) REFERENCES staff(staff_id),
    
    INDEX idx_release_date (release_date),
    INDEX idx_film_id (film_id),
    INDEX idx_release_quarter (release_quarter, release_year),
    INDEX idx_category (category)
) ENGINE=InnoDB CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Inventory Purchases Tracking
-- Tracks when inventory was purchased and by whom
CREATE TABLE IF NOT EXISTS inventory_purchases (
    purchase_id INT AUTO_INCREMENT PRIMARY KEY,
    film_id INT NOT NULL,
    inventory_id INT,
    staff_id INT,
    purchase_date DATE NOT NULL,
    quantity INT DEFAULT 1,
    purchase_reason VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (film_id) REFERENCES film(film_id),
    FOREIGN KEY (inventory_id) REFERENCES inventory(inventory_id),
    FOREIGN KEY (staff_id) REFERENCES staff(staff_id),
    
    INDEX idx_film_id (film_id),
    INDEX idx_staff_id (staff_id),
    INDEX idx_purchase_date (purchase_date)
) ENGINE=InnoDB CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
