#!/usr/bin/env python3
"""
Inventory Manager - Interactive inventory creation and management
Allows choosing different strategies for adding inventory to stores
"""

import mysql.connector
from mysql.connector import Error
import json
import logging
import sys
from datetime import datetime
from typing import Dict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def load_config(config_file='config.json'):
    """Load configuration from JSON file"""
    with open(config_file, 'r') as f:
        return json.load(f)


class InventoryManager:
    def __init__(self, config: dict):
        self.config = config['mysql']
        self.db_name = self.config['database']
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """Establish connection"""
        try:
            self.conn = mysql.connector.connect(
                host=self.config['host'],
                user=self.config['user'],
                password=self.config['password'],
                database=self.db_name
            )
            self.cursor = self.conn.cursor()
            logger.info(f"Connected to {self.db_name}")
        except Error as e:
            logger.error(f"Connection failed: {e}")
            raise
    
    def disconnect(self):
        """Close connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
    
    def show_current_inventory(self):
        """Show current inventory statistics"""
        logger.info("\n" + "=" * 70)
        logger.info("CURRENT INVENTORY STATUS")
        logger.info("=" * 70)
        
        try:
            # Total inventory
            self.cursor.execute("SELECT COUNT(*) FROM inventory")
            total_items = self.cursor.fetchone()[0]
            
            # Inventory by store
            self.cursor.execute("""
                SELECT store_id, COUNT(*) as count
                FROM inventory
                GROUP BY store_id
                ORDER BY store_id
            """)
            store_inventory = self.cursor.fetchall()
            
            # Inventory by film
            self.cursor.execute("""
                SELECT COUNT(DISTINCT film_id) as num_films,
                       MIN(copies_per_film) as min_copies,
                       MAX(copies_per_film) as max_copies,
                       AVG(copies_per_film) as avg_copies
                FROM (
                    SELECT film_id, COUNT(*) as copies_per_film
                    FROM inventory
                    GROUP BY film_id
                ) subq
            """)
            film_stats = self.cursor.fetchone()
            num_films, min_copies, max_copies, avg_copies = film_stats
            
            # Rented vs available
            self.cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN inventory_id IN (
                        SELECT DISTINCT inventory_id FROM rental WHERE return_date IS NULL
                    ) THEN 1 ELSE 0 END) as rented,
                    SUM(CASE WHEN inventory_id NOT IN (
                        SELECT DISTINCT inventory_id FROM rental WHERE return_date IS NULL
                    ) THEN 1 ELSE 0 END) as available
                FROM inventory
            """)
            self.cursor.fetchall()  # Consume subquery results
            
            self.cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN i.inventory_id IN (
                        SELECT DISTINCT inventory_id FROM rental WHERE return_date IS NULL
                    ) THEN 1 ELSE 0 END) as rented
                FROM inventory i
            """)
            result = self.cursor.fetchone()
            total, rented = result if result[1] is not None else (result[0], 0)
            available = total - rented
            
            logger.info(f"\nTotal Inventory Items: {total_items:,}")
            logger.info(f"  • Rented (checked out): {rented:,}")
            logger.info(f"  • Available: {available:,}")
            logger.info(f"\nInventory by Store:")
            for store_id, count in store_inventory:
                logger.info(f"  • Store {store_id}: {count:,} items")
            
            logger.info(f"\nInventory Distribution by Film:")
            logger.info(f"  • Number of films: {num_films:,}")
            logger.info(f"  • Min copies per film: {int(min_copies)}")
            logger.info(f"  • Max copies per film: {int(max_copies)}")
            logger.info(f"  • Avg copies per film: {avg_copies:.1f}")
            
            logger.info("=" * 70)
            return total_items, num_films
            
        except Error as e:
            logger.error(f"Error retrieving inventory: {e}")
            raise
    
    def add_fixed_quantity(self, quantity: int, date_purchased=None, staff_id=None):
        """Add fixed number of items across all films and stores"""
        logger.info(f"\n📦 Strategy: Add {quantity:,} items")
        logger.info("Distribution: Random across all films and stores")
        
        try:
            from datetime import date as date_class
            import random
            
            # Use provided date or today's date
            if date_purchased is None:
                date_purchased = date_class.today()
            
            # Get all films and stores
            self.cursor.execute("SELECT DISTINCT film_id FROM film")
            film_ids = [row[0] for row in self.cursor.fetchall()]
            
            self.cursor.execute("SELECT DISTINCT store_id FROM store")
            store_ids = [row[0] for row in self.cursor.fetchall()]
            
            # Get staff for stores or use random staff
            if staff_id is None:
                self.cursor.execute("SELECT DISTINCT staff_id FROM staff WHERE active = TRUE")
                staff_ids = [row[0] for row in self.cursor.fetchall()]
                if not staff_ids:
                    self.cursor.execute("SELECT DISTINCT staff_id FROM staff LIMIT 1")
                    staff_row = self.cursor.fetchone()
                    if staff_row:
                        staff_ids = [staff_row[0]]
                    else:
                        logger.error("No staff members found in database")
                        return 0
            else:
                staff_ids = [staff_id]
            
            if not film_ids or not store_ids:
                logger.error("No films or stores found in database")
                return 0
            
            # Create inventory items with new columns
            inventory = []
            for _ in range(quantity):
                film_id = random.choice(film_ids)
                store_id = random.choice(store_ids)
                assigned_staff_id = random.choice(staff_ids) if len(staff_ids) > 1 else staff_ids[0]
                inventory.append((film_id, store_id, date_purchased, assigned_staff_id))
            
            self.cursor.executemany(
                "INSERT INTO inventory (film_id, store_id, date_purchased, staff_id) VALUES (%s, %s, %s, %s)",
                inventory
            )
            self.conn.commit()
            logger.info(f"✓ Added {len(inventory):,} inventory items")
            logger.info(f"  • Date purchased: {date_purchased}")
            logger.info(f"  • Staff member(s): {len(set([inv[3] for inv in inventory]))} different staff")
            return len(inventory)
            
        except Error as e:
            logger.error(f"Error adding inventory: {e}")
            self.conn.rollback()
            return 0
    
    def add_percentage_growth(self, percentage: float, date_purchased=None, staff_id=None):
        """Add inventory as percentage of current inventory"""
        logger.info(f"\n📦 Strategy: Grow inventory by {percentage:+.1f}%")
        
        try:
            self.cursor.execute("SELECT COUNT(*) FROM inventory")
            current_count = self.cursor.fetchone()[0]
            
            quantity = int(current_count * percentage / 100)
            
            if quantity <= 0:
                logger.warning(f"Calculated quantity {quantity} is 0 or negative")
                return 0
            
            logger.info(f"Current inventory: {current_count:,}")
            logger.info(f"Adding {quantity:,} items ({percentage:+.1f}%)")
            
            return self.add_fixed_quantity(quantity, date_purchased, staff_id)
            
        except Error as e:
            logger.error(f"Error calculating growth: {e}")
            return 0
    
    def add_per_film_copies(self, copies: int, date_purchased=None, staff_id=None):
        """Add fixed number of copies for each film in each store"""
        logger.info(f"\n📦 Strategy: Add {copies} copies per film per store")
        
        try:
            from datetime import date as date_class
            import random
            
            # Use provided date or today's date
            if date_purchased is None:
                date_purchased = date_class.today()
            
            self.cursor.execute("SELECT DISTINCT film_id FROM film")
            film_ids = [row[0] for row in self.cursor.fetchall()]
            
            self.cursor.execute("SELECT DISTINCT store_id FROM store")
            store_ids = [row[0] for row in self.cursor.fetchall()]
            
            # Get staff for stores
            if staff_id is None:
                self.cursor.execute("SELECT DISTINCT staff_id FROM staff WHERE active = TRUE")
                staff_ids = [row[0] for row in self.cursor.fetchall()]
                if not staff_ids:
                    self.cursor.execute("SELECT DISTINCT staff_id FROM staff LIMIT 1")
                    staff_row = self.cursor.fetchone()
                    if staff_row:
                        staff_ids = [staff_row[0]]
                    else:
                        logger.error("No staff members found in database")
                        return 0
            else:
                staff_ids = [staff_id]
            
            if not film_ids or not store_ids:
                logger.error("No films or stores found")
                return 0
            
            inventory = []
            for film_id in film_ids:
                for store_id in store_ids:
                    for _ in range(copies):
                        assigned_staff_id = random.choice(staff_ids) if len(staff_ids) > 1 else staff_ids[0]
                        inventory.append((film_id, store_id, date_purchased, assigned_staff_id))
            
            self.cursor.executemany(
                "INSERT INTO inventory (film_id, store_id, date_purchased, staff_id) VALUES (%s, %s, %s, %s)",
                inventory
            )
            self.conn.commit()
            
            logger.info(f"✓ Added {len(inventory):,} inventory items")
            logger.info(f"  • {len(film_ids)} films × {len(store_ids)} stores × {copies} copies")
            logger.info(f"  • Date purchased: {date_purchased}")
            logger.info(f"  • Staff member(s): {len(set([inv[3] for inv in inventory]))} different staff")
            return len(inventory)
            
        except Error as e:
            logger.error(f"Error adding inventory: {e}")
            self.conn.rollback()
            return 0
    
    def add_popular_films_only(self, copies_per_film: int, num_films: int, date_purchased=None, staff_id=None):
        """Add copies only for most popular films"""
        logger.info(f"\n📦 Strategy: Add {copies_per_film} copies for top {num_films} popular films")
        
        try:
            from datetime import date as date_class
            import random
            
            # Use provided date or today's date
            if date_purchased is None:
                date_purchased = date_class.today()
            
            # Get most rented films
            self.cursor.execute("""
                SELECT f.film_id, COUNT(r.rental_id) as rental_count
                FROM film f
                LEFT JOIN inventory i ON f.film_id = i.film_id
                LEFT JOIN rental r ON i.inventory_id = r.inventory_id
                GROUP BY f.film_id
                ORDER BY rental_count DESC
                LIMIT %s
            """, (num_films,))
            
            popular_films = [row[0] for row in self.cursor.fetchall()]
            
            self.cursor.execute("SELECT DISTINCT store_id FROM store")
            store_ids = [row[0] for row in self.cursor.fetchall()]
            
            # Get staff for stores
            if staff_id is None:
                self.cursor.execute("SELECT DISTINCT staff_id FROM staff WHERE active = TRUE")
                staff_ids = [row[0] for row in self.cursor.fetchall()]
                if not staff_ids:
                    self.cursor.execute("SELECT DISTINCT staff_id FROM staff LIMIT 1")
                    staff_row = self.cursor.fetchone()
                    if staff_row:
                        staff_ids = [staff_row[0]]
                    else:
                        logger.error("No staff members found in database")
                        return 0
            else:
                staff_ids = [staff_id]
            
            inventory = []
            for film_id in popular_films:
                for store_id in store_ids:
                    for _ in range(copies_per_film):
                        assigned_staff_id = random.choice(staff_ids) if len(staff_ids) > 1 else staff_ids[0]
                        inventory.append((film_id, store_id, date_purchased, assigned_staff_id))
            
            self.cursor.executemany(
                "INSERT INTO inventory (film_id, store_id, date_purchased, staff_id) VALUES (%s, %s, %s, %s)",
                inventory
            )
            self.conn.commit()
            
            logger.info(f"✓ Added {len(inventory):,} inventory items")
            logger.info(f"  • Top {len(popular_films)} films × {len(store_ids)} stores × {copies_per_film} copies")
            logger.info(f"  • Date purchased: {date_purchased}")
            logger.info(f"  • Staff member(s): {len(set([inv[3] for inv in inventory]))} different staff")
            return len(inventory)
            
        except Error as e:
            logger.error(f"Error adding inventory: {e}")
            self.conn.rollback()
            return 0


def show_menu():
    """Display strategy menu"""
    print("\n" + "=" * 70)
    print("INVENTORY ADDITION STRATEGIES")
    print("=" * 70)
    print("1. Fixed Quantity     - Add X items randomly across films/stores")
    print("2. Percentage Growth  - Grow inventory by X% of current")
    print("3. Per-Film Copies    - Add X copies of each film in each store")
    print("4. Popular Films Only - Add copies only to most-rented films")
    print("0. Cancel             - Exit without making changes")
    print("=" * 70)


def get_strategy_choice():
    """Get user's strategy choice"""
    while True:
        show_menu()
        try:
            choice = input("\nSelect strategy (0-4): ").strip()
            if choice in ['0', '1', '2', '3', '4']:
                return choice
            print("❌ Invalid choice. Please enter 0-4.")
        except KeyboardInterrupt:
            print("\n\n⚠️  Cancelled by user")
            sys.exit(0)


