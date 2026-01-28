#!/usr/bin/env python3
"""
Validation and diagnostic script for DVD Rental Live database
"""

import mysql.connector
from mysql.connector import Error
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def load_config(config_file='config.json'):
    """Load configuration from JSON file"""
    with open(config_file, 'r') as f:
        return json.load(f)


def check_mysql_connection(config):
    """Check if MySQL connection is working"""
    try:
        conn = mysql.connector.connect(
            host=config['host'],
            user=config['user'],
            password=config['password']
        )
        conn.close()
        logger.info("✓ MySQL connection successful")
        return True
    except Error as e:
        logger.error(f"✗ MySQL connection failed: {e}")
        return False


def check_database_exists(config):
    """Check if database exists"""
    try:
        conn = mysql.connector.connect(
            host=config['host'],
            user=config['user'],
            password=config['password'],
            database=config['database']
        )
        conn.close()
        logger.info(f"✓ Database '{config['database']}' exists")
        return True
    except Error as e:
        logger.warning(f"✗ Database '{config['database']}' does not exist: {e}")
        return False


def check_tables(config):
    """Check if all required tables exist"""
    required_tables = [
        'country', 'city', 'address', 'language', 'category', 'actor',
        'film', 'film_actor', 'film_category', 'store', 'staff',
        'customer', 'inventory', 'rental', 'payment'
    ]
    
    try:
        conn = mysql.connector.connect(
            host=config['host'],
            user=config['user'],
            password=config['password'],
            database=config['database']
        )
        cursor = conn.cursor()
        
        cursor.execute("SHOW TABLES")
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        missing_tables = [t for t in required_tables if t not in existing_tables]
        
        if missing_tables:
            logger.warning(f"✗ Missing tables: {', '.join(missing_tables)}")
            conn.close()
            return False
        else:
            logger.info(f"✓ All {len(required_tables)} required tables exist")
            conn.close()
            return True
    except Error as e:
        logger.error(f"✗ Error checking tables: {e}")
        return False


def get_statistics(config):
    """Get database statistics"""
    try:
        conn = mysql.connector.connect(
            host=config['host'],
            user=config['user'],
            password=config['password'],
            database=config['database']
        )
        cursor = conn.cursor()
        
        stats = {}
        
        # Count records in each table
        tables = ['country', 'city', 'actor', 'film', 'category', 'store', 
                 'staff', 'customer', 'inventory', 'rental', 'payment']
        
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                stats[table] = count
            except Error:
                stats[table] = 0
        
        # Get date range of rentals
        try:
            cursor.execute("SELECT MIN(rental_date), MAX(rental_date) FROM rental")
            min_date, max_date = cursor.fetchone()
            if min_date and max_date:
                stats['rental_date_range'] = f"{min_date} to {max_date}"
                days = (max_date - min_date).days
                stats['days_of_data'] = days
            else:
                stats['rental_date_range'] = 'No rentals'
        except Error:
            stats['rental_date_range'] = 'Error'
        
        conn.close()
        return stats
    except Error as e:
        logger.error(f"✗ Error getting statistics: {e}")
        return {}


def validate_setup():
    """Run all validation checks"""
    logger.info("="*50)
    logger.info("DVD Rental Live - Setup Validation")
    logger.info("="*50)
    
    # Load config
    try:
        config = load_config()
        logger.info(f"✓ Configuration loaded from config.json")
    except Exception as e:
        logger.error(f"✗ Failed to load config.json: {e}")
        return False
    
    mysql_config = config['mysql']
    
    logger.info("\nChecking MySQL connection...")
    if not check_mysql_connection(mysql_config):
        return False
    
    logger.info("\nChecking database...")
    if not check_database_exists(mysql_config):
        logger.info("  Run 'python generator.py' to initialize the database")
        return False
    
    logger.info("\nChecking tables...")
    if not check_tables(mysql_config):
        logger.info("  Run 'python generator.py' to create tables")
        return False
    
    logger.info("\nGetting database statistics...")
    stats = get_statistics(mysql_config)
    
    if stats:
        logger.info("\nDatabase Statistics:")
        for table, count in stats.items():
            if isinstance(count, str):
                logger.info(f"  {table}: {count}")
            else:
                logger.info(f"  {table}: {count:,} records")
    
    logger.info("\n" + "="*50)
    if stats.get('rental', 0) > 0:
        logger.info("✓ Setup is complete and database is populated!")
        logger.info("  Use 'python incremental_update.py' to add more weeks")
    else:
        logger.warning("⚠ Database exists but no rental data found")
        logger.info("  Run 'python generator.py' to populate with initial data")
    logger.info("="*50)
    
    return True


if __name__ == '__main__':
    validate_setup()
