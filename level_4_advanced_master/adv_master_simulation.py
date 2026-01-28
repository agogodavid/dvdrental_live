#!/usr/bin/env python3
"""
Level 4 - Advanced Master Simulation (10-Year Business Lifecycle)

This is the DEFINITIVE tool for generating a complete 10-year DVD rental database with:
  • Complete business lifecycle modeling (growth, plateau, decline, reactivation)
  • Advanced customer segmentation and churn modeling  
  • Late fees and accounts receivable (AR) tracking
  • Inventory status management (available/rented/damaged/missing)
  • Realistic seasonal variations and market dynamics
  • Film releases and inventory purchasing strategies
  • Comprehensive business intelligence analytics

ORGANIZATIONAL NARRATIVE:
=========================

Level 1 (Basic):
  - Creates simple starter database with base schema
  - No sophisticated business logic
  - Used for learning SQL fundamentals

Level 2 (Incremental):
  - Adds weeks incrementally to existing database
  - Simple growth multipliers
  - Good for extending data gradually

Level 3 (Master Simulation):
  - Full multi-year simulation with film releases
  - Inventory purchasing strategies  
  - Seasonal demand variations
  - Film generator integration
  - Good foundation but missing advanced business features

Level 4 (Advanced Master - THIS FILE):
  - Everything from Level 3 PLUS:
  - Complete business lifecycle with 4 distinct phases
  - Customer segmentation (Super Loyal, Loyal, Average, Occasional)
  - Customer churn and reactivation modeling
  - Late fees calculation ($1.50/day default)
  - Accounts receivable (AR) tracking with aging (30/60/90+ days)
  - Inventory status tracking (available/rented/damaged/missing)
  - Advanced performance optimizations
  - Configuration-driven feature flags
  
USAGE:
======
  Generate 10 years of data in dvdrental_10year_advanced database:
    python level_4_advanced_master/master_simulation.py
  
  Use different database:
    python level_4_advanced_master/master_simulation.py --database my_dvdrental_10year
  
  Override seasonal multipliers:
    python level_4_advanced_master/master_simulation.py --season 50  # 50% boost
  
CONFIG:
=======
  Default: config_10year_advanced.json
  - 520 weeks (10 years) of data
  - Advanced features enabled by default
  - Can disable individual features via enable flags

OUTPUT:
=======
  Complete database with 10 years of realistic business data including:
    • ~200,000+ rental transactions
    • Customer lifecycle patterns (acquisitions, churn, reactivation)
    • Late fees and AR aging for overdue rentals
    • Inventory growth and status tracking
    • Film releases aligned with market trends
    • Seasonal variations in rental patterns
"""

import mysql.connector
from mysql.connector import Error
import json
import logging
import sys
import argparse
import os
from datetime import datetime, timedelta, date
from typing import Dict, List, Tuple
import random

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add parent directory and sibling directories to path
script_dir = os.path.dirname(os.path.abspath(__file__))
workspace_root = os.path.dirname(script_dir)
level_1_basic = os.path.join(workspace_root, 'level_1_basic')
level_3_film_system = os.path.join(workspace_root, 'level_3_master_simulation', 'film_system')
if level_3_film_system not in sys.path:
    sys.path.insert(0, level_3_film_system)
if level_1_basic not in sys.path:
    sys.path.insert(0, level_1_basic)
if workspace_root not in sys.path:
    sys.path.insert(0, workspace_root)


# ============================================================================
# ADVANCED CONFIGURATION CLASS
# ============================================================================

