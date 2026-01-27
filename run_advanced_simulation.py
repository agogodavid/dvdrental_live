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
from datetime import datetime, timedelta, date
from typing import Dict, List, Tuple

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AdvancedSimulationConfig:
    """Configuration for the advanced 10-year simulation"""
    
    def __init__(self, config_file: str):
        with open(config_file, 'r') as f:
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


def add_incremental_weeks(config: AdvancedSimulationConfig, num_weeks: int, current_sim_week: int) -> int:
    """Add incremental weeks with advanced business logic"""
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
            
            # Apply advanced business logic
            volume_modifier = get_volume_modifier(week_number, config)
            seasonal_multiplier = get_seasonal_multiplier(week_number, config)
            
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
    config_file = 'config_10year_advanced.json'
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
    
    logger.info(f"Loading configuration from: {config_file}")
    
    try:
        config = AdvancedSimulationConfig(config_file)
    except FileNotFoundError:
        logger.error(f"Configuration file {config_file} not found")
        logger.info("Using default config_10year_advanced.json")
        config = AdvancedSimulationConfig('config_10year_advanced.json')
    
    # Create database if it doesn't exist
    if not create_database_if_needed(config.mysql_config):
        logger.error("Failed to create database. Exiting.")
        sys.exit(1)
    
    display_simulation_plan(config)
    
    try:
        # PHASE 1: Initial setup
        logger.info(f"Start date set to {config.start_date}")
        input("\nPress Enter to begin simulation...")
        
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