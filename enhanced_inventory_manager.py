#!/usr/bin/env python3
"""
Enhanced Inventory Manager - Configurable inventory purchasing strategies
Implements three different inventory purchasing strategies:
1. Aggressive: High growth across all genres
2. Stable: Balanced growth with moderate diversification  
3. Seasonal: Growth focused on seasonally appropriate genres
"""

import mysql.connector
from mysql.connector import Error
import json
import logging
import random
from datetime import date, datetime, timedelta
from typing import Dict, List, Tuple

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class EnhancedInventoryManager:
    def __init__(self, mysql_config: Dict, config: Dict):
        """Initialize with MySQL configuration and strategy config"""
        self.mysql_config = mysql_config
        self.config = config
        self.conn = None
        self.cursor = None
        
        # Load strategy configuration
        self.strategy_config = config.get('inventory_purchasing', {})
        self.current_strategy = self.strategy_config.get('strategy', 'stable')
        
        logger.info(f"Using inventory purchasing strategy: {self.current_strategy}")
    
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
    
    def get_quarter_for_date(self, date_obj: date) -> str:
        """Get quarter designation for a given date"""
        quarter = (date_obj.month - 1) // 3 + 1
        return f"Q{quarter}"
    
    def get_seasonal_genre_preferences(self, date_obj: date) -> List[str]:
        """Get preferred genres for the current season"""
        quarter = self.get_quarter_for_date(date_obj)
        seasonal_prefs = self.strategy_config.get('seasonal', {}).get('seasonal_preferences', {})
        return seasonal_prefs.get(quarter, [])
    
    def get_strategy_params(self) -> Dict:
        """Get parameters for current strategy"""
        strategy_data = self.strategy_config.get(self.current_strategy, {})
        return {
            'inventory_per_film': strategy_data.get('inventory_per_film', [5, 8]),
            'diversification_factor': strategy_data.get('diversification_factor', 0.8),
            'description': strategy_data.get('description', 'Unknown strategy')
        }
    
    def get_available_genres(self) -> List[str]:
        """Get all available genres from the database"""
        try:
            self.cursor.execute("SELECT name FROM category")
            return [row[0] for row in self.cursor.fetchall()]
        except Exception as e:
            logger.warning(f"Failed to get genres: {e}")
            return ["Action", "Comedy", "Drama", "Horror", "Romance"]
    
    def get_recent_film_releases(self, date_obj: date, days_back: int = 30) -> List[int]:
        """Get film IDs released in the recent period"""
        try:
            cutoff_date = date_obj - timedelta(days=days_back)
            self.cursor.execute("""
                SELECT DISTINCT film_id FROM film_releases 
                WHERE release_date >= %s
            """, (cutoff_date,))
            return [row[0] for row in self.cursor.fetchall()]
        except Exception as e:
            logger.warning(f"Failed to get recent releases: {e}")
            return []
    
    def calculate_genre_weights(self, date_obj: date, available_genres: List[str]) -> Dict[str, float]:
        """Calculate genre weights based on strategy and season"""
        strategy_params = self.get_strategy_params()
        diversification_factor = strategy_params['diversification_factor']
        
        # Base weights - all genres equal initially
        base_weight = 1.0 / len(available_genres) if available_genres else 1.0
        
        weights = {genre: base_weight for genre in available_genres}
        
        if self.current_strategy == 'seasonal':
            # Get seasonal preferences
            seasonal_genres = self.get_seasonal_genre_preferences(date_obj)
            
            # Boost seasonal genres, reduce others
            for genre in weights:
                if genre in seasonal_genres:
                    weights[genre] *= (1.0 + diversification_factor)
                else:
                    weights[genre] *= (1.0 - diversification_factor * 0.5)
        
        elif self.current_strategy == 'aggressive':
            # Aggressive strategy: more diversification
            # Slightly boost less popular genres to encourage diversity
            for genre in weights:
                weights[genre] *= (1.0 + diversification_factor * 0.2)
        
        # Normalize weights to sum to 1
        total_weight = sum(weights.values())
        if total_weight > 0:
            weights = {genre: weight / total_weight for genre, weight in weights.items()}
        
        return weights
    
    def select_film_for_purchase(self, date_obj: date, available_genres: List[str]) -> Tuple[int, str]:
        """Select a film to purchase based on strategy and season"""
        # Get recent releases to prioritize
        recent_releases = self.get_recent_film_releases(date_obj)
        
        if recent_releases and random.random() < 0.7:  # 70% chance to buy recent releases
            # Prefer recent releases
            self.cursor.execute("""
                SELECT f.film_id, f.title, fc.category_id, c.name
                FROM film f
                JOIN film_category fc ON f.film_id = fc.film_id
                JOIN category c ON fc.category_id = c.category_id
                WHERE f.film_id IN (%s)
                ORDER BY RAND()
                LIMIT 1
            """ % ','.join(['%s'] * len(recent_releases)), recent_releases)
        else:
            # Use genre-based selection
            genre_weights = self.calculate_genre_weights(date_obj, available_genres)
            
            # Select genre based on weights
            selected_genre = random.choices(
                list(genre_weights.keys()),
                weights=list(genre_weights.values())
            )[0]
            
            # Get a film from that genre
            self.cursor.execute("""
                SELECT f.film_id, f.title
                FROM film f
                JOIN film_category fc ON f.film_id = fc.film_id
                JOIN category c ON fc.category_id = c.category_id
                WHERE c.name = %s
                ORDER BY RAND()
                LIMIT 1
            """, (selected_genre,))
        
        result = self.cursor.fetchone()
        if result:
            film_id, title = result[0], result[1]
            return film_id, title
        else:
            # Fallback: get any film
            self.cursor.execute("SELECT film_id, title FROM film ORDER BY RAND() LIMIT 1")
            result = self.cursor.fetchone()
            return result[0], result[1] if result else (None, None)
    
    def add_inventory_batch(self, quantity: int, description: str = "", date_purchased: date = None, staff_id: int = None) -> int:
        """
        Add inventory using configurable purchasing strategy
        Returns: number of inventory items added
        """
        try:
            if date_purchased is None:
                date_purchased = date.today()
            
            # Get stores and staff
            self.cursor.execute("SELECT DISTINCT store_id FROM store")
            store_ids = [row[0] for row in self.cursor.fetchall()]
            
            if staff_id is None:
                self.cursor.execute("SELECT DISTINCT staff_id FROM staff WHERE active = TRUE")
                staff_results = self.cursor.fetchall()
                if staff_results:
                    staff_ids = [row[0] for row in staff_results]
                else:
                    self.cursor.execute("SELECT DISTINCT staff_id FROM staff LIMIT 1")
                    staff_row = self.cursor.fetchone()
                    staff_ids = [staff_row[0]] if staff_row else [1]
            else:
                staff_ids = [staff_id]
            
            if not store_ids:
                logger.warning("No stores found")
                return 0
            
            # Get strategy parameters
            strategy_params = self.get_strategy_params()
            min_inventory, max_inventory = strategy_params['inventory_per_film']
            
            # Get available genres
            available_genres = self.get_available_genres()
            
            # Calculate how many films to purchase based on strategy
            # Aggressive: more films, Stable: moderate, Seasonal: fewer but targeted
            if self.current_strategy == 'aggressive':
                films_to_purchase = max(3, quantity // 6)  # Buy more films
            elif self.current_strategy == 'seasonal':
                films_to_purchase = max(2, quantity // 10)  # Buy fewer, more targeted films
            else:  # stable
                films_to_purchase = max(2, quantity // 8)  # Moderate approach
            
            logger.info(f"Strategy '{self.current_strategy}': Purchasing {films_to_purchase} films for {quantity} total items")
            logger.info(f"Description: {description}")
            
            # Purchase films and create inventory
            inventory_items = []
            purchased_films = []
            
            for _ in range(films_to_purchase):
                film_id, film_title = self.select_film_for_purchase(date_purchased, available_genres)
                
                if film_id:
                    # Determine inventory quantity for this film based on strategy
                    if self.current_strategy == 'aggressive':
                        film_quantity = random.randint(min_inventory + 2, max_inventory + 4)
                    elif self.current_strategy == 'seasonal':
                        film_quantity = random.randint(min_inventory - 1, max_inventory - 1)
                    else:  # stable
                        film_quantity = random.randint(min_inventory, max_inventory)
                    
                    # Distribute across stores
                    for _ in range(film_quantity):
                        store_id = random.choice(store_ids)
                        assigned_staff_id = random.choice(staff_ids)
                        inventory_items.append((film_id, store_id, date_purchased, assigned_staff_id))
                    
                    purchased_films.append((film_id, film_title, film_quantity))
            
            if inventory_items:
                # Insert inventory items
                self.cursor.executemany(
                    "INSERT INTO inventory (film_id, store_id, date_purchased, staff_id) VALUES (%s, %s, %s, %s)",
                    inventory_items
                )
                
                # Create inventory_purchases table if it doesn't exist
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
                
                # Get inserted inventory IDs and record purchases
                self.cursor.execute("SELECT LAST_INSERT_ID()")
                first_inventory_id = self.cursor.fetchone()[0]
                
                purchase_records = []
                for i in range(len(inventory_items)):
                    inventory_id = first_inventory_id + i
                    film_id = inventory_items[i][0]
                    staff_id = inventory_items[i][3]
                    purchase_records.append((film_id, inventory_id, staff_id, date_purchased))
                
                self.cursor.executemany("""
                    INSERT INTO inventory_purchases (film_id, inventory_id, staff_id, purchase_date)
                    VALUES (%s, %s, %s, %s)
                """, purchase_records)
                
                self.conn.commit()
                
                # Log purchase summary
                logger.info(f"✓ Added {len(inventory_items)} inventory items using '{self.current_strategy}' strategy")
                logger.info(f"  Strategy: {strategy_params['description']}")
                logger.info(f"  Films purchased:")
                for film_id, title, qty in purchased_films:
                    logger.info(f"    • {title} (ID: {film_id}) - {qty} copies")
                
                return len(inventory_items)
            else:
                logger.warning("No inventory items were created")
                return 0
                
        except Exception as e:
            logger.error(f"Failed to add inventory: {e}")
            self.conn.rollback()
            return 0


def main():
    """Test the enhanced inventory manager"""
    # Load configuration
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    mysql_config = config['mysql']
    
    # Test different strategies
    strategies = ['aggressive', 'stable', 'seasonal']
    
    for strategy in strategies:
        logger.info(f"\n{'='*60}")
        logger.info(f"Testing strategy: {strategy}")
        logger.info(f"{'='*60}")
        
        # Update strategy in config
        config['inventory_purchasing']['strategy'] = strategy
        
        manager = EnhancedInventoryManager(mysql_config, config)
        
        try:
            manager.connect()
            
            # Test adding inventory
            test_date = date(2023, 6, 15)  # Summer date
            added = manager.add_inventory_batch(
                quantity=50,
                description=f"Test batch for {strategy} strategy",
                date_purchased=test_date
            )
            
            logger.info(f"Added {added} inventory items with {strategy} strategy")
            
        except Exception as e:
            logger.error(f"Error testing {strategy}: {e}")
        finally:
            manager.disconnect()


if __name__ == '__main__':
    main()