#!/usr/bin/env python3
"""
Film Releases Checker - View film releases and inventory purchases
"""

import mysql.connector
from mysql.connector import Error
import json
import logging
import sys
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def load_config(config_file='config.json'):
    """Load configuration from JSON file"""
    with open(config_file, 'r') as f:
        return json.load(f)


class FilmReleasesChecker:
    def __init__(self, config: dict, database_override: str = None):
        self.config = config['mysql']
        self.db_name = database_override or self.config['database']
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
        except Error as e:
            logger.error(f"Connection failed: {e}")
            raise
    
    def disconnect(self):
        """Close connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
    
    def show_film_releases(self):
        """Display the film_releases table"""
        logger.info("\n🎬 Film Releases Table")
        logger.info("=" * 80)
        
        try:
            # Get film releases with film details
            query = """
            SELECT 
                fr.release_id,
                fr.film_id,
                f.title,
                f.release_year,
                fr.release_quarter,
                fr.release_date,
                fr.created_at
            FROM film_releases fr
            JOIN film f ON fr.film_id = f.film_id
            ORDER BY fr.release_date, fr.release_id
            """
            
            self.cursor.execute(query)
            results = self.cursor.fetchall()
            
            if not results:
                logger.info("  No film releases found.")
                return
            
            logger.info(f"{'ID':<4} {'Film ID':<8} {'Title':<30} {'Year':<6} {'Quarter':<10} {'Release Date':<12} {'Created At'}")
            logger.info("-" * 80)
            
            for row in results:
                release_id, film_id, title, release_year, release_quarter, release_date, created_at = row
                
                # Truncate title if too long
                if len(title) > 29:
                    title = title[:26] + "..."
                
                logger.info(f"{release_id:<4} {film_id:<8} {title:<30} {release_year:<6} {release_quarter:<10} {release_date:<12} {created_at}")
            
            logger.info(f"\n  Total film releases: {len(results)}")
            
            # Show summary by quarter
            logger.info("\nReleases by Quarter:")
            logger.info("-" * 40)
            
            self.cursor.execute("""
                SELECT release_quarter, COUNT(*) as count
                FROM film_releases
                GROUP BY release_quarter
                ORDER BY release_quarter
            """)
            
            quarter_results = self.cursor.fetchall()
            for quarter, count in quarter_results:
                logger.info(f"  {quarter}: {count} films")
            
        except Error as e:
            logger.error(f"Error getting film releases: {e}")
    
    def show_inventory_purchases(self):
        """Display inventory purchases summary"""
        logger.info("\n📦 Inventory Purchases Summary")
        logger.info("=" * 80)
        
        try:
            # Show inventory purchases by month
            self.cursor.execute("""
                SELECT 
                    DATE_FORMAT(purchase_date, '%Y-%m') as month,
                    COUNT(*) as purchases,
                    COUNT(DISTINCT film_id) as unique_films,
                    COUNT(DISTINCT staff_id) as staff_involved,
                    MIN(purchase_date) as first_purchase,
                    MAX(purchase_date) as last_purchase
                FROM inventory_purchases
                GROUP BY DATE_FORMAT(purchase_date, '%Y-%m')
                ORDER BY month
            """)
            
            results = self.cursor.fetchall()
            
            if not results:
                logger.info("  No inventory purchases found.")
                return
            
            logger.info(f"{'Month':<8} {'Purchases':<10} {'Unique Films':<12} {'Staff Involved':<14} {'Date Range'}")
            logger.info("-" * 80)
            
            for month, purchases, unique_films, staff_involved, first_purchase, last_purchase in results:
                date_range = f"{first_purchase} to {last_purchase}"
                logger.info(f"{month:<8} {purchases:<10} {unique_films:<12} {staff_involved:<14} {date_range}")
            
            # Show total summary
            self.cursor.execute("SELECT COUNT(*) FROM inventory_purchases")
            total_purchases = self.cursor.fetchone()[0]
            
            self.cursor.execute("SELECT COUNT(DISTINCT film_id) FROM inventory_purchases")
            total_films = self.cursor.fetchone()[0]
            
            self.cursor.execute("SELECT COUNT(DISTINCT staff_id) FROM inventory_purchases")
            total_staff = self.cursor.fetchone()[0]
            
            logger.info(f"\n  Total Purchases: {total_purchases:,}")
            logger.info(f"  Total Films: {total_films:,}")
            logger.info(f"  Staff Involved: {total_staff}")
            
        except Error as e:
            logger.error(f"Error getting inventory purchases: {e}")
    
    def show_film_details(self):
        """Show detailed film information"""
        logger.info("\n📋 Film Details")
        logger.info("=" * 80)
        
        try:
            # Get detailed film information
            query = """
            SELECT 
                f.film_id,
                f.title,
                f.release_year,
                f.rating,
                f.length,
                f.rental_rate,
                f.replacement_cost,
                GROUP_CONCAT(c.name) as categories,
                COUNT(i.inventory_id) as inventory_count
            FROM film f
            LEFT JOIN film_category fc ON f.film_id = fc.film_id
            LEFT JOIN category c ON fc.category_id = c.category_id
            LEFT JOIN inventory i ON f.film_id = i.film_id
            WHERE f.film_id IN (SELECT film_id FROM film_releases)
            GROUP BY f.film_id
            ORDER BY f.release_year, f.title
            """
            
            self.cursor.execute(query)
            results = self.cursor.fetchall()
            
            if not results:
                logger.info("  No films found.")
                return
            
            logger.info(f"{'ID':<4} {'Title':<30} {'Year':<6} {'Rating':<6} {'Length':<6} {'Rate':<6} {'Cost':<8} {'Categories':<20} {'Inventory'}")
            logger.info("-" * 80)
            
            for row in results:
                film_id, title, release_year, rating, length, rental_rate, replacement_cost, categories, inventory_count = row
                
                # Truncate title if too long
                if len(title) > 29:
                    title = title[:26] + "..."
                
                # Truncate categories if too long
                if categories and len(categories) > 19:
                    categories = categories[:16] + "..."
                
                logger.info(f"{film_id:<4} {title:<30} {release_year:<6} {rating:<6} {length:<6} {rental_rate:<6} {replacement_cost:<8} {categories:<20} {inventory_count}")
            
            logger.info(f"\n  Total films: {len(results)}")
            
        except Error as e:
            logger.error(f"Error getting film details: {e}")
    
    def show_staff_involvement(self):
        """Show staff involvement in film releases"""
        logger.info("\n👥 Staff Involvement")
        logger.info("=" * 80)
        
        try:
            # Show staff involvement in inventory purchases
            self.cursor.execute("""
                SELECT 
                    s.staff_id,
                    CONCAT(s.first_name, ' ', s.last_name) as staff_name,
                    COUNT(DISTINCT ip.film_id) as films_involved,
                    COUNT(ip.purchase_id) as total_purchases,
                    MIN(ip.purchase_date) as first_purchase,
                    MAX(ip.purchase_date) as last_purchase
                FROM staff s
                JOIN inventory_purchases ip ON s.staff_id = ip.staff_id
                GROUP BY s.staff_id
                ORDER BY films_involved DESC, total_purchases DESC
            """)
            
            results = self.cursor.fetchall()
            
            if not results:
                logger.info("  No staff involvement found.")
                return
            
            logger.info(f"{'ID':<4} {'Name':<20} {'Films':<8} {'Purchases':<10} {'First Purchase':<15} {'Last Purchase'}")
            logger.info("-" * 80)
            
            for staff_id, staff_name, films_involved, total_purchases, first_purchase, last_purchase in results:
                logger.info(f"{staff_id:<4} {staff_name:<20} {films_involved:<8} {total_purchases:<10} {first_purchase:<15} {last_purchase}")
            
            logger.info(f"\n  Total staff involved: {len(results)}")
            
        except Error as e:
            logger.error(f"Error getting staff involvement: {e}")


def main():
    """Main function"""
    config = load_config()
    default_db = config['mysql']['database']
    
    # Ask user which database to use
    print(f"\n🎬 Film Releases Checker\n")
    print(f"Default database (from config): {default_db}")
    print("\nOptions:")
    print(f"  1) Use default database: {default_db}")
    print(f"  2) Use a different database")
    
    choice = input("\nSelect option (1 or 2): ").strip()
    
    if choice == '2':
        database_override = input("Enter database name: ").strip()
        if not database_override:
            logger.error("Database name cannot be empty")
            sys.exit(1)
        print(f"\n✓ Using database: {database_override}\n")
    else:
        database_override = None
        print(f"\n✓ Using default database: {default_db}\n")
    
    checker = FilmReleasesChecker(config, database_override)
    
    try:
        checker.connect()
        
        # Show all film release information
        checker.show_film_releases()
        checker.show_inventory_purchases()
        checker.show_film_details()
        checker.show_staff_involvement()
        
        logger.info("\n✓ Film releases check complete!")
        
    except Exception as e:
        logger.error(f"Error: {e}")
    
    finally:
        checker.disconnect()


if __name__ == '__main__':
    main()