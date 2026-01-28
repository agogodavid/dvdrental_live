#!/usr/bin/env python3
"""
Advanced 10-Year Simulation Runner

This script runs the advanced 10-year simulation using the config_10year_advanced.json
configuration with sophisticated business lifecycle modeling.
"""

import sys
import json
import mysql.connector
from mysql.connector import Error
import logging
import argparse
import os
from datetime import datetime, timedelta, date
from typing import Dict, List, Tuple
import random

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add parent directory and sibling directories to path to find generator module
script_dir = os.path.dirname(os.path.abspath(__file__))
workspace_root = os.path.dirname(script_dir)  # Go up from level_4_advanced_master
level_1_basic = os.path.join(workspace_root, 'level_1_basic')
level_3_film_system = os.path.join(workspace_root, 'level_3_master_simulation', 'film_system')  # Find film_generator
if level_3_film_system not in sys.path:
    sys.path.insert(0, level_3_film_system)
if level_1_basic not in sys.path:
    sys.path.insert(0, level_1_basic)
if workspace_root not in sys.path:
    sys.path.insert(0, workspace_root)


class AdvancedSimulationConfig:
    """Configuration for the advanced 10-year simulation"""
    
    def __init__(self, config_file: str):
        # Try to find config file in multiple locations
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_paths = [
            config_file,  # Current directory
            os.path.join(script_dir, config_file),  # Same directory as script
            os.path.join(script_dir, '..', 'shared', 'configs', config_file),  # Shared configs
        ]
        
        config_path = None
        for path in config_paths:
            if os.path.exists(path):
                config_path = path
                logger.info(f"Found config at: {path}")
                break
        
        if not config_path:
            logger.error(f"Config file not found in: {config_paths}")
            raise FileNotFoundError(f"Cannot find {config_file}")
        
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.mysql_config = self.config['mysql']
        self.simulation_config = self.config['simulation']
        self.generation_config = self.config['generation']
        
        # Business lifecycle phases
        self.business_phases = self.generation_config['business_lifecycle']
        self.volume_modifiers = self.generation_config['volume_modifiers']
        self.customer_segments = self.generation_config['customer_segments']
        self.reactivation_config = self.generation_config['reactivation']
        self.plateau_config = self.generation_config['plateau']
        
        # Timeline
        self.start_date = datetime.strptime(self.simulation_config['start_date'], '%Y-%m-%d').date()
        self.total_weeks = self.simulation_config['initial_weeks']
        
        # Performance settings
        self.performance = self.generation_config.get('performance', {})


def create_database_if_needed(mysql_config: dict) -> bool:
    """Create the database if it doesn't exist"""
    try:
        conn = mysql.connector.connect(
            host=mysql_config['host'],
            user=mysql_config['user'],
            password=mysql_config['password']
        )
        cursor = conn.cursor()
        
        db_name = mysql_config['database']
        
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


def get_business_phase(week_number: int, config: AdvancedSimulationConfig) -> str:
    """Determine which business phase we're in"""
    growth_end = config.business_phases['growth_phase_weeks']
    plateau_end = growth_end + config.business_phases['plateau_phase_weeks']
    decline_end = plateau_end + config.business_phases['decline_phase_weeks']
    
    if week_number <= growth_end:
        return "growth"
    elif week_number <= plateau_end:
        return "plateau"
    elif week_number <= decline_end:
        return "decline"
    else:
        return "reactivation"


def get_volume_modifier(week_number: int, config: AdvancedSimulationConfig) -> float:
    """Get the volume modifier for the current business phase"""
    phase = get_business_phase(week_number, config)
    
    if phase == "growth":
        return config.volume_modifiers['growth_factor']
    elif phase == "plateau":
        return config.volume_modifiers['plateau_factor']
    elif phase == "decline":
        return config.volume_modifiers['decline_factor']
    else:  # reactivation
        return config.volume_modifiers['reactivation_factor']


