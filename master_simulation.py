#!/usr/bin/env python3
"""
Master Simulation Script - Generate realistic 3-10 year DVD rental database

This script orchestrates the full simulation pipeline:
1. Initial database setup with starter inventory
2. Periodic inventory additions
3. Regular weekly incremental updates
4. Seasonal demand variations (summer boost, holiday season, etc.)
5. Progress tracking and statistics

Configuration can be easily modified to generate 10+ years of data by adjusting
the TOTAL_WEEKS parameter and inventory schedule.
"""

import mysql.connector
from mysql.connector import Error
import json
import logging
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# SIMULATION CONFIGURATION - MODIFY HERE FOR DIFFERENT DURATIONS
# ============================================================================

class SimulationConfig:
    """Configuration for the master simulation"""
    
    # Timeline
    START_DATE = datetime(2001, 10, 1).date()  # October 1, 2001 (Monday)
    TOTAL_WEEKS = 156  # 156 weeks = 3 years (change to 520 for 10 years)
    
    # Inventory Management
    # Format: (week_number, quantity, description)
    # First entry at week 0 is initial creation
    INVENTORY_ADDITIONS = [
        (0, 0, "Initial inventory created by generator"),  # Generator creates initial stock
        (12, 50, "Q1 2002 - Holiday season restock"),
        (26, 40, "Q2 2002 - Spring refresh"),
        (40, 60, "Q3 2002 - Summer prep"),
        (52, 50, "Q4 2002 - Holiday restock"),
        (66, 40, "Q1 2003 - Winter refresh"),
        (78, 60, "Q2 2003 - Spring collection expansion"),
        (92, 70, "Q3 2003 - Summer blockbuster prep"),
        (104, 50, "Q4 2003 - Holiday season expansion"),
        # Uncomment and extend for 10+ year simulation:
        # (118, 60, "Q1 2004 - New year expansion"),
        # (130, 50, "Q2 2004 - Spring refresh"),
        # ... continue pattern ...
    ]
    
    # Seasonal demand multipliers by month
    # 1=January, 12=December
    SEASONAL_MULTIPLIERS = {
        1: 20,    # January: Cold months, slight boost
        2: -10,   # February: Post-holiday slump
        3: 10,    # March: Spring approaching
        4: 15,    # April: Spring refresh
        5: 20,    # May: Pre-summer boost
        6: 80,    # June: Summer begins! Major boost
        7: 100,   # July: Peak summer season
        8: 90,    # August: Late summer
        9: 30,    # September: Back to school
        10: 25,   # October: Fall season
        11: 40,   # November: Thanksgiving prep
        12: 60,   # December: Holiday rush
    }


def load_config(config_file='config.json', override_database=None) -> dict:
    """Load MySQL configuration
    
    Args:
        config_file: Path to config.json file
        override_database: Optional database name to override config.json setting
    
    Returns:
        Configuration dict with optional database override applied
    """
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    # Override database name if provided
    if override_database:
        config['mysql']['database'] = override_database
        logger.info(f"Using database: {override_database} (overriding config.json)")
    
    return config


def get_seasonal_drift(date: datetime.date) -> float:
    """Get seasonal demand multiplier for given date"""
    month = date.month
    return SimulationConfig.SEASONAL_MULTIPLIERS.get(month, 0)


def week_number_for_date(date: datetime.date, start_date: datetime.date) -> int:
    """Calculate week number since start date"""
    return (date - start_date).days // 7


