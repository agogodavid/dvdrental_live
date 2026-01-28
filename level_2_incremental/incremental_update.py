"""
Incremental update script for DVD Rental Database
Run this script to add new weeks of transaction data

NOTE: This script automatically uses all available inventory in the database.
To add more inventory before running this, use inventory_manager.py
"""

import sys
import os
from datetime import datetime
from pathlib import Path

# Add parent directory and sibling directories to path to find generator module
script_dir = os.path.dirname(os.path.abspath(__file__))
workspace_root = os.path.dirname(script_dir)  # Go up from level_2_incremental
level_1_basic = os.path.join(workspace_root, 'level_1_basic')
if level_1_basic not in sys.path:
    sys.path.insert(0, level_1_basic)
if workspace_root not in sys.path:
    sys.path.insert(0, workspace_root)

from generator import DVDRentalDataGenerator
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def load_config(config_file='config.json', override_database=None):
    """Load configuration from JSON file with intelligent path resolution"""
    # Try to find config file in multiple locations
    script_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_root = os.path.dirname(script_dir)  # Go up from level_2_incremental
    config_paths = [
        config_file,  # Current directory
        os.path.join(script_dir, config_file),  # Same directory as script
        os.path.join(workspace_root, 'shared', 'configs', config_file),  # Shared configs
        os.path.join(workspace_root, config_file),  # Workspace root
    ]
    
    config_path = None
    for path in config_paths:
        if os.path.exists(path):
            config_path = path
            logger.debug(f"Found config at: {path}")
            break
    
    if not config_path:
        logger.error(f"Config file not found in any of: {config_paths}")
        raise FileNotFoundError(f"Cannot find {config_file}")
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    if override_database:
        config['mysql']['database'] = override_database
        logger.info(f"Database override: {override_database}")
    
    return config


def get_next_week_number(cursor) -> int:
    """Get the next week number to generate"""
    cursor.execute("""
        SELECT MAX(YEAR(rental_date) * 52 + WEEK(rental_date)) as week_num
        FROM rental
    """)
    result = cursor.fetchone()
    if result and result[0]:
        return result[0] + 1
    else:
        return 1


def add_incremental_week(config_file='config.json', num_weeks: int = 1, seasonal_drift: float = 0.0, override_database=None):
    """Add incremental weeks to the database
    
    Args:
        config_file: Path to config.json
        num_weeks: Number of weeks to add
        seasonal_drift: Percentage change in transaction volume (-100 to 100+)
                       e.g., 50 = 50% increase, -50 = 50% decrease
    """
    config = load_config(config_file, override_database)
    mysql_config = config['mysql']
    
    # Print database name being updated
    database_name = mysql_config.get('database', 'unknown')
    logger.info(f"Updating database: {database_name}")
    
    generator = DVDRentalDataGenerator(mysql_config, config.get('generation', {}))
    generator.seasonal_drift = seasonal_drift
    
    try:
        generator.connect()
        
        # Get current database status
        generator.cursor.execute("SELECT COUNT(*) FROM customer WHERE activebool = TRUE")
        active_customers = generator.cursor.fetchone()[0]
        
        # Get range of existing records
        generator.cursor.execute("SELECT MIN(rental_date), MAX(rental_date) FROM rental")
        date_range = generator.cursor.fetchone()
        
        if not date_range or not date_range[1]:
            logger.warning("No existing rentals found. Use generator.py for initial setup.")
            return
        
        first_rental, last_rental = date_range
        logger.info(f"Current record range: {first_rental} to {last_rental}")
        
        logger.info(f"Active customers: {active_customers}")
        
        # Calculate next week start (move last_rental to next Monday)
        from datetime import timedelta, datetime
        
        if isinstance(last_rental, str):
            last_rental = datetime.strptime(last_rental, '%Y-%m-%d %H:%M:%S')
        
        # Get the date part and round to next Monday
        last_date = last_rental.date() if hasattr(last_rental, 'date') else last_rental
        next_week_start = last_date + timedelta(days=1)
        next_week_start = next_week_start - timedelta(days=next_week_start.weekday())  # Move to Monday
        
        logger.info(f"Adding {num_weeks} weeks starting from {next_week_start}")
        
        # Calculate week numbers based on weeks since start of simulation
        generator.cursor.execute("SELECT MIN(rental_date) FROM rental")
        min_rental = generator.cursor.fetchone()[0]
        
        if min_rental:
            start_date = min_rental.date() if hasattr(min_rental, 'date') else min_rental
            weeks_since_start = (next_week_start - start_date).days // 7
            
            # Add new weeks
            for i in range(num_weeks):
                week_start = next_week_start + timedelta(weeks=i)
                week_number = weeks_since_start + i + 1
                logger.info(f"Generating week {week_number}...")
                generator.add_week_of_transactions(week_start, week_number)
        
        logger.info(f"Successfully added {num_weeks} weeks of transaction data")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
    finally:
        generator.disconnect()


def main():
    """Main function"""
    num_weeks = 1
    seasonal_drift = 0.0
    override_database = None
    
    # Parse arguments
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        
        if arg == '--seasonal' and i + 1 < len(sys.argv):
            try:
                seasonal_drift = float(sys.argv[i + 1])
                i += 2
            except ValueError:
                logger.error("--seasonal requires a numeric value (e.g., 50 or -50)")
                sys.exit(1)
        elif arg == '--database' and i + 1 < len(sys.argv):
            override_database = sys.argv[i + 1]
            i += 2
        else:
            try:
                num_weeks = int(arg)
                i += 1
            except ValueError:
                logger.error("Usage: python incremental_update.py [num_weeks] [--seasonal PERCENT] [--database DB_NAME]")
                logger.error("  Examples:")
                logger.error("    python incremental_update.py 4")
                logger.error("    python incremental_update.py 4 --seasonal 50")
                logger.error("    python incremental_update.py 4 --database dvdrental_group_a")
                logger.error("    python incremental_update.py 4 --seasonal -50 --database dvdrental_group_b")
                sys.exit(1)
    
    logger.info(f"Adding {num_weeks} weeks with seasonal drift: {seasonal_drift:+.1f}%")
    add_incremental_week(config_file='config.json', num_weeks=num_weeks, seasonal_drift=seasonal_drift, override_database=override_database)


if __name__ == '__main__':
    main()