class AdvancedSimulationConfig:
    """
    Configuration for Level 4 Advanced Simulation
    
    Loads from config_10year_advanced.json which contains:
    - mysql: Database connection settings
    - simulation: Timeline and date settings  
    - generation: Customer segments, business lifecycle, advanced features
    - inventory_purchasing: Inventory growth strategies
    """
    
    def __init__(self, config_file: str):
        # Try to find config file in multiple locations
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_paths = [
            config_file,
            os.path.join(script_dir, config_file),
            os.path.join(script_dir, '..', 'shared', 'configs', config_file),
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
        
        # Extract main sections
        self.mysql_config = self.config['mysql']
        self.simulation_config = self.config['simulation']
        self.generation_config = self.config['generation']
        self.inventory_config = self.config.get('inventory_purchasing', {})
        
        # Business lifecycle phases
        self.business_phases = self.generation_config.get('business_lifecycle', {
            'growth_phase_weeks': 104,
            'plateau_phase_weeks': 208,
            'decline_phase_weeks': 104,
            'reactivation_phase_weeks': 104
        })
        
        # Volume modifiers for each phase
        self.volume_modifiers = self.generation_config.get('volume_modifiers', {
            'growth_factor': 0.025,
            'plateau_factor': 0.0,
            'decline_factor': -0.005,
            'reactivation_factor': 0.015
        })
        
        # Customer segmentation
        self.customer_segments = self.generation_config.get('customer_segments', {})
        
        # Reactivation settings
        self.reactivation_config = self.generation_config.get('reactivation', {
            'enable_reactivation': False
        })
        
        # Plateau configuration
        self.plateau_config = self.generation_config.get('plateau', {
            'start_week': 104,
            'duration_weeks': 208,
            'plateau_multiplier': 1.0,
            'seasonal_volatility': 0.1
        })
        
        # Advanced features (Level 4 specific)
        self.advanced_features = self.generation_config.get('advanced_features', {})
        
        # Timeline
        self.start_date = datetime.strptime(self.simulation_config['start_date'], '%Y-%m-%d').date()
        self.total_weeks = self.simulation_config['initial_weeks']
        
        # Performance settings
        self.performance = self.generation_config.get('performance', {})
        
        # Film releases schedule (quarterly releases by category)
        self.film_releases = self._generate_film_release_schedule()
        
        # Seasonal multipliers by month
        self.seasonal_multipliers = {
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
    
    def _generate_film_release_schedule(self) -> List[Tuple[int, int, str, str]]:
        """Generate comprehensive 10-year film release schedule"""
        releases = []
        categories = ["Action", "Comedy", "Drama", "Horror", "Romance", "Sci-Fi", 
                     "Animation", "Family", "Thriller"]
        
        # Generate quarterly releases for 10 years (520 weeks / 13 weeks per quarter = 40 quarters)
        for quarter in range(40):
            week = quarter * 13
            if week > 0:  # Skip week 0 (handled by initial setup)
                category = categories[quarter % len(categories)]
                year = 2002 + (quarter // 4)
                q_num = (quarter % 4) + 1
                releases.append((week, 20, category, f"Q{q_num} {year} - {category} releases"))
        
        return releases


# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

def create_database_if_needed(mysql_config: dict) -> bool:
    """Create the database if it doesn't exist"""
    try:
        conn = mysql.connector.connect(
            host=mysql_config['host'],
            user=mysql_config['user'],
            password=mysql_config['password']
        )
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(f"SHOW DATABASES LIKE '{mysql_config['database']}'")
        if cursor.fetchone():
            logger.info(f"Database '{mysql_config['database']}' already exists, using existing database")
            cursor.close()
            conn.close()
            return True
        
        # Create database
        cursor.execute(
            f"CREATE DATABASE {mysql_config['database']} "
            f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
        logger.info(f"Database '{mysql_config['database']}' created successfully")
        
        cursor.close()
        conn.close()
        return True
        
    except Error as e:
        logger.error(f"Error creating database: {e}")
        return False


def run_initial_setup(config: AdvancedSimulationConfig) -> Tuple[int, int]:
    """
    Run initial database setup
    
    Returns:
        Tuple of (weeks_added, initial_inventory_count)
    """
    logger.info("=" * 80)
    logger.info("PHASE 1: Initial Database Setup")
    logger.info("=" * 80)
    
    try:
        conn = mysql.connector.connect(
            host=config.mysql_config['host'],
            user=config.mysql_config['user'],
            password=config.mysql_config['password']
        )
        logger.info("Connected to MySQL successfully")
        
        # Initialize database
        from generator import DVDRentalDataGenerator
        
        logger.info(f"Initializing database for start date: {config.start_date}")
        generator = DVDRentalDataGenerator(config.mysql_config)
        generator.initialize_database(config.start_date)
        
        logger.info("Database initialized and seeded successfully")
        
        # Check initial inventory
        conn = mysql.connector.connect(
            host=config.mysql_config['host'],
            user=config.mysql_config['user'],
            password=config.mysql_config['password'],
            database=config.mysql_config['database']
        )
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM inventory")
        initial_inventory = cursor.fetchone()[0]
        logger.info(f"✓ Initial inventory created: {initial_inventory} items")
        cursor.close()
        conn.close()
        
        # Generate initial rental transactions (first few weeks)
        logger.info("Generating initial rental transactions...")
        initial_weeks = 30  # Start with 30 weeks
        
        for week in range(initial_weeks):
            week_start = config.start_date - timedelta(weeks=initial_weeks - week - 1)
            logger.info(f"Adding transactions for week {week + 1} starting {week_start}")
            
            # Calculate volume with growth and seasonality
            base_volume = config.generation_config['base_weekly_transactions']
            growth_multiplier = 1.0 + (config.volume_modifiers['growth_factor'] * (week + 1))
            
            month = week_start.month
            seasonal_pct = config.seasonal_multipliers.get(month, 0)
            seasonal_multiplier = 1.0 + (seasonal_pct / 100.0)
            
            expected_volume = int(base_volume * growth_multiplier * seasonal_multiplier)
            
            logger.info(f"Base volume: {base_volume}, Growth: {growth_multiplier:.2f}x, "
                       f"Seasonal: {seasonal_multiplier:.2f}x ({seasonal_pct:+.1f}%), "
                       f"Total expected: {expected_volume}")
            
            generator = DVDRentalDataGenerator(config.mysql_config)
            generator.connect()
            added = generator.add_week_of_transactions(week_start, week + 1)
            generator.disconnect()
            
            logger.info(f"Added {added} transactions for week {week + 1}")
        
        return initial_weeks, initial_inventory
        
    except Exception as e:
        logger.error(f"Initial setup failed: {e}")
        raise


# ============================================================================
# FILM RELEASES AND INVENTORY MANAGEMENT
# ============================================================================

def get_film_releases_for_week(config: AdvancedSimulationConfig, week_num: int) -> Tuple[bool, int, str, str]:
    """Check if films should be released this week"""
    for week, num_films, category_focus, desc in config.film_releases:
        if week == week_num:
            return True, num_films, category_focus, desc
    return False, 0, None, ""


def get_inventory_additions_for_week(config: AdvancedSimulationConfig, week_num: int) -> Tuple[bool, int, str]:
    """
    Determine if inventory should be added this week based on business phase
    
    Dynamic inventory growth aligned with business lifecycle:
    - Growth Phase (Years 1-2): Aggressive quarterly additions
    - Plateau Phase (Years 3-6): Moderate growth every 4 months
    - Decline Phase (Years 7-8): Minimal growth every 5 months  
    - Reactivation Phase (Years 9-10): Strategic quarterly additions
    """
    if week_num == 0:
        return False, 0, "Initial inventory created by generator"
    
    # Growth phase (first 2 years): Aggressive inventory growth
    if week_num <= 104:
        if week_num % 13 == 0 and week_num > 0:  # Every quarter
            quarter = week_num // 13
            year = config.start_date.year + (week_num // 52)
            return True, 50, f"Q{quarter + 1} {year} - Aggressive growth phase"
    
    # Plateau phase (years 3-6): Moderate growth
    elif week_num <= 312:
        if week_num % 16 == 0:  # Every 4 months
            quarter = (week_num - 104) // 16
            year = config.start_date.year + (week_num // 52)
            return True, 30, f"Q{quarter + 1} {year} - Plateau maintenance"
    
    # Decline phase (years 7-8): Minimal growth
    elif week_num <= 416:
        if week_num % 20 == 0:  # Every 5 months
            quarter = (week_num - 312) // 20
            year = config.start_date.year + (week_num // 52)
            return True, 15, f"Q{quarter + 1} {year} - Decline phase"
    
    # Reactivation phase (years 9-10): Strategic growth
    else:
        if week_num % 12 == 0:  # Every quarter
            quarter = (week_num - 416) // 12
            year = config.start_date.year + (week_num // 52)
            return True, 25, f"Q{quarter + 1} {year} - Reactivation growth"
    
    return False, 0, ""


def add_film_batch(config: AdvancedSimulationConfig, num_films: int, category_focus: str, 
                   description: str, sim_date: date, add_inventory: bool = True) -> int:
    """Add a batch of new films to the database"""
    try:
        from film_generator import FilmGenerator
        
        conn = mysql.connector.connect(
            host=config.mysql_config['host'],
            user=config.mysql_config['user'],
            password=config.mysql_config['password'],
            database=config.mysql_config['database']
        )
        
        film_gen = FilmGenerator(conn)
        added = film_gen.add_films(num_films, category_focus, add_inventory)
        
        conn.close()
        return added
        
    except Exception as e:
        logger.warning(f"Could not add films: {e}")
        return 0


def add_inventory_batch(config: AdvancedSimulationConfig, quantity: int, 
                       description: str, date_purchased: date) -> int:
    """Add inventory for existing films"""
    try:
        from enhanced_inventory_manager import EnhancedInventoryManager
        
        conn = mysql.connector.connect(
            host=config.mysql_config['host'],
            user=config.mysql_config['user'],
            password=config.mysql_config['password'],
            database=config.mysql_config['database']
        )
        
        inv_mgr = EnhancedInventoryManager(conn)
        added = inv_mgr.add_inventory(quantity, date_purchased, description)
        
        conn.close()
        return added
        
    except Exception as e:
        logger.warning(f"Could not add inventory: {e}")
        return 0


# ============================================================================
# BUSINESS LOGIC - PHASES AND MODIFIERS
# ============================================================================

def get_business_phase(week_num: int, config: AdvancedSimulationConfig) -> str:
    """Determine current business phase"""
    growth_end = config.business_phases['growth_phase_weeks']
    plateau_end = growth_end + config.business_phases['plateau_phase_weeks']
    decline_end = plateau_end + config.business_phases['decline_phase_weeks']
    
    if week_num <= growth_end:
        return "growth"
    elif week_num <= plateau_end:
        return "plateau"
    elif week_num <= decline_end:
        return "decline"
    else:
        return "reactivation"


def get_volume_modifier(week_num: int, config: AdvancedSimulationConfig) -> float:
    """Calculate volume modifier based on business phase and week"""
    phase = get_business_phase(week_num, config)
    
    if phase == "growth":
        return config.volume_modifiers['growth_factor'] * week_num
    elif phase == "plateau":
        return config.volume_modifiers['plateau_factor']
    elif phase == "decline":
        weeks_in_decline = week_num - (config.business_phases['growth_phase_weeks'] + 
                                       config.business_phases['plateau_phase_weeks'])
        return config.volume_modifiers['decline_factor'] * weeks_in_decline
    else:  # reactivation
        weeks_in_reactivation = week_num - (config.business_phases['growth_phase_weeks'] + 
                                            config.business_phases['plateau_phase_weeks'] +
                                            config.business_phases['decline_phase_weeks'])
        return config.volume_modifiers['reactivation_factor'] * weeks_in_reactivation


def get_seasonal_multiplier(week_num: int, config: AdvancedSimulationConfig, 
                           override_season: float = None) -> float:
    """Calculate seasonal demand multiplier"""
    if override_season is not None:
        # Override with user-specified value
        return 1.0 + (override_season / 100.0)
    
    # Calculate date for this week
    week_date = config.start_date + timedelta(weeks=week_num)
    month = week_date.month
    
    # Get base seasonal percentage
    seasonal_pct = config.seasonal_multipliers.get(month, 0)
    
    # Add volatility if in advanced features
    if config.advanced_features.get('enable_seasonality', False):
        volatility = config.advanced_features.get('seasonality', {}).get('volatility', 0.05)
        seasonal_pct += random.uniform(-volatility * 100, volatility * 100)
    
    return 1.0 + (seasonal_pct / 100.0)


def get_seasonal_drift(sim_date: date, config: AdvancedSimulationConfig) -> float:
    """Get seasonal drift percentage for a given date"""
    month = sim_date.month
    return config.seasonal_multipliers.get(month, 0)


# ============================================================================
# ADVANCED FEATURES - LATE FEES, AR, INVENTORY STATUS
# ============================================================================

def process_late_fees(config: AdvancedSimulationConfig, simulation_date: date = None) -> int:
    """
    Calculate and record late fees for overdue rentals
    
    Level 4 Feature: Tracks rentals that exceed rental_duration and calculates
    daily late fees (default $1.50/day). Creates late_fees table records.
    """
    if not config.advanced_features.get('enable_late_fees', False):
        return 0
    
    try:
        conn = mysql.connector.connect(
            host=config.mysql_config['host'],
            user=config.mysql_config['user'],
            password=config.mysql_config['password'],
            database=config.mysql_config['database']
        )
        cursor = conn.cursor()
        
        if simulation_date is None:
            simulation_date = date.today()
        
        late_fee_config = config.advanced_features['late_fees']
        daily_rate = late_fee_config['daily_rate']
        
        # Find rentals that are overdue and don't have late fees yet
        cursor.execute("""
            SELECT r.rental_id, r.customer_id, r.inventory_id, r.rental_date, r.return_date,
                   f.rental_duration
            FROM rental r
            INNER JOIN inventory i ON r.inventory_id = i.inventory_id
            INNER JOIN film f ON i.film_id = f.film_id
            LEFT JOIN late_fees lf ON r.rental_id = lf.rental_id
            WHERE r.return_date IS NULL 
            AND DATEDIFF(%s, r.rental_date) > f.rental_duration + 1
            AND lf.rental_id IS NULL
            LIMIT 1000
        """, (simulation_date,))
        
        overdue_rentals = cursor.fetchall()
        late_fees_records = []
        
        for rental_id, customer_id, inventory_id, rental_date, _, rental_duration in overdue_rentals:
            days_overdue = (simulation_date - rental_date.date()).days - rental_duration
            if days_overdue > 0:
                total_fee = days_overdue * daily_rate
                late_fees_records.append((
                    rental_id, customer_id, inventory_id, days_overdue, 
                    daily_rate, total_fee, simulation_date, False, None, None
                ))
        
        if late_fees_records:
            cursor.executemany("""
                INSERT INTO late_fees 
                (rental_id, customer_id, inventory_id, days_overdue, daily_rate, total_fee, 
                 fee_date, paid, paid_date, paid_amount)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, late_fees_records)
            conn.commit()
            logger.debug(f"  Late fees recorded: {len(late_fees_records)}")
        
        cursor.close()
        conn.close()
        return len(late_fees_records)
        
    except Exception as e:
        logger.debug(f"Late fees processing error: {e}")
        return 0


def update_customer_ar(config: AdvancedSimulationConfig, simulation_date: date = None) -> int:
    """
    Update customer accounts receivable (AR) balances
    
    Level 4 Feature: Maintains customer_ar table with total_owed, ar_balance,
    days_past_due, and ar_status (current/30_days/60_days/90_days_plus).
    """
    if not config.advanced_features.get('enable_ar_tracking', False):
        return 0
    
    try:
        conn = mysql.connector.connect(
            host=config.mysql_config['host'],
            user=config.mysql_config['user'],
            password=config.mysql_config['password'],
            database=config.mysql_config['database']
        )
        cursor = conn.cursor()
        
        if simulation_date is None:
            simulation_date = date.today()
        
        # Create customer_ar table if doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customer_ar (
                ar_id INT AUTO_INCREMENT PRIMARY KEY,
                customer_id INT NOT NULL UNIQUE,
                total_owed DECIMAL(10,2) DEFAULT 0,
                total_paid DECIMAL(10,2) DEFAULT 0,
                ar_balance DECIMAL(10,2) DEFAULT 0,
                last_payment_date DATETIME,
                days_past_due INT,
                ar_status ENUM('current', '30_days', '60_days', '90_days_plus') DEFAULT 'current',
                ar_notes VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customer(customer_id)
            ) ENGINE=InnoDB
        """)
        
        # Insert new customers
        cursor.execute("""
            INSERT INTO customer_ar (customer_id, total_owed, ar_balance)
            SELECT DISTINCT c.customer_id, 0, 0 FROM customer c
            LEFT JOIN customer_ar ca ON c.customer_id = ca.customer_id
            WHERE ca.ar_id IS NULL
            LIMIT 5000
        """)
        
        # Update balances based on late fees
        cursor.execute("""
            UPDATE customer_ar ca
            SET 
                total_owed = COALESCE((
                    SELECT COALESCE(SUM(total_fee), 0)
                    FROM late_fees lf
                    WHERE lf.customer_id = ca.customer_id AND lf.paid = FALSE
                ), 0),
                ar_balance = COALESCE((
                    SELECT COALESCE(SUM(total_fee), 0)
                    FROM late_fees lf
                    WHERE lf.customer_id = ca.customer_id AND lf.paid = FALSE
                ), 0),
                days_past_due = COALESCE((
                    SELECT MAX(days_overdue)
                    FROM late_fees lf
                    WHERE lf.customer_id = ca.customer_id AND lf.paid = FALSE
                ), 0),
                ar_status = CASE
                    WHEN COALESCE((SELECT MAX(days_overdue) FROM late_fees lf WHERE lf.customer_id = ca.customer_id AND lf.paid = FALSE), 0) >= 90 THEN '90_days_plus'
                    WHEN COALESCE((SELECT MAX(days_overdue) FROM late_fees lf WHERE lf.customer_id = ca.customer_id AND lf.paid = FALSE), 0) >= 60 THEN '60_days'
                    WHEN COALESCE((SELECT MAX(days_overdue) FROM late_fees lf WHERE lf.customer_id = ca.customer_id AND lf.paid = FALSE), 0) >= 30 THEN '30_days'
                    ELSE 'current'
                END
            WHERE COALESCE((SELECT COALESCE(SUM(total_fee), 0) FROM late_fees lf WHERE lf.customer_id = ca.customer_id AND lf.paid = FALSE), 0) > 0
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        return 1
        
    except Exception as e:
        logger.debug(f"Customer AR update error: {e}")
        return 0


def update_inventory_status(config: AdvancedSimulationConfig, simulation_date: date = None) -> int:
    """
    Update inventory status tracking
    
    Level 4 Feature: Tracks inventory transitions between states:
    available, rented, damaged, missing, maintenance
    """
    if not config.advanced_features.get('enable_inventory_status_tracking', False):
        return 0
    
    try:
        conn = mysql.connector.connect(
            host=config.mysql_config['host'],
            user=config.mysql_config['user'],
            password=config.mysql_config['password'],
            database=config.mysql_config['database']
        )
        cursor = conn.cursor()
        
        if simulation_date is None:
            simulation_date = date.today()
        
        # Get currently rented inventory
        cursor.execute("""
            SELECT DISTINCT i.inventory_id FROM inventory i
            INNER JOIN rental r ON i.inventory_id = r.inventory_id
            WHERE r.return_date IS NULL
        """)
        
        rented_ids = [row[0] for row in cursor.fetchall()]
        status_updates = []
        
        for inv_id in rented_ids[:500]:  # Batch process
            status_updates.append(('rented', simulation_date, None, inv_id))
        
        if status_updates:
            cursor.executemany("""
                INSERT INTO inventory_status (status, status_date, notes, inventory_id)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                status = VALUES(status),
                status_date = VALUES(status_date)
            """, status_updates)
            conn.commit()
        
        cursor.close()
        conn.close()
        return len(status_updates)
        
    except Exception as e:
        logger.debug(f"Inventory status update error: {e}")
        return 0


# ============================================================================
# INCREMENTAL WEEKS WITH ADVANCED BUSINESS LOGIC
# ============================================================================

def add_incremental_weeks(config: AdvancedSimulationConfig, num_weeks: int, 
                         current_sim_week: int, override_season: float = None) -> int:
    """
    Add incremental weeks with Level 4 advanced business logic
    
    Includes:
    - Film releases aligned with market trends
    - Inventory additions based on business phase
    - Volume modifiers from business lifecycle
    - Seasonal multipliers
    - Progress tracking every 10 weeks
    """
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
        
        weeks_added = 0
        for i in range(num_weeks):
            week_start = next_week_start + timedelta(weeks=i)
            week_number = weeks_since_start + i + 1
            
            # Check for film releases
            has_films, num_films, category, film_desc = get_film_releases_for_week(config, week_number)
            if has_films and num_films > 0:
                current_date = config.start_date + timedelta(weeks=week_number)
                logger.info(f"\n🎬 Week {week_number} ({current_date}): {film_desc}")
                add_film_batch(config, num_films, category, film_desc, sim_date=current_date)
            
            # Check for inventory additions
            should_add, qty, desc = get_inventory_additions_for_week(config, week_number)
            if should_add and qty > 0:
                current_date = config.start_date + timedelta(weeks=week_number)
                # Get Monday of current rental week
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
            seasonal_multiplier = get_seasonal_multiplier(week_number, config, override_season)
            
            # Calculate adjusted base volume
            base_volume = config.generation_config['base_weekly_transactions']
            adjusted_volume = int(base_volume * (1 + volume_modifier) * seasonal_multiplier)
            
            # Set seasonal drift for this week
            generator.seasonal_drift = (seasonal_multiplier - 1) * 100
            
            phase = get_business_phase(week_number, config)
            logger.info(f"   Week {week_number}: {phase.title()} Phase")
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


# ============================================================================
# MAIN SIMULATION ORCHESTRATION
# ============================================================================

def display_simulation_plan(config: AdvancedSimulationConfig):
    """Display comprehensive simulation plan"""
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
    if config.reactivation_config.get('enable_reactivation', False):
        logger.info(f"\nCustomer Reactivation:")
        logger.info(f"  Starts: Week {config.reactivation_config['reactivation_start_week']}")
        logger.info(f"  Probability: {config.reactivation_config['reactivation_probability']*100:.0f}%")
        logger.info(f"  Duration: {config.reactivation_config['reactivation_duration_weeks']} weeks")
    
    # Advanced features status
    logger.info(f"\nAdvanced Features (Level 4):")
    logger.info(f"  Late Fees: {'✓ Enabled' if config.advanced_features.get('enable_late_fees') else '✗ Disabled'}")
    logger.info(f"  AR Tracking: {'✓ Enabled' if config.advanced_features.get('enable_ar_tracking') else '✗ Disabled'}")
    logger.info(f"  Inventory Status: {'✓ Enabled' if config.advanced_features.get('enable_inventory_status_tracking') else '✗ Disabled'}")
    logger.info(f"  Seasonality: {'✓ Enabled' if config.advanced_features.get('enable_seasonality') else '✗ Disabled'}")
    logger.info(f"  Customer Churn: {'✓ Enabled' if config.advanced_features.get('enable_customer_churn') else '✗ Disabled'}")
    
    logger.info("=" * 80 + "\n")


def main():
    """Main Level 4 simulation orchestration"""
    print("\n")
    logger.info("╔" + "═" * 78 + "╗")
    logger.info("║" + " LEVEL 4 - ADVANCED MASTER SIMULATION (10-YEAR) ".center(78) + "║")
    logger.info("╚" + "═" * 78 + "╝")
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Level 4 Advanced Master Simulation - Complete 10-year business lifecycle'
    )
    parser.add_argument('--config', type=str, default='config_10year_advanced.json', 
                        help='Configuration file to use (default: config_10year_advanced.json)')
    parser.add_argument('--database', type=str, 
                        help='Database name to override config setting')
    parser.add_argument('--season', type=float, 
                        help='Seasonal boost percentage (e.g., 50 for 50%% boost, 0 for no seasonality)')
    args = parser.parse_args()
    
    logger.info(f"Loading configuration from: {args.config}")
    
    try:
        config = AdvancedSimulationConfig(args.config)
        
        # Override database if provided
        if args.database:
            config.mysql_config['database'] = args.database
            logger.info(f"Database override: {args.database}")
        
        # Override seasonality if provided
        if args.season is not None:
            logger.info(f"Seasonal override: {args.season:+.0f}%")
    
    except FileNotFoundError:
        logger.error(f"Configuration file {args.config} not found")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    
    # Create database if needed
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
        
        # PHASE 2: Advanced business lifecycle simulation
        logger.info("\n" + "=" * 80)
        logger.info("PHASE 2: Advanced Business Lifecycle Simulation")
        logger.info("=" * 80)
        
        remaining_weeks = config.total_weeks - current_week
        logger.info(f"Adding {remaining_weeks} weeks with advanced business logic...\n")
        
        batch_size = 4  # Process 4 weeks at a time
        weeks_added = 0
        
        while weeks_added < remaining_weeks:
            weeks_to_add = min(batch_size, remaining_weeks - weeks_added)
            current_sim_week = current_week + weeks_added
            current_date = config.start_date + timedelta(weeks=current_sim_week)
            
            logger.info(f"\n📊 Weeks {current_sim_week}-{current_sim_week + weeks_to_add - 1} "
                       f"({current_date.strftime('%b %d, %Y')} - ...)")
            
            # Add weeks with advanced business logic
            added_weeks = add_incremental_weeks(config, weeks_to_add, current_sim_week, args.season)
            weeks_added += added_weeks
            
            # Process Level 4 advanced features after each batch
            logger.debug("  Processing advanced features...")
            late_fees_processed = process_late_fees(config, current_date)
            ar_updated = update_customer_ar(config, current_date)
            inventory_updated = update_inventory_status(config, current_date)
            
            progress = (weeks_added / remaining_weeks) * 100
            logger.info(f"   Batch Progress: {progress:.1f}% ({weeks_added}/{remaining_weeks} weeks)")
        
        # PHASE 3: Summary and analytics
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
        
        # Get core statistics
        cursor.execute("SELECT COUNT(*) FROM rental")
        total_rentals = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT customer_id) FROM customer WHERE activebool = TRUE")
        active_customers = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM inventory")
        total_inventory = cursor.fetchone()[0]
        
        cursor.execute("SELECT MIN(rental_date), MAX(rental_date) FROM rental")
        date_range = cursor.fetchone()
        min_date, max_date = date_range
        
        cursor.execute("SELECT COUNT(*) FROM rental WHERE return_date IS NULL")
        checked_out = cursor.fetchone()[0]
        
        # Yearly performance
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
        
        # Customer segmentation analysis
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
        
        # Advanced features statistics (Level 4)
        late_fees_total = 0
        overdue_rentals = 0
        ar_customers = 0
        ar_total_owed = 0
        ar_aging = []
        
        try:
            cursor.execute("SELECT COUNT(*), SUM(total_fee) FROM late_fees WHERE paid = FALSE")
            result = cursor.fetchone()
            overdue_rentals = result[0] if result[0] else 0
            late_fees_total = result[1] if result[1] else 0
            
            cursor.execute("SELECT COUNT(*), SUM(ar_balance) FROM customer_ar WHERE ar_balance > 0")
            result = cursor.fetchone()
            ar_customers = result[0] if result[0] else 0
            ar_total_owed = result[1] if result[1] else 0
            
            cursor.execute("""
                SELECT ar_status, COUNT(*)
                FROM customer_ar
                WHERE ar_balance > 0
                GROUP BY ar_status
                ORDER BY ar_status
            """)
            ar_aging = cursor.fetchall()
        except:
            pass  # Advanced features tables may not exist
        
        cursor.close()
        conn.close()
        
        # Display results
        logger.info(f"\n✓ Total Rentals: {total_rentals:,}")
        logger.info(f"✓ Active Customers: {active_customers:,}")
        logger.info(f"✓ Total Inventory Items: {total_inventory:,}")
        logger.info(f"✓ Inventory Growth: {((total_inventory - initial_inventory) / initial_inventory * 100):.1f}% "
                   f"(from {initial_inventory:,} to {total_inventory:,})")
        logger.info(f"✓ Data Range: {min_date} to {max_date}")
        logger.info(f"✓ Currently Checked Out: {checked_out:,} items")
        logger.info(f"✓ Average Rentals per Week: {total_rentals // config.total_weeks:,}")
        
        logger.info(f"\n📊 Yearly Performance:")
        for year, rentals, avg_duration in yearly_stats:
            logger.info(f"   Year {year}: {rentals:,} rentals (avg duration: {avg_duration:.1f} days)")
        
        logger.info(f"\n👥 Customer Segments:")
        for user_type, count, avg_rentals in user_segments:
            logger.info(f"   {user_type}: {count:,} customers (avg {avg_rentals:.1f} rentals each)")
        
        # Level 4 advanced analytics
        if config.advanced_features.get('enable_late_fees', False) or config.advanced_features.get('enable_ar_tracking', False):
            logger.info(f"\n💰 Late Fees & Accounts Receivable (Level 4):")
            logger.info(f"   Overdue Rentals: {overdue_rentals:,}")
            logger.info(f"   Total Late Fees Owed: ${late_fees_total:,.2f}")
            logger.info(f"   Customers with AR: {ar_customers:,}")
            logger.info(f"   Total AR Balance: ${ar_total_owed:,.2f}")
            
            if ar_aging:
                logger.info(f"   AR Aging Breakdown:")
                for status, count in ar_aging:
                    logger.info(f"      {status}: {count:,} customers")
        
        logger.info("\n" + "=" * 80)
        logger.info("LEVEL 4 ADVANCED SIMULATION SUCCESSFUL!")
        logger.info("=" * 80)
        logger.info(f"\nDatabase '{config.mysql_config['database']}' contains {config.total_weeks // 52} years of")
        logger.info("sophisticated business simulation with:")
        logger.info("  • Complete business lifecycle (growth → plateau → decline → reactivation)")
        logger.info("  • Advanced customer segmentation and behavior modeling")
        logger.info("  • Late fees and accounts receivable tracking")
        logger.info("  • Inventory status management")
        logger.info("  • Realistic seasonal variations and market dynamics")
        logger.info("  • Customer churn and reactivation patterns")
        logger.info("  • Comprehensive business intelligence data")
        logger.info("\nReady for advanced SQL analysis, business intelligence, and data science projects!")
        logger.info("\n")
        
    except Exception as e:
        logger.error(f"\n❌ Simulation failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