def get_seasonal_multiplier(week_number: int, config: AdvancedSimulationConfig) -> float:
    """Get seasonal multiplier based on the week"""
    current_date = config.start_date + timedelta(weeks=week_number)
    month = current_date.month
    
    # Seasonal preferences by quarter
    seasonal_volatility = config.plateau_config.get('seasonal_volatility', 0.1)
    
    # Base seasonal multipliers
    seasonal_multipliers = {
        1: 1.05,   # January: Winter entertainment
        2: 0.95,   # February: Post-holiday slump
        3: 1.05,   # March: Spring approaching
        4: 1.10,   # April: Spring refresh
        5: 1.15,   # May: Pre-summer boost
        6: 1.25,   # June: Summer begins
        7: 1.30,   # July: Peak summer
        8: 1.25,   # August: Late summer
        9: 1.15,   # September: Back to school
        10: 1.12,  # October: Fall season
        11: 1.20,  # November: Thanksgiving prep
        12: 1.25   # December: Holiday rush
    }
    
    base_multiplier = seasonal_multipliers.get(month, 1.0)
    
    # Add plateau volatility during plateau phase
    phase = get_business_phase(week_number, config)
    if phase == "plateau":
        import random
        volatility = random.uniform(-seasonal_volatility, seasonal_volatility)
        base_multiplier += volatility
    
    return base_multiplier


def run_initial_setup(config: AdvancedSimulationConfig) -> Tuple[int, int]:
    """Run initial database setup"""
    logger.info("=" * 80)
    logger.info("PHASE 1: Initial Database Setup")
    logger.info("=" * 80)
    
    try:
        from generator import DVDRentalDataGenerator
        
        generator = DVDRentalDataGenerator(config.mysql_config)
        generator.connect()
        
        logger.info(f"Initializing database for start date: {config.start_date}")
        generator.initialize_and_seed()
        
        # Get inventory count after initial setup
        generator.cursor.execute("SELECT COUNT(*) FROM inventory")
        initial_inventory = generator.cursor.fetchone()[0]
        logger.info(f"✓ Initial inventory created: {initial_inventory} items")
        
        # Generate initial rental transactions using config values
        logger.info("Generating initial rental transactions...")
        initial_weeks = config.total_weeks
        generator.generate_weeks(initial_weeks, start_date=config.start_date)
        
        # Count initial transactions
        generator.cursor.execute("SELECT COUNT(*) FROM rental")
        initial_rentals = generator.cursor.fetchone()[0]
        logger.info(f"✓ Initial transactions created: {initial_rentals} rentals over {initial_weeks} weeks")
        
        generator.disconnect()
        
        return initial_weeks, initial_inventory
        
    except Exception as e:
        logger.error(f"Failed to run initial setup: {e}")
        raise


def add_film_batch(config: AdvancedSimulationConfig, num_films: int, category_focus: str = None, description: str = "", sim_date: date = None) -> int:
    """Add new films to the database with inventory copies using the film generator"""
    try:
        from film_generator import FilmGenerator
        
        film_generator = FilmGenerator(config.mysql_config)
        film_generator.connect()
        
        # Create film_releases table if it doesn't exist
        film_generator.create_film_releases_table()
        
        # Generate films using the film generator
        films_added = film_generator.add_film_batch(
            num_films, category_focus, description, sim_date
        )
        
        film_generator.disconnect()
        return films_added
        
    except Exception as e:
        logger.error(f"Failed to add films: {e}")
        return 0


