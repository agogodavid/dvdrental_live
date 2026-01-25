"""
Incremental update script for DVD Rental Database
Run this script to add new weeks of transaction data
"""

import sys
from datetime import datetime
from generator import DVDRentalDataGenerator
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def load_config(config_file='config.json'):
    """Load configuration from JSON file"""
    with open(config_file, 'r') as f:
        return json.load(f)


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


def add_incremental_week(config_file='config.json', num_weeks: int = 1):
    """Add incremental weeks to the database"""
    config = load_config(config_file)
    mysql_config = config['mysql']
    
    generator = DVDRentalDataGenerator(mysql_config)
    
    try:
        generator.connect()
        
        # Get current database status
        generator.cursor.execute("SELECT COUNT(*) FROM customer WHERE activebool = TRUE")
        active_customers = generator.cursor.fetchone()[0]
        
        generator.cursor.execute("SELECT MAX(rental_date) FROM rental")
        last_rental = generator.cursor.fetchone()[0]
        
        if last_rental:
            logger.info(f"Last rental date: {last_rental}")
            next_week_start = last_rental.date() + __import__('datetime').timedelta(days=1)
            next_week_start = next_week_start - __import__('datetime').timedelta(
                days=next_week_start.weekday()
            )
        else:
            logger.warning("No existing rentals found. Use generator.py for initial setup.")
            return
        
        logger.info(f"Adding {num_weeks} weeks starting from {next_week_start}")
        logger.info(f"Current active customers: {active_customers}")
        
        # Generate the new weeks
        from datetime import timedelta
        for i in range(num_weeks):
            week_start = next_week_start + timedelta(weeks=i)
            # Calculate week number based on weeks since start
            generator.cursor.execute("SELECT MIN(rental_date) FROM rental")
            min_date = generator.cursor.fetchone()[0]
            if min_date:
                weeks_elapsed = (week_start - min_date.date()).days // 7
                generator.add_week_of_transactions(week_start, weeks_elapsed + 1)
        
        logger.info(f"Successfully added {num_weeks} weeks of transaction data")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
    finally:
        generator.disconnect()


def main():
    """Main function"""
    num_weeks = 1
    if len(sys.argv) > 1:
        try:
            num_weeks = int(sys.argv[1])
        except ValueError:
            logger.error("Usage: python incremental_update.py [num_weeks]")
            sys.exit(1)
    
    add_incremental_week(num_weeks=num_weeks)


if __name__ == '__main__':
    main()