def create_database_if_needed(mysql_config: dict) -> bool:
    """
    Create the database if it doesn't exist
    
    Returns:
        True if database created or already exists, False on error
    """
    try:
        # Connect to MySQL without specifying database
        conn = mysql.connector.connect(
            host=mysql_config['host'],
            user=mysql_config['user'],
            password=mysql_config['password']
        )
        cursor = conn.cursor()
        
        db_name = mysql_config['database']
        
        # Check if database exists
        cursor.execute("SHOW DATABASES LIKE %s", (db_name,))
        exists = cursor.fetchone() is not None
        
        if not exists:
            logger.info(f"Creating database '{db_name}'...")
            cursor.execute(f"CREATE DATABASE `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            logger.info(f"✓ Database '{db_name}' created successfully")
        else:
            logger.info(f"Database '{db_name}' already exists, using existing database")
        
        cursor.close()
        conn.close()
        return True
        
    except Error as e:
        logger.error(f"Error creating database: {e}")
        return False


def run_initial_setup(mysql_config: dict) -> Tuple[int, int]:
    """
    Run initial database setup using generator.py
    Returns: (initial_weeks, initial_inventory_count)
    """
    logger.info("=" * 80)
    logger.info("PHASE 1: Initial Database Setup")
    logger.info("=" * 80)
    
    try:
        from generator import DVDRentalDataGenerator
        
        generator = DVDRentalDataGenerator(mysql_config)
        generator.connect()
        
        logger.info(f"Initializing database for start date: {SimulationConfig.START_DATE}")
        generator.initialize_and_seed()
        
        # Get inventory count after initial setup
        generator.cursor.execute("SELECT COUNT(*) FROM inventory")
        initial_inventory = generator.cursor.fetchone()[0]
        logger.info(f"✓ Initial inventory created: {initial_inventory} items")
        
        # Generate initial rental transactions (~12 weeks)
        logger.info("Generating initial rental transactions...")
        initial_weeks = 12
        generator.generate_weeks(initial_weeks, start_date=SimulationConfig.START_DATE)
        
        # Count initial transactions
        generator.cursor.execute("SELECT COUNT(*) FROM rental")
        initial_rentals = generator.cursor.fetchone()[0]
        logger.info(f"✓ Initial transactions created: {initial_rentals} rentals over {initial_weeks} weeks")
        
        generator.disconnect()
        
        return initial_weeks, initial_inventory
        
    except Exception as e:
        logger.error(f"Failed to run initial setup: {e}")
        raise


def add_inventory_batch(mysql_config: dict, quantity: int, description: str, date_purchased=None, staff_id=None) -> int:
    """Add inventory using inventory_manager logic"""
    try:
        import random
        from datetime import date as date_class
        
        conn = mysql.connector.connect(
            host=mysql_config['host'],
            user=mysql_config['user'],
            password=mysql_config['password'],
            database=mysql_config['database']
        )
        cursor = conn.cursor()
        
        # Use provided date or today's date
        if date_purchased is None:
            date_purchased = date_class.today()
        
        # Get all films and stores
        cursor.execute("SELECT DISTINCT film_id FROM film")
        film_ids = [row[0] for row in cursor.fetchall()]
        
        cursor.execute("SELECT DISTINCT store_id FROM store")
        store_ids = [row[0] for row in cursor.fetchall()]
        
        # Get staff if not provided
        if staff_id is None:
            cursor.execute("SELECT DISTINCT staff_id FROM staff WHERE active = TRUE")
            staff_ids = [row[0] for row in cursor.fetchall()]
            if not staff_ids:
                cursor.execute("SELECT DISTINCT staff_id FROM staff LIMIT 1")
                staff_row = cursor.fetchone()
                if staff_row:
                    staff_ids = [staff_row[0]]
                else:
                    logger.warning("No staff members found, cannot add inventory")
                    cursor.close()
                    conn.close()
                    return 0
        else:
            staff_ids = [staff_id]
        
        if not film_ids or not store_ids:
            logger.warning("No films or stores found")
            cursor.close()
            conn.close()
            return 0
        
        # Create inventory items with new columns
        inventory = []
        for _ in range(quantity):
            film_id = random.choice(film_ids)
            store_id = random.choice(store_ids)
            assigned_staff_id = random.choice(staff_ids) if len(staff_ids) > 1 else staff_ids[0]
            inventory.append((film_id, store_id, date_purchased, assigned_staff_id))
        
        cursor.executemany(
            "INSERT INTO inventory (film_id, store_id, date_purchased, staff_id) VALUES (%s, %s, %s, %s)",
            inventory
        )
        conn.commit()
        
        logger.info(f"✓ Added {quantity} inventory items - {description}")
        
        cursor.close()
        conn.close()
        return len(inventory)
        
    except Exception as e:
        logger.error(f"Failed to add inventory: {e}")
        return 0


def add_incremental_weeks(mysql_config: dict, num_weeks: int, seasonal_drift: float = 0.0) -> int:
    """
    Add incremental weeks of transactions
    Returns: number of weeks added
    """
    try:
        from generator import DVDRentalDataGenerator
        
        generator = DVDRentalDataGenerator(mysql_config)
        generator.seasonal_drift = seasonal_drift
        generator.connect()
        
        # Get current database status
        generator.cursor.execute("SELECT MAX(rental_date) FROM rental")
        last_rental_row = generator.cursor.fetchone()
        
        if not last_rental_row or not last_rental_row[0]:
            logger.warning("No existing rentals found")
            generator.disconnect()
            return 0
        
        last_rental = last_rental_row[0]
        
        # Calculate next week start
        if isinstance(last_rental, str):
            last_rental = datetime.strptime(last_rental, '%Y-%m-%d %H:%M:%S')
        
        last_date = last_rental.date() if hasattr(last_rental, 'date') else last_rental
        next_week_start = last_date + timedelta(days=1)
        next_week_start = next_week_start - timedelta(days=next_week_start.weekday())
        
        # Get week count
        generator.cursor.execute("SELECT MIN(rental_date) FROM rental")
        min_rental = generator.cursor.fetchone()[0]
        start_date = min_rental.date() if hasattr(min_rental, 'date') else min_rental
        weeks_since_start = (next_week_start - start_date).days // 7
        
        # Add weeks
        weeks_added = 0
        for i in range(num_weeks):
            week_start = next_week_start + timedelta(weeks=i)
            week_number = weeks_since_start + i + 1
            generator.add_week_of_transactions(week_start, week_number)
            weeks_added += 1
        
        generator.disconnect()
        return weeks_added
        
    except Exception as e:
        logger.error(f"Failed to add incremental weeks: {e}")
        raise


def get_inventory_additions_for_week(week_num: int) -> Tuple[bool, int, str]:
    """Check if inventory should be added this week"""
    for week, qty, desc in SimulationConfig.INVENTORY_ADDITIONS:
        if week == week_num:
            return True, qty, desc
    return False, 0, ""


def display_simulation_plan():
    """Display the simulation plan"""
    logger.info("=" * 80)
    logger.info("SIMULATION PLAN")
    logger.info("=" * 80)
    logger.info(f"Start Date: {SimulationConfig.START_DATE}")
    logger.info(f"Duration: {SimulationConfig.TOTAL_WEEKS} weeks (~{SimulationConfig.TOTAL_WEEKS / 52:.1f} years)")
    end_date = SimulationConfig.START_DATE + timedelta(weeks=SimulationConfig.TOTAL_WEEKS)
    logger.info(f"End Date: {end_date}")
    logger.info(f"\nInventory Additions Schedule:")
    for week, qty, desc in SimulationConfig.INVENTORY_ADDITIONS:
        date = SimulationConfig.START_DATE + timedelta(weeks=week)
        logger.info(f"  Week {week:3d} ({date}): +{qty:3d} items - {desc}")
    logger.info("=" * 80 + "\n")


def main():
    """Main simulation orchestration"""
    print("\n")
    logger.info("╔" + "═" * 78 + "╗")
    logger.info("║" + " MASTER DVD RENTAL SIMULATION - 3 Year Data Generation ".center(78) + "║")
    logger.info("╚" + "═" * 78 + "╝")
    
    # Parse command-line arguments
    override_database = None
    if len(sys.argv) > 1:
        override_database = sys.argv[1]
        logger.info(f"Database override: {override_database}")
    
    config = load_config(override_database=override_database)
    mysql_config = config['mysql']
    
    # Create database if it doesn't exist (required for CLI overrides)
    if not create_database_if_needed(mysql_config):
        logger.error("Failed to create database. Exiting.")
        sys.exit(1)
    
    display_simulation_plan()
    
    try:
        # PHASE 1: Initial setup
        logger.info(f"Start date set to {SimulationConfig.START_DATE}")
        input("\nPress Enter to begin simulation...")
        
        initial_weeks, initial_inventory = run_initial_setup(mysql_config)
        current_week = initial_weeks
        
        # PHASE 2: Incremental updates with seasonal variations
        logger.info("\n" + "=" * 80)
        logger.info("PHASE 2: Incremental Weekly Updates with Seasonal Variations")
        logger.info("=" * 80)
        
        remaining_weeks = SimulationConfig.TOTAL_WEEKS - current_week
        logger.info(f"Adding {remaining_weeks} weeks of transactions...\n")
        
        batch_size = 4  # Add 4 weeks at a time for efficiency
        weeks_added = 0
        total_inventory_added = 0
        
        while weeks_added < remaining_weeks:
            # Check for inventory additions
            current_sim_week = current_week + weeks_added
            should_add, qty, desc = get_inventory_additions_for_week(current_sim_week)
            
            if should_add and qty > 0:
                current_date = SimulationConfig.START_DATE + timedelta(weeks=current_sim_week)
                logger.info(f"\n📦 Week {current_sim_week} ({current_date}): {desc}")
                added = add_inventory_batch(mysql_config, qty, desc)
                total_inventory_added += added
            
            # Calculate weeks to add
            weeks_to_add = min(batch_size, remaining_weeks - weeks_added)
            
            # Get seasonal drift for the middle of this batch
            batch_middle_week = current_sim_week + weeks_to_add // 2
            batch_middle_date = SimulationConfig.START_DATE + timedelta(weeks=batch_middle_week)
            seasonal_drift = get_seasonal_drift(batch_middle_date)
            
            # Add weeks
            current_date = SimulationConfig.START_DATE + timedelta(weeks=current_sim_week)
            logger.info(f"\n📊 Weeks {current_sim_week}-{current_sim_week + weeks_to_add - 1} "
                       f"({current_date.strftime('%b %d, %Y')} - ...)")
            logger.info(f"   Seasonal drift: {seasonal_drift:+.0f}% "
                       f"(month: {batch_middle_date.strftime('%B')})")
            
            added_weeks = add_incremental_weeks(mysql_config, weeks_to_add, seasonal_drift)
            weeks_added += added_weeks
            
            progress = (weeks_added / remaining_weeks) * 100
            logger.info(f"   Progress: {progress:.1f}% ({weeks_added}/{remaining_weeks} weeks)")
        
        # PHASE 3: Summary
        logger.info("\n" + "=" * 80)
        logger.info("PHASE 3: Simulation Complete - Database Summary")
        logger.info("=" * 80)
        
        conn = mysql.connector.connect(
            host=mysql_config['host'],
            user=mysql_config['user'],
            password=mysql_config['password'],
            database=mysql_config['database']
        )
        cursor = conn.cursor()
        
        # Get statistics
        cursor.execute("SELECT COUNT(*) FROM rental")
        total_rentals = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT customer_id) FROM customer WHERE activebool = TRUE")
        active_customers = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM inventory")
        total_inventory = cursor.fetchone()[0]
        
        cursor.execute("SELECT MIN(rental_date), MAX(rental_date) FROM rental")
        date_range = cursor.fetchone()
        min_date, max_date = date_range
        
        cursor.execute("""
            SELECT COUNT(*) FROM rental 
            WHERE return_date IS NULL
        """)
        checked_out = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        logger.info(f"\n✓ Total Rentals: {total_rentals:,}")
        logger.info(f"✓ Active Customers: {active_customers:,}")
        logger.info(f"✓ Total Inventory Items: {total_inventory:,} "
                   f"(+{total_inventory_added:,} added during simulation)")
        logger.info(f"✓ Data Range: {min_date} to {max_date}")
        logger.info(f"✓ Currently Checked Out: {checked_out:,} items")
        logger.info(f"✓ Average Rentals per Week: {total_rentals // SimulationConfig.TOTAL_WEEKS:,}")
        
        logger.info("\n" + "=" * 80)
        logger.info("SIMULATION SUCCESSFUL!")
        logger.info("=" * 80)
        logger.info(f"\nDatabase '{mysql_config['database']}' is ready with {SimulationConfig.TOTAL_WEEKS // 52:.1f} years of realistic transaction data.")
        logger.info("\nTo extend simulation to 10 years:")
        logger.info("  1. Set TOTAL_WEEKS = 520 in SimulationConfig")
        logger.info("  2. Add more entries to INVENTORY_ADDITIONS (extend the pattern)")
        logger.info(f"  3. Run: python master_simulation.py {mysql_config['database']}")
        logger.info("\n")
        
    except Exception as e:
        logger.error(f"\n❌ Simulation failed: {e}")
        logger.error("Make sure MySQL is running and config.json is set up correctly")
        sys.exit(1)


if __name__ == '__main__':
    main()