def get_integer_input(prompt: str, min_val: int = 1, max_val: int = 1000000) -> int:
    """Get integer input from user"""
    while True:
        try:
            value = int(input(prompt).strip())
            if min_val <= value <= max_val:
                return value
            print(f"❌ Please enter a value between {min_val} and {max_val}")
        except ValueError:
            print("❌ Please enter a valid number")
        except KeyboardInterrupt:
            print("\n\n⚠️  Cancelled by user")
            sys.exit(0)


def get_float_input(prompt: str, min_val: float = -100, max_val: float = 1000) -> float:
    """Get float input from user"""
    while True:
        try:
            value = float(input(prompt).strip())
            if min_val <= value <= max_val:
                return value
            print(f"❌ Please enter a value between {min_val} and {max_val}")
        except ValueError:
            print("❌ Please enter a valid number")
        except KeyboardInterrupt:
            print("\n\n⚠️  Cancelled by user")
            sys.exit(0)


def main():
    """Main function"""
    print("\n" + "=" * 70)
    print("INVENTORY MANAGER - Add inventory to DVD Rental Database")
    print("=" * 70)
    
    config = load_config()
    manager = InventoryManager(config)
    
    try:
        manager.connect()
        
        # Show current inventory
        current_items, num_films = manager.show_current_inventory()
        
        # Get strategy choice
        choice = get_strategy_choice()
        
        if choice == '0':
            print("\n✓ Cancelled. No changes made.")
            return
        
        items_added = 0
        
        if choice == '1':
            # Fixed quantity
            quantity = get_integer_input("\nHow many items to add? ")
            items_added = manager.add_fixed_quantity(quantity)
        
        elif choice == '2':
            # Percentage growth
            percentage = get_float_input("\nGrowth percentage (e.g., 10 for +10%, -20 for -20%): ", -100, 1000)
            items_added = manager.add_percentage_growth(percentage)
        
        elif choice == '3':
            # Per-film copies
            copies = get_integer_input("\nHow many copies per film per store? ")
            items_added = manager.add_per_film_copies(copies)
        
        elif choice == '4':
            # Popular films only
            num_films_input = get_integer_input(f"\nHow many top films to add to (max {num_films})? ", 1, num_films)
            copies = get_integer_input("How many copies per film per store? ")
            items_added = manager.add_popular_films_only(copies, num_films_input)
        
        if items_added > 0:
            print(f"\n✓ Successfully added {items_added:,} inventory items!")
            print("\nUpdated Inventory:")
            manager.show_current_inventory()
        else:
            print("\n⚠️  No items were added.")
    
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)
    
    finally:
        manager.disconnect()


if __name__ == '__main__':
    main()
