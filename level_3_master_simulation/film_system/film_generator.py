#!/usr/bin/env python3
"""
Film Generator Module - Generates new films for quarterly releases
Uses unified_film_generator for consistent, template-based title generation
"""

import mysql.connector
from mysql.connector import Error
import random
import json
import logging
from datetime import datetime, date
from typing import Dict, List, Tuple, Optional
import os

from unified_film_generator import generate_film_title, load_templates_from_files

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load templates once on import - this provides all 16 categories
FILM_TEMPLATES = load_templates_from_files()


class FilmGenerator:
    def __init__(self, mysql_config: Dict):
        """Initialize with MySQL configuration"""
        self.mysql_config = mysql_config
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """Establish MySQL connection"""
        try:
            self.conn = mysql.connector.connect(**self.mysql_config)
            self.cursor = self.conn.cursor()
            logger.info("Connected to MySQL successfully")
        except Error as e:
            logger.error(f"Error connecting to MySQL: {e}")
            raise
    
    def disconnect(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        logger.info("Disconnected from MySQL")
    
    def create_film_releases_table(self):
        """Create the film_releases table if it doesn't exist"""
        try:
            # Create film_releases table for tracking movie market releases
            create_releases_table_query = """
            CREATE TABLE IF NOT EXISTS film_releases (
                release_id INT AUTO_INCREMENT PRIMARY KEY,
                film_id INT NOT NULL,
                release_quarter VARCHAR(10) NOT NULL,
                release_date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (film_id) REFERENCES film(film_id),
                INDEX idx_release_quarter (release_quarter),
                INDEX idx_release_date (release_date)
            ) ENGINE=InnoDB
            """
            self.cursor.execute(create_releases_table_query)
            
            # Create inventory_purchases table for tracking inventory ordering
            create_purchases_table_query = """
            CREATE TABLE IF NOT EXISTS inventory_purchases (
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
            ) ENGINE=InnoDB
            """
            self.cursor.execute(create_purchases_table_query)
            
            self.conn.commit()
            logger.info("Film releases and inventory purchases tables created/verified successfully")
        except Error as e:
            logger.error(f"Error creating film tables: {e}")
            raise
    
    def get_quarter_for_date(self, date_obj: date) -> str:
        """
        Get quarter designation for a given date
        Returns: String like "Q1 2023"
        """
        quarter = (date_obj.month - 1) // 3 + 1
        return f"Q{quarter} {date_obj.year}"
    
    def get_random_staff_member(self) -> int:
        """Get a random staff member ID"""
        try:
            self.cursor.execute("SELECT staff_id FROM staff WHERE active = TRUE LIMIT 10")
            staff_members = self.cursor.fetchall()
            if staff_members:
                return random.choice(staff_members)[0]
            else:
                # Fallback to any staff member
                self.cursor.execute("SELECT staff_id FROM staff LIMIT 1")
                result = self.cursor.fetchone()
                return result[0] if result else 1
        except Exception as e:
            logger.warning(f"Failed to get staff member: {e}")
            return 1
    
    def add_film_batch(self, num_films: int, category_focus: str = None, 
                      description: str = "", release_date: date = None, add_inventory: bool = True) -> int:
        """
        Add new films to the database with optional inventory copies and track releases
        
        Args:
            num_films: Number of films to generate
            category_focus: Focus on specific category
            description: Description of the batch
            release_date: When films are being released
            add_inventory: Whether to add inventory copies (True) or just record release (False)
        
        Returns: number of films added
        """
        try:
            # Get language_id for English
            self.cursor.execute("SELECT language_id FROM language WHERE name = 'English' LIMIT 1")
            lang_result = self.cursor.fetchone()
            language_id = lang_result[0] if lang_result else 1
            
            # First, load templates from files to get all available categories
            load_templates()
            
            # Ensure all template categories exist in the database
            for template_cat in TEMPLATES.keys():
                self.cursor.execute("SELECT category_id FROM category WHERE name = %s", (template_cat,))
                cat_result = self.cursor.fetchone()
                if not cat_result:
                    # Create category if it doesn't exist
                    logger.info(f"Creating new category from template: {template_cat}")
                    self.cursor.execute("INSERT INTO category (name) VALUES (%s)", (template_cat,))
                    self.conn.commit()
            
            # Get or create categories list
            self.cursor.execute("SELECT category_id FROM category")
            cat_results = self.cursor.fetchall()
            categories = [c[0] for c in cat_results] if cat_results else [1]
            
            # Get stores
            self.cursor.execute("SELECT store_id FROM store")
            store_results = self.cursor.fetchall()
            store_ids = [s[0] for s in store_results] if store_results else [1, 2]
            
            # Get staff members
            self.cursor.execute("SELECT staff_id FROM staff WHERE active = TRUE")
            staff_results = self.cursor.fetchall()
            staff_ids = [s[0] for s in staff_results] if staff_results else [1, 2]
            
            # Create film_releases table if it doesn't exist
            self.create_film_releases_table()
            
            # Use provided release_date or get from config
            if not release_date:
                try:
                    import json
                    with open('config.json', 'r') as f:
                        config = json.load(f)
                    start_date_str = config.get('simulation', {}).get('start_date', '2001-10-01')
                    from datetime import datetime
                    release_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                except:
                    # Final fallback
                    release_date = date(2001, 10, 1)
            
            film_date = release_date
            film_year = film_date.year
            
            films_added = 0
            
            for _ in range(num_films):
                # Use category_focus if provided, otherwise random
                if category_focus:
                    category_choice = category_focus
                else:
                    # Random from available categories in templates
                    category_choice = random.choice(list(FILM_TEMPLATES.keys()))
                
                # Generate title, description, rating using unified generator
                title, desc, rating = generate_film_title(category_choice, FILM_TEMPLATES)
                
                # Get template for this category to get length and cost ranges
                template = FILM_TEMPLATES.get(category_choice, FILM_TEMPLATES.get("Drama", {}))
                length = random.randint(template.get("length_range", (90, 120))[0], template.get("length_range", (90, 120))[1])
                cost_range = template.get("cost_range", (14, 22))
                cost = round(random.uniform(cost_range[0], cost_range[1]), 2)
                rental_rate = round(cost * 0.2, 2)  # 20% of cost as rental rate
                release_year = film_year
                
                # Insert film
                self.cursor.execute("""
                    INSERT INTO film (title, description, release_year, language_id, 
                                     rental_duration, rental_rate, length, replacement_cost, rating)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (title, desc, release_year, language_id, 3, rental_rate, length, cost, rating))
                
                film_id = self.cursor.lastrowid
                
                # Link to category
                category_id = random.choice(categories)
                self.cursor.execute("""
                    INSERT INTO film_category (film_id, category_id)
                    VALUES (%s, %s)
                """, (film_id, category_id))
                
                # Record film release to market
                release_quarter = self.get_quarter_for_date(film_date)
                self.cursor.execute("""
                    INSERT INTO film_releases (film_id, release_quarter, release_date)
                    VALUES (%s, %s, %s)
                """, (film_id, release_quarter, film_date))
                
                # Optionally add inventory copies (can be skipped for market releases)
                if add_inventory:
                    # Add inventory copies to stores
                    inventory = []
                    for store_id in store_ids:
                        # Add 5-7 copies per store for more substantial inventory growth
                        for _ in range(random.randint(5, 7)):
                            staff_id = random.choice(staff_ids) if staff_ids else 1
                            inventory.append((film_id, store_id, film_date, staff_id))
                    
                    logger.debug(f"Inserting {len(inventory)} inventory items with staff IDs: {[item[3] for item in inventory]}")
                    
                    self.cursor.executemany(
                        "INSERT INTO inventory (film_id, store_id, date_purchased, staff_id) VALUES (%s, %s, %s, %s)",
                        inventory
                    )
                    
                    # Get the inserted inventory IDs and record purchases
                    # We need to get the actual inserted IDs, not guess them
                    self.cursor.execute("SELECT LAST_INSERT_ID()")
                    first_inventory_id = self.cursor.fetchone()[0]
                    
                    # Record inventory purchases
                    purchase_records = []
                    for i in range(len(inventory)):
                        inventory_id = first_inventory_id + i
                        # For film releases, we'll link to a staff member for purchase decisions
                        staff_id = inventory[i][3] if inventory[i][3] else None
                        purchase_records.append((film_id, inventory_id, staff_id, film_date))
                    
                    self.cursor.executemany("""
                        INSERT INTO inventory_purchases (film_id, inventory_id, staff_id, purchase_date)
                        VALUES (%s, %s, %s, %s)
                    """, purchase_records)
                
                films_added += 1
            
            self.conn.commit()
            
            if add_inventory:
                logger.info(f"✓ Added {films_added} new films with inventory - {description}")
                logger.info(f"  • Category focus: {category_focus or 'Mixed'}")
                logger.info(f"  • Release quarter: {self.get_quarter_for_date(film_date)}")
                logger.info(f"  • Total inventory copies added: {films_added * len(store_ids) * 2}-{films_added * len(store_ids) * 3}")
            else:
                logger.info(f"✓ Added {films_added} films to market (film_releases) - {description}")
                logger.info(f"  • Category focus: {category_focus or 'Mixed'}")
                logger.info(f"  • Release quarter: {self.get_quarter_for_date(film_date)}")
                logger.info(f"  • Note: Not added to inventory, available for purchase decisions")
            
            return films_added
            
        except Exception as e:
            logger.error(f"Failed to add films: {e}")
            self.conn.rollback()
            return 0
    
    def generate_quarterly_films(self, quarter: str, num_films: int, 
                                category_focus: str = None) -> int:
        """
        Generate films for a specific quarter
        Args:
            quarter: Quarter designation like "Q1 2023"
            num_films: Number of films to generate
            category_focus: Optional category focus
        Returns: Number of films added
        """
        try:
            self.connect()
            
            # Parse quarter to get approximate date
            # Format: "Q1 2023"
            parts = quarter.split()
            if len(parts) == 2:
                q_num = int(parts[0][1])  # Extract number from "Q1"
                year = int(parts[1])
                
                # Map quarter to approximate month
                quarter_months = {1: 2, 2: 5, 3: 8, 4: 11}  # Middle month of each quarter
                month = quarter_months.get(q_num, 1)
                release_date = date(year, month, 15)  # Middle of the month
            else:
                release_date = date.today()
            
            description = f"Quarterly release for {quarter}"
            films_added = self.add_film_batch(
                num_films, category_focus, description, release_date
            )
            
            self.disconnect()
            return films_added
            
        except Exception as e:
            logger.error(f"Error generating quarterly films: {e}")
            if self.conn:
                self.disconnect()
            return 0


def main():
    """Main function for testing"""
    # This would typically be called from master_simulation.py
    pass


if __name__ == '__main__':
    main()