def add_inventory_batch(config: AdvancedSimulationConfig, quantity: int, description: str, date_purchased=None, staff_id=None) -> int:
    """Add inventory using inventory manager logic and track purchases"""
    try:
        from datetime import date as date_class
        
        conn = mysql.connector.connect(
            host=config.mysql_config['host'],
            user=config.mysql_config['user'],
            password=config.mysql_config['password'],
            database=config.mysql_config['database']
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
        
        # Track inventory purchases (link to staff for subsequent waves)
        cursor.execute("SELECT LAST_INSERT_ID()")
        first_inventory_id = cursor.fetchone()[0]
        
        # Record inventory purchases
        purchase_records = []
        for i in range(len(inventory)):
            inventory_id = first_inventory_id + i
            # For periodic inventory additions, link to staff member
            staff_id = inventory[i][3] if inventory[i][3] else None
            film_id = inventory[i][0]
            purchase_records.append((film_id, inventory_id, staff_id, date_purchased))
        
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
        cursor.execute(create_purchases_table_query)
        
        cursor.executemany("""
            INSERT INTO inventory_purchases (film_id, inventory_id, staff_id, purchase_date)
            VALUES (%s, %s, %s, %s)
        """, purchase_records)
        conn.commit()
        
        logger.info(f"✓ Added {quantity} inventory items - {description}")
        
        cursor.close()
        conn.close()
        return len(inventory)
        
    except Exception as e:
        logger.error(f"Failed to add inventory: {e}")
        return 0


def get_film_releases_for_week(week_num: int) -> Tuple[bool, int, str, str]:
    """Check if there's a film release scheduled for this week"""
    # Quarterly film releases for 10-year simulation - 20 films per quarter
    film_releases = [
        (0, 0, None, "Initial catalog loaded by generator"),
        (13, 20, "Action", "Q1 2002 - Action blockbusters"),
        (26, 20, "Comedy", "Q2 2002 - Comedy hits"),
        (39, 20, "Drama", "Q3 2002 - Award-worthy dramas"),
        (52, 20, "Horror", "Q4 2002 - Holiday horror"),
        (65, 20, "Romance", "Q1 2003 - Romance releases"),
        (78, 20, "Sci-Fi", "Q2 2003 - Sci-Fi adventures"),
        (91, 20, "Animation", "Q3 2003 - Animated features"),
        (104, 20, "Family", "Q4 2003 - Holiday family films"),
        (117, 20, "Thriller", "Q1 2004 - Thriller releases"),
        (130, 20, "Action", "Q2 2004 - Summer action"),
        (143, 20, "Comedy", "Q3 2004 - Comedy hits"),
        (156, 20, "Drama", "Q4 2004 - Award season dramas"),
        (169, 20, "Horror", "Q1 2005 - Horror releases"),
        (182, 20, "Romance", "Q2 2005 - Romance season"),
        (195, 20, "Sci-Fi", "Q3 2005 - Sci-Fi adventures"),
        (208, 20, "Animation", "Q4 2005 - Holiday animation"),
        (221, 20, "Family", "Q1 2006 - Family films"),
        (234, 20, "Thriller", "Q2 2006 - Thriller releases"),
        (247, 20, "Action", "Q3 2006 - Summer action"),
        (260, 20, "Comedy", "Q4 2006 - Holiday comedy"),
        (273, 20, "Drama", "Q1 2007 - Drama releases"),
        (286, 20, "Horror", "Q2 2007 - Horror season"),
        (299, 20, "Romance", "Q3 2007 - Romance films"),
        (312, 20, "Sci-Fi", "Q4 2007 - Holiday sci-fi"),
        (325, 20, "Animation", "Q1 2008 - Animation releases"),
        (338, 20, "Family", "Q2 2008 - Family season"),
        (351, 20, "Thriller", "Q3 2008 - Thriller releases"),
        (364, 20, "Action", "Q4 2008 - Holiday action"),
        (377, 20, "Comedy", "Q1 2009 - Comedy releases"),
        (390, 20, "Drama", "Q2 2009 - Drama season"),
        (403, 20, "Horror", "Q3 2009 - Horror releases"),
        (416, 20, "Romance", "Q4 2009 - Holiday romance"),
        (429, 20, "Sci-Fi", "Q1 2010 - Sci-Fi releases"),
        (442, 20, "Animation", "Q2 2010 - Animation season"),
        (455, 20, "Family", "Q3 2010 - Family releases"),
        (468, 20, "Thriller", "Q4 2010 - Holiday thriller"),
        (481, 20, "Action", "Q1 2011 - Action releases"),
        (494, 20, "Comedy", "Q2 2011 - Comedy season"),
        (507, 20, "Drama", "Q3 2011 - Drama releases"),
        (520, 20, "Horror", "Q4 2011 - Holiday horror"),
    ]
    
    for week, num_films, category_focus, desc in film_releases:
        if week == week_num:
            return True, num_films, category_focus, desc
    return False, 0, None, ""


def get_inventory_additions_for_week(week_num: int, total_weeks: int, start_date: date) -> Tuple[bool, int, str]:
    """Check if inventory should be added this week"""
    # Dynamic inventory growth based on business phase and time
    if week_num == 0:
        return False, 0, "Initial inventory created by generator"
    
    # Growth phase (first 2 years): Aggressive inventory growth
    if week_num <= 104:
        if week_num % 13 == 0 and week_num > 0:  # Every quarter after week 0
            quarter = week_num // 13
            year = start_date.year + (week_num // 52)
            return True, 50, f"Q{quarter + 1} {year} - Aggressive growth"
    
    # Plateau phase (years 3-6): Moderate growth
    elif week_num <= 312:
        if week_num % 16 == 0:  # Every 4 months
            quarter = (week_num - 104) // 16
            year = start_date.year + (104 + week_num) // 52
            return True, 30, f"Q{quarter + 1} {year} - Moderate growth"
    
    # Decline phase (years 7-8): Minimal growth
    elif week_num <= 416:
        if week_num % 20 == 0:  # Every 5 months
            quarter = (week_num - 312) // 20
            year = start_date.year + (312 + week_num) // 52
            return True, 15, f"Q{quarter + 1} {year} - Minimal growth"
    
    # Reactivation phase (years 9-10): Strategic growth
    else:
        if week_num % 12 == 0:  # Every quarter
            quarter = (week_num - 416) // 12
            year = start_date.year + (416 + week_num) // 52
            return True, 25, f"Q{quarter + 1} {year} - Strategic growth"
    
    return False, 0, ""


def add_incremental_weeks(config: AdvancedSimulationConfig, num_weeks: int, current_sim_week: int) -> int:
    """Add incremental weeks with advanced business logic including film releases and inventory growth"""
    try:
        from generator import DVDRentalDataGenerator
        
        generator = DVDRentalDataGenerator(config.mysql_config)
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
        
        # Add weeks with advanced business logic
        weeks_added = 0
        for i in range(num_weeks):
            week_start = next_week_start + timedelta(weeks=i)
            week_number = weeks_since_start + i + 1
            
            # Check for film releases
            has_films, num_films, category, film_desc = get_film_releases_for_week(week_number)
            
            if has_films and num_films > 0:
                current_date = config.start_date + timedelta(weeks=week_number)
                logger.info(f"\n🎬 Week {week_number} ({current_date}): {film_desc}")
                add_film_batch(config, num_films, category, film_desc, sim_date=current_date)
            
            # Check for inventory additions
            should_add, qty, desc = get_inventory_additions_for_week(week_number, config.total_weeks, config.start_date)
            
            if should_add and qty > 0:
                current_date = config.start_date + timedelta(weeks=week_number)
                # Get Monday of the current active rental simulation week
                generator.cursor.execute("SELECT MAX(rental_date) FROM rental")
                latest_rental_row = generator.cursor.fetchone()
                if latest_rental_row and latest_rental_row[0]:
                    latest_rental = latest_rental_row[0]
                    if isinstance(latest_rental, str):
                        latest_rental = datetime.strptime(latest_rental, '%Y-%m-%d %H:%M:%S')
                    monday_of_rental_week = latest_rental.date() - timedelta(days=latest_rental.date().weekday())
                else:
                    monday_of_rental_week = current_date
                logger.info(f"\n📦 Week {week_number} ({current_date}): {desc}")
                add_inventory_batch(config, qty, desc, date_purchased=monday_of_rental_week)
            
            # Print inventory and film counts every 10 weeks
            if week_number % 10 == 0 and week_number > 0:
                generator.cursor.execute("SELECT COUNT(*) FROM inventory")
                inventory_count = generator.cursor.fetchone()[0]
                generator.cursor.execute("SELECT COUNT(*) FROM film")
                film_count = generator.cursor.fetchone()[0]
                logger.info(f"   📊 Week {week_number}: {inventory_count} inventory items, {film_count} films")
            
            # Apply advanced business logic
            volume_modifier = get_volume_modifier(week_number, config)
            seasonal_multiplier = get_seasonal_multiplier(week_number, config)
            
            # Override seasonal multiplier if --season provided
            if args.season is not None:
                # Convert percentage to multiplier: 50% boost = 1.5x
                seasonal_multiplier = 1.0 + (args.season / 100.0)
            
            # Calculate adjusted base volume
            base_volume = config.generation_config['base_weekly_transactions']
            adjusted_volume = int(base_volume * (1 + volume_modifier) * seasonal_multiplier)
            
            # Set seasonal drift for this week
            generator.seasonal_drift = (seasonal_multiplier - 1) * 100
            
            logger.info(f"   Week {week_number}: {get_business_phase(week_number, config).title()} Phase")
            logger.info(f"   Volume: {adjusted_volume} transactions (base: {base_volume}, "
                       f"modifier: {volume_modifier:+.3f}, seasonal: {seasonal_multiplier:.2f}x)")
            
            generator.add_week_of_transactions(week_start, week_number)
            weeks_added += 1
            
            # Report progress
            overall_progress = (current_sim_week + weeks_added) / config.total_weeks * 100
            logger.info(f"   Progress: {overall_progress:.1f}% ({current_sim_week + weeks_added}/{config.total_weeks} weeks)")
            
            # Print inventory and film counts every 10 weeks
            if (current_sim_week + weeks_added) % 10 == 0:
                generator.cursor.execute("SELECT COUNT(*) FROM inventory")
                inventory_count = generator.cursor.fetchone()[0]
                generator.cursor.execute("SELECT COUNT(*) FROM film")
                film_count = generator.cursor.fetchone()[0]
                logger.info(f"   📊 Week {current_sim_week + weeks_added}: {inventory_count} inventory items, {film_count} films")
        
        generator.disconnect()
        return weeks_added
        
    except Exception as e:
        logger.error(f"Failed to add incremental weeks: {e}")
        raise


def display_simulation_plan(config: AdvancedSimulationConfig):
    """Display the simulation plan"""
    logger.info("=" * 80)
    logger.info("ADVANCED 10-YEAR SIMULATION PLAN")
    logger.info("=" * 80)
    logger.info(f"Start Date: {config.start_date}")
    logger.info(f"Duration: {config.total_weeks} weeks ({config.total_weeks // 52} years)")
    end_date = config.start_date + timedelta(weeks=config.total_weeks)
    logger.info(f"End Date: {end_date}")
    
    # Business phases
    logger.info(f"\nBusiness Lifecycle Phases:")
    growth_end = config.business_phases['growth_phase_weeks']
    plateau_end = growth_end + config.business_phases['plateau_phase_weeks']
    decline_end = plateau_end + config.business_phases['decline_phase_weeks']
    
    logger.info(f"  Growth Phase: Weeks 1-{growth_end} (Years 1-2)")
    logger.info(f"  Plateau Phase: Weeks {growth_end+1}-{plateau_end} (Years 3-6)")
    logger.info(f"  Decline Phase: Weeks {plateau_end+1}-{decline_end} (Years 7-8)")
    logger.info(f"  Reactivation Phase: Weeks {decline_end+1}-{config.total_weeks} (Years 9-10)")
    
    # Customer segments
    logger.info(f"\nCustomer Segmentation:")
    for segment, details in config.customer_segments.items():
        logger.info(f"  {segment.title()}: {details['percentage']*100:.0f}% of customers, "
                   f"{details['churn_rate']*100:.0f}% churn rate, "
                   f"{details['activity_multiplier']}x activity, "
                   f"{details['lifetime_weeks']} weeks lifetime")
    
    # Reactivation
    if config.reactivation_config['enable_reactivation']:
        logger.info(f"\nCustomer Reactivation:")
        logger.info(f"  Starts: Week {config.reactivation_config['reactivation_start_week']}")
        logger.info(f"  Probability: {config.reactivation_config['reactivation_probability']*100:.0f}%")
        logger.info(f"  Duration: {config.reactivation_config['reactivation_duration_weeks']} weeks")
    
    logger.info("=" * 80 + "\n")


def main():
    """Main simulation orchestration"""
    print("\n")
    logger.info("╔" + "═" * 78 + "╗")
    logger.info("║" + " ADVANCED 10-YEAR DVD RENTAL SIMULATION ".center(78) + "║")
    logger.info("╚" + "═" * 78 + "╝")
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Advanced DVD Rental Simulation')
    parser.add_argument('--config', type=str, default='config.json', 
                        help='Configuration file to use')
    parser.add_argument('--database', type=str, help='Database name to override config')
    parser.add_argument('--season', type=float, help='Seasonal boost percentage (e.g., 50 for 50% boost, 0 for no seasonality)')
    args = parser.parse_args()
    
    logger.info(f"Loading configuration from: {args.config}")
    
    try:
        config = AdvancedSimulationConfig(args.config)
        
        # Override database if provided via --database
        if args.database:
            config.mysql_config['database'] = args.database
            logger.info(f"Database override: {args.database}")
    except FileNotFoundError:
        logger.error(f"Configuration file {args.config} not found")
        sys.exit(1)
    
    
    # Create database if it doesn't exist
    if not create_database_if_needed(config.mysql_config):
        logger.error("Failed to create database. Exiting.")
        sys.exit(1)
    
    display_simulation_plan(config)
    
    try:
        # PHASE 1: Initial setup
        logger.info(f"Start date set to {config.start_date}")
        logger.info("Starting simulation automatically...")
        
        initial_weeks, initial_inventory = run_initial_setup(config)
        current_week = initial_weeks
        
        # PHASE 2: Incremental updates with advanced business logic
        logger.info("\n" + "=" * 80)
        logger.info("PHASE 2: Advanced Business Lifecycle Simulation")
        logger.info("=" * 80)
        
        remaining_weeks = config.total_weeks - current_week
        logger.info(f"Adding {remaining_weeks} weeks with advanced business logic...\n")
        
        batch_size = 4  # Add 4 weeks at a time for efficiency
        weeks_added = 0
        
        while weeks_added < remaining_weeks:
            # Calculate weeks to add
            weeks_to_add = min(batch_size, remaining_weeks - weeks_added)
            
            # Add weeks with advanced business logic
            current_sim_week = current_week + weeks_added
            current_date = config.start_date + timedelta(weeks=current_sim_week)
            
            logger.info(f"\n📊 Weeks {current_sim_week}-{current_sim_week + weeks_to_add - 1} "
                       f"({current_date.strftime('%b %d, %Y')} - ...)")
            
            added_weeks = add_incremental_weeks(config, weeks_to_add, current_sim_week)
            weeks_added += added_weeks
            
            progress = (weeks_added / remaining_weeks) * 100
            logger.info(f"   Progress: {progress:.1f}% ({weeks_added}/{remaining_weeks} weeks)")
        
        # PHASE 3: Summary
        logger.info("\n" + "=" * 80)
        logger.info("PHASE 3: Simulation Complete - Advanced Business Analysis")
        logger.info("=" * 80)
        
        conn = mysql.connector.connect(
            host=config.mysql_config['host'],
            user=config.mysql_config['user'],
            password=config.mysql_config['password'],
            database=config.mysql_config['database']
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
        
        # Calculate business phase statistics
        cursor.execute("""
            SELECT 
                YEAR(rental_date) as year,
                COUNT(*) as rentals,
                AVG(DATEDIFF(return_date, rental_date)) as avg_duration
            FROM rental 
            WHERE return_date IS NOT NULL
            GROUP BY YEAR(rental_date)
            ORDER BY year
        """)
        yearly_stats = cursor.fetchall()
        
        # Calculate customer segment analysis
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN COUNT(*) > 50 THEN 'Heavy Users'
                    WHEN COUNT(*) > 20 THEN 'Regular Users'
                    WHEN COUNT(*) > 5 THEN 'Occasional Users'
                    ELSE 'Light Users'
                END as user_type,
                COUNT(DISTINCT customer_id) as customer_count,
                AVG(rental_count) as avg_rentals_per_customer
            FROM (
                SELECT customer_id, COUNT(*) as rental_count
                FROM rental
                GROUP BY customer_id
            ) customer_stats
            GROUP BY user_type
            ORDER BY customer_count DESC
        """)
        user_segments = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        logger.info(f"\n✓ Total Rentals: {total_rentals:,}")
        logger.info(f"✓ Active Customers: {active_customers:,}")
        logger.info(f"✓ Total Inventory Items: {total_inventory:,}")
        logger.info(f"✓ Data Range: {min_date} to {max_date}")
        logger.info(f"✓ Currently Checked Out: {checked_out:,} items")
        logger.info(f"✓ Average Rentals per Week: {total_rentals // config.total_weeks:,}")
        
        logger.info(f"\n📊 Yearly Performance:")
        for year, rentals, avg_duration in yearly_stats:
            logger.info(f"   Year {year}: {rentals:,} rentals (avg duration: {avg_duration:.1f} days)")
        
        logger.info(f"\n👥 Customer Segments:")
        for user_type, count, avg_rentals in user_segments:
            logger.info(f"   {user_type}: {count:,} customers (avg {avg_rentals:.1f} rentals each)")
        
        logger.info("\n" + "=" * 80)
        logger.info("ADVANCED SIMULATION SUCCESSFUL!")
        logger.info("=" * 80)
        logger.info(f"\nDatabase '{config.mysql_config['database']}' contains {config.total_weeks // 52} years of")
        logger.info("sophisticated business simulation with:")
        logger.info("  • Complete business lifecycle (growth, plateau, decline, reactivation)")
        logger.info("  • Advanced customer segmentation and behavior modeling")
        logger.info("  • Realistic seasonal variations and market dynamics")
        logger.info("  • Customer churn and reactivation patterns")
        logger.info("  • Comprehensive business intelligence data")
        logger.info("\nUse the late_fees_view.sql for advanced business analysis!")
        logger.info("\n")
        
    except Exception as e:
        logger.error(f"\n❌ Simulation failed: {e}")
        logger.error("Make sure MySQL is running and configuration is correct")
        sys.exit(1)


if __name__ == '__main__':
    main()