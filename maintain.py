#!/usr/bin/env python3
"""
Database maintenance utilities for DVD Rental Live
Includes: backup, restore, optimize, and statistics
"""

import mysql.connector
from mysql.connector import Error
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def load_config(config_file='config.json'):
    """Load configuration from JSON file"""
    with open(config_file, 'r') as f:
        return json.load(f)


class DatabaseMaintenance:
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
        except Error as e:
            logger.error(f"Connection failed: {e}")
            raise
    
    def disconnect(self):
        """Close connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
    
    def optimize_tables(self):
        """Optimize all tables"""
        logger.info("Optimizing tables...")
        try:
            tables = [
                'rental', 'payment', 'customer', 'film', 'actor',
                'film_actor', 'inventory', 'order'
            ]
            
            for table in tables:
                try:
                    self.cursor.execute(f"OPTIMIZE TABLE {table}")
                    logger.info(f"  ✓ Optimized {table}")
                except Error:
                    pass  # Table might not exist
            
            self.conn.commit()
            logger.info("Optimization complete")
        except Error as e:
            logger.error(f"Optimization failed: {e}")
    
    def analyze_tables(self):
        """Analyze table statistics"""
        logger.info("Analyzing table statistics...")
        try:
            tables = [
                'rental', 'payment', 'customer', 'film', 'actor',
                'film_actor', 'inventory', 'store', 'staff'
            ]
            
            for table in tables:
                try:
                    self.cursor.execute(f"ANALYZE TABLE {table}")
                    logger.info(f"  ✓ Analyzed {table}")
                except Error:
                    pass
            
            self.conn.commit()
            logger.info("Analysis complete")
        except Error as e:
            logger.error(f"Analysis failed: {e}")
    
    def show_statistics(self):
        """Display database statistics"""
        logger.info("\nDatabase Statistics")
        logger.info("=" * 50)
        
        try:
            tables = {
                'country': 'Countries',
                'city': 'Cities',
                'address': 'Addresses',
                'language': 'Languages',
                'category': 'Categories',
                'actor': 'Actors',
                'film': 'Films',
                'store': 'Stores',
                'staff': 'Staff',
                'customer': 'Customers',
                'inventory': 'Inventory Items',
                'rental': 'Rentals',
                'payment': 'Payments'
            }
            
            total_records = 0
            for table, label in tables.items():
                try:
                    self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = self.cursor.fetchone()[0]
                    total_records += count
                    logger.info(f"  {label:20s}: {count:>10,}")
                except Error:
                    logger.info(f"  {label:20s}: {0:>10,}")
            
            logger.info("=" * 50)
            logger.info(f"  Total Records:     {total_records:>10,}")
            
            # Get rental date range
            try:
                self.cursor.execute("""
                    SELECT MIN(rental_date), MAX(rental_date) FROM rental
                """)
                min_date, max_date = self.cursor.fetchone()
                if min_date and max_date:
                    days = (max_date - min_date).days
                    logger.info(f"  Date Range:        {min_date} to {max_date}")
                    logger.info(f"  Days of Data:      {days} days")
            except Error:
                pass
            
            # Get database size
            try:
                self.cursor.execute(f"""
                    SELECT 
                        ROUND(SUM(data_length + index_length) / 1024 / 1024, 2)
                    FROM information_schema.tables
                    WHERE table_schema = '{self.db_name}'
                """)
                size_mb = self.cursor.fetchone()[0]
                if size_mb:
                    logger.info(f"  Database Size:     {size_mb} MB")
            except Error:
                pass
            
            logger.info("=" * 50)
            
        except Error as e:
            logger.error(f"Error getting statistics: {e}")
    
    def check_data_integrity(self):
        """Check data integrity constraints"""
        logger.info("\nChecking Data Integrity")
        logger.info("=" * 50)
        
        try:
            checks = [
                ("Rentals without inventory", 
                 "SELECT COUNT(*) FROM rental WHERE inventory_id NOT IN (SELECT inventory_id FROM inventory)"),
                ("Rentals without customer",
                 "SELECT COUNT(*) FROM rental WHERE customer_id NOT IN (SELECT customer_id FROM customer)"),
                ("Rentals without staff",
                 "SELECT COUNT(*) FROM rental WHERE staff_id NOT IN (SELECT staff_id FROM staff)"),
                ("Payments without rental",
                 "SELECT COUNT(*) FROM payment WHERE rental_id NOT IN (SELECT rental_id FROM rental)"),
                ("Customers without store",
                 "SELECT COUNT(*) FROM customer WHERE store_id NOT IN (SELECT store_id FROM store)"),
                ("Inventory without film",
                 "SELECT COUNT(*) FROM inventory WHERE film_id NOT IN (SELECT film_id FROM film)"),
            ]
            
            issues_found = 0
            for check_name, query in checks:
                self.cursor.execute(query)
                count = self.cursor.fetchone()[0]
                if count > 0:
                    logger.warning(f"  ⚠ {check_name}: {count} issues")
                    issues_found += count
                else:
                    logger.info(f"  ✓ {check_name}: OK")
            
            logger.info("=" * 50)
            if issues_found == 0:
                logger.info("✓ Data integrity check passed!")
            else:
                logger.warning(f"⚠ Found {issues_found} integrity issues")
            
        except Error as e:
            logger.error(f"Error checking integrity: {e}")
    
    def show_slow_queries(self, limit: int = 10):
        """Show potential slow query patterns"""
        logger.info(f"\nPotential Slow Queries (Top {limit})")
        logger.info("=" * 50)
        
        try:
            # Tables without indexes on foreign keys
            self.cursor.execute("""
                SELECT table_name, column_name
                FROM information_schema.key_column_usage
                WHERE table_schema = %s
                AND referenced_table_name IS NOT NULL
                AND table_name NOT IN (
                    SELECT table_name FROM information_schema.statistics
                    WHERE table_schema = %s
                )
            """, (self.db_name, self.db_name))
            
            results = self.cursor.fetchall()
            if results:
                logger.info("  Consider adding indexes to these columns:")
                for table, column in results:
                    logger.info(f"    - {table}.{column}")
            else:
                logger.info("  ✓ All foreign keys are indexed")
        
        except Error as e:
            logger.error(f"Error checking indexes: {e}")
        
        logger.info("=" * 50)
    
    def backup_database(self):
        """Create database backup"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f"backup_dvdrental_{timestamp}.sql"
        
        logger.info(f"Creating backup: {backup_file}")
        
        try:
            import subprocess
            result = subprocess.run([
                'mysqldump',
                '-u', self.config['user'],
                f'-p{self.config["password"]}',
                self.db_name
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                with open(backup_file, 'w') as f:
                    f.write(result.stdout)
                
                file_size_mb = Path(backup_file).stat().st_size / 1024 / 1024
                logger.info(f"✓ Backup created successfully ({file_size_mb:.2f} MB)")
                logger.info(f"  Location: {Path(backup_file).absolute()}")
            else:
                logger.error(f"Backup failed: {result.stderr}")
        
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
    
    def show_growth_metrics(self):
        """Show business growth metrics"""
        logger.info("\nGrowth Metrics")
        logger.info("=" * 50)
        
        try:
            # Weekly transaction growth
            self.cursor.execute("""
                SELECT 
                    WEEK(rental_date) as week,
                    COUNT(*) as transactions,
                    COUNT(DISTINCT customer_id) as unique_customers
                FROM rental
                GROUP BY WEEK(rental_date)
                ORDER BY week DESC
                LIMIT 5
            """)
            
            logger.info("  Recent Weeks (Latest First):")
            for week, transactions, customers in reversed(self.cursor.fetchall()):
                logger.info(f"    Week {week}: {transactions:>5} transactions, {customers:>4} customers")
            
            # Customer growth
            self.cursor.execute("""
                SELECT 
                    WEEK(create_date) as week,
                    COUNT(*) as new_customers
                FROM customer
                GROUP BY WEEK(create_date)
                ORDER BY week DESC
                LIMIT 5
            """)
            
            logger.info("  New Customers (Latest First):")
            for week, count in reversed(self.cursor.fetchall()):
                logger.info(f"    Week {week}: {count:>3} new customers")
            
        except Error as e:
            logger.error(f"Error getting metrics: {e}")
        
        logger.info("=" * 50)


def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("""
Database Maintenance Utilities

Usage: python maintain.py <command>

Commands:
  stats      - Show database statistics
  optimize   - Optimize all tables
  analyze    - Analyze table statistics
  integrity  - Check data integrity
  slow       - Show potential slow queries
  growth     - Show business growth metrics
  backup     - Create database backup
  full       - Run all checks and optimization
        """)
        sys.exit(1)
    
    command = sys.argv[1].lower()
    config = load_config()
    
    maintenance = DatabaseMaintenance(config)
    
    try:
        maintenance.connect()
        
        if command == 'stats':
            maintenance.show_statistics()
        elif command == 'optimize':
            maintenance.optimize_tables()
        elif command == 'analyze':
            maintenance.analyze_tables()
        elif command == 'integrity':
            maintenance.check_data_integrity()
        elif command == 'slow':
            maintenance.show_slow_queries()
        elif command == 'growth':
            maintenance.show_growth_metrics()
        elif command == 'backup':
            maintenance.backup_database()
        elif command == 'full':
            maintenance.show_statistics()
            maintenance.check_data_integrity()
            maintenance.show_slow_queries()
            maintenance.show_growth_metrics()
            maintenance.optimize_tables()
            maintenance.analyze_tables()
            logger.info("\n✓ Full maintenance complete!")
        else:
            logger.error(f"Unknown command: {command}")
    
    except Exception as e:
        logger.error(f"Error: {e}")
    
    finally:
        maintenance.disconnect()


if __name__ == '__main__':
    main()
