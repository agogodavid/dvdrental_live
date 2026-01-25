#!/usr/bin/env python3
"""
Inventory Schema Migration
Adds date_purchased and staff_id columns to existing inventory tables
Safe to run multiple times - checks if columns already exist
"""

import mysql.connector
from mysql.connector import Error
import json
import logging
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def load_config(config_file='config.json'):
    """Load configuration from JSON file"""
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Config file '{config_file}' not found")
        sys.exit(1)


def migrate_inventory_table(config):
    """Migrate inventory table to add new columns"""
    
    try:
        mysql_config = config['mysql']
        conn = mysql.connector.connect(
            host=mysql_config['host'],
            user=mysql_config['user'],
            password=mysql_config['password'],
            database=mysql_config['database']
        )
        cursor = conn.cursor()
        
        logger.info("=" * 70)
        logger.info("INVENTORY TABLE MIGRATION")
        logger.info("=" * 70)
        
        # Check if date_purchased column exists
        cursor.execute("""
            SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'inventory' AND COLUMN_NAME = 'date_purchased'
        """)
        
        if cursor.fetchone():
            logger.info("✓ date_purchased column already exists")
        else:
            logger.info("Adding date_purchased column...")
            cursor.execute("""
                ALTER TABLE inventory 
                ADD COLUMN date_purchased DATE NOT NULL DEFAULT CURDATE()
            """)
            logger.info("✓ Added date_purchased column with default value of today")
        
        # Check if staff_id column exists
        cursor.execute("""
            SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'inventory' AND COLUMN_NAME = 'staff_id'
        """)
        
        if cursor.fetchone():
            logger.info("✓ staff_id column already exists")
        else:
            logger.info("Adding staff_id column...")
            
            # First get a default staff_id
            cursor.execute("SELECT MIN(staff_id) FROM staff WHERE active = TRUE")
            default_staff = cursor.fetchone()
            
            if not default_staff or not default_staff[0]:
                cursor.execute("SELECT MIN(staff_id) FROM staff")
                default_staff = cursor.fetchone()
            
            if default_staff and default_staff[0]:
                default_staff_id = default_staff[0]
                cursor.execute(f"""
                    ALTER TABLE inventory 
                    ADD COLUMN staff_id INT NOT NULL DEFAULT {default_staff_id},
                    ADD FOREIGN KEY (staff_id) REFERENCES staff(staff_id)
                """)
                logger.info(f"✓ Added staff_id column with default staff_id = {default_staff_id}")
            else:
                logger.error("No staff members found in database")
                cursor.close()
                conn.close()
                return False
        
        # Add index for date_purchased if it doesn't exist
        cursor.execute("""
            SELECT 1 FROM INFORMATION_SCHEMA.STATISTICS 
            WHERE TABLE_NAME = 'inventory' AND COLUMN_NAME = 'date_purchased'
        """)
        
        if not cursor.fetchone():
            logger.info("Adding index on date_purchased...")
            cursor.execute("""
                ALTER TABLE inventory 
                ADD INDEX idx_date_purchased (date_purchased)
            """)
            logger.info("✓ Added index on date_purchased")
        else:
            logger.info("✓ Index on date_purchased already exists")
        
        # Add index for staff_id if it doesn't exist
        cursor.execute("""
            SELECT 1 FROM INFORMATION_SCHEMA.STATISTICS 
            WHERE TABLE_NAME = 'inventory' AND COLUMN_NAME = 'staff_id' AND INDEX_NAME = 'idx_staff_id'
        """)
        
        if not cursor.fetchone():
            logger.info("Adding index on staff_id...")
            cursor.execute("""
                ALTER TABLE inventory 
                ADD INDEX idx_staff_id (staff_id)
            """)
            logger.info("✓ Added index on staff_id")
        else:
            logger.info("✓ Index on staff_id already exists")
        
        conn.commit()
        
        # Show table structure
        logger.info("\n" + "=" * 70)
        logger.info("UPDATED INVENTORY TABLE STRUCTURE")
        logger.info("=" * 70)
        
        cursor.execute("DESC inventory")
        columns = cursor.fetchall()
        for col in columns:
            logger.info(f"  • {col[0]}: {col[1]}")
        
        logger.info("\n✅ Migration completed successfully!")
        logger.info("=" * 70)
        
        cursor.close()
        conn.close()
        return True
        
    except Error as e:
        logger.error(f"Database error: {e}")
        return False
    except Exception as e:
        logger.error(f"Error: {e}")
        return False


def main():
    """Main function"""
    config = load_config()
    
    try:
        if migrate_inventory_table(config):
            logger.info("\n✓ All migrations completed successfully!")
            sys.exit(0)
        else:
            logger.error("\n✗ Migration failed")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
