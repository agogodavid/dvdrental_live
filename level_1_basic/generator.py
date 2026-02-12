"""
DVD Rental Database Generator
Generates realistic transaction data with business patterns:
- Transactions shift from weekends to weekdays over time
- New customers added gradually (~10/week)
- Customer churn (~40% after 5 weeks, ~15% loyal)
- ~500 transactions/week initially
- Rental duration 3-7 days
- Random spike days (4x rentals)
"""

import mysql.connector
from mysql.connector import Error
import random
import math
from datetime import datetime, timedelta
from typing import List, Tuple, Dict
import json
from pathlib import Path
import logging
import argparse
import os

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DVDRentalDataGenerator:
    def __init__(self, mysql_config: Dict, generation_config: Dict = None):
        """Initialize database connection and configuration"""
        self.mysql_config = mysql_config
        self.generation_config = generation_config or {}
        self.config = self.generation_config  # Alias for compatibility
        self.conn = None
        self.cursor = None
        self.db_name = mysql_config.get('database', 'dvdrental_live')
        # Allow database override via environment variable
        if 'DATABASE_NAME' in os.environ:
            self.db_name = os.environ['DATABASE_NAME']
        self.seasonal_drift = 0.0  # Percentage change in transaction volume (-100 to 100+)
        self.churned_customers = set()  # Track permanently churned customers
        
        # Parse start_date from generation config
        start_date_str = self.generation_config.get('start_date', '2001-10-01')
        logger.info(f"Loading start_date from config: {start_date_str}")
        if isinstance(start_date_str, str):
            from datetime import datetime as dt
            self.start_date = dt.strptime(start_date_str, '%Y-%m-%d').date()
        else:
            self.start_date = start_date_str
        logger.info(f"Using start_date: {self.start_date}")
        
        # Get power law exponent from config (for Zipfian distribution)
        self.zipfian_alpha = self.generation_config.get('rental_distribution', {}).get('alpha', 1.0)
        
        # Extract all generation parameters from config
        self.weekly_new_customers = self.generation_config.get('weekly_new_customers', 10)
        self.base_weekly_transactions = self.generation_config.get('base_weekly_transactions', 500)
        self.churn_after_weeks = self.generation_config.get('customer_churn_after_weeks', 5)
        self.churn_rate = self.generation_config.get('churn_rate', 0.4)
        self.loyal_customer_rate = self.generation_config.get('loyal_customer_rate', 0.15)
        self.rental_duration_min = self.generation_config.get('rental_duration_min', 3)
        self.rental_duration_max = self.generation_config.get('rental_duration_max', 7)
        self.spike_day_probability = self.generation_config.get('spike_day_probability', 0.05)
        self.spike_day_multiplier = self.generation_config.get('spike_day_multiplier', 4)
        
        # Film generation parameters
        self.film_rental_rate_min = self.generation_config.get('film_rental_rate_min', 2.99)
        self.film_rental_rate_max = self.generation_config.get('film_rental_rate_max', 9.99)
        self.film_length_min = self.generation_config.get('film_length_min', 80)
        self.film_length_max = self.generation_config.get('film_length_max', 180)
        self.film_replacement_cost_min = self.generation_config.get('film_replacement_cost_min', 10.0)
        self.film_replacement_cost_max = self.generation_config.get('film_replacement_cost_max', 30.0)
        
        # Payment/return parameters
        self.payment_amount_min = self.generation_config.get('payment_amount_min', 2.99)
        self.payment_amount_max = self.generation_config.get('payment_amount_max', 15.99)
        self.late_return_probability = self.generation_config.get('late_return_probability', 0.3)
        self.late_days_max = self.generation_config.get('late_days_max', 14)
        
        # Transaction pattern parameters
        self.week_shift_threshold = self.generation_config.get('week_shift_threshold', 8)
        self.week_shift_duration = self.generation_config.get('week_shift_duration', 16)
        
        # Student names configuration
        student_names_config = self.generation_config.get('student_names', {})
        self.use_student_names = student_names_config.get('enabled', False)
        self.student_names = student_names_config.get('names', [])
        
    def _get_first_and_last_names(self):
        """Get first and last name lists, using student names if enabled"""
        if self.use_student_names and self.student_names:
            # Use student names for first names, and generic last names or student last initials
            first_names = self.student_names
            # Generate last names by adding common suffixes to student names
            last_names = [f"{name}son" if name[-1] != 's' else f"{name}en" for name in self.student_names]
            # Fallback: ensure we have enough names
            if len(first_names) < 8:
                default_first = ['James', 'Mary', 'Robert', 'Patricia', 'Michael', 'Linda', 'William', 'Barbara']
                first_names = first_names + default_first[len(first_names):]
            if len(last_names) < 8:
                default_last = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis']
                last_names = last_names + default_last[len(last_names):]
            return first_names, last_names
        else:
            # Use default names
            first_names = ['James', 'Mary', 'Robert', 'Patricia', 'Michael', 'Linda', 'William', 'Barbara',
                          'David', 'Elizabeth', 'Richard', 'Susan', 'Joseph', 'Jessica', 'Thomas', 'Sarah']
            last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
                         'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson', 'Thomas']
            return first_names, last_names
        
    def connect(self):
        """Establish MySQL connection"""
        try:
            # Connect to MySQL without specifying database first
            self.conn = mysql.connector.connect(
                host=self.mysql_config['host'],
                user=self.mysql_config['user'],
                password=self.mysql_config['password']
            )
            self.cursor = self.conn.cursor()
            
            # Check if database exists
            self.cursor.execute("SHOW DATABASES")
            databases = [db[0] for db in self.cursor.fetchall()]
            
            if self.db_name not in databases:
                logger.info(f"Database {self.db_name} does not exist. Creating it...")
                self.create_database()
            else:
                # Select the database if it exists
                self.cursor.execute(f"USE {self.db_name}")
                
            logger.info("Connected to MySQL successfully")
        except Error as e:
            logger.error(f"Error connecting to MySQL: {e}")
            raise
    def disconnect(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        logger.info("Disconnected from MySQL")
    
    def create_database(self):
        """Create the dvdrental_live database"""
        try:
            self.cursor.execute(f"DROP DATABASE IF EXISTS {self.db_name}")
            self.cursor.execute(f"CREATE DATABASE {self.db_name}")
            self.cursor.execute(f"USE {self.db_name}")
            self.conn.commit()
            logger.info(f"Database {self.db_name} created successfully")
        except Error as e:
            logger.error(f"Error creating database: {e}")
            raise
    
    def create_schema(self, schema_file: str = 'schema_base.sql'):
        """Create tables from schema file"""
        # Try to find schema file in multiple locations
        script_dir = os.path.dirname(os.path.abspath(__file__))
        schema_paths = [
            schema_file,  # Current directory
            os.path.join(script_dir, schema_file),  # Same directory as script
            os.path.join(script_dir, '..', 'shared', 'schemas', schema_file),  # Shared schemas
        ]
        
        schema_path = None
        for path in schema_paths:
            if os.path.exists(path):
                schema_path = path
                logger.info(f"Found schema at: {path}")
                break
        
        if not schema_path:
            logger.error(f"Schema file not found in: {schema_paths}")
            raise FileNotFoundError(f"Cannot find {schema_file}")
        
        try:
            with open(schema_path, 'r') as f:
                schema = f.read()
            
            # Split by semicolon and execute each statement
            statements = [stmt.strip() for stmt in schema.split(';') if stmt.strip()]
            for stmt in statements:
                self.cursor.execute(stmt)
            self.conn.commit()
            logger.info("Schema created successfully")
        except Error as e:
            logger.error(f"Error creating schema: {e}")
            raise
    
    def seed_base_data(self):
        """Seed initial reference data (countries, cities, languages, categories, actors, films)"""
        logger.info("Seeding base data...")
        
        # Countries
        countries = [
            ('United States',), ('Canada',), ('United Kingdom',), ('Australia',),
            ('Germany',), ('France',), ('Japan',), ('India',)
        ]
        self.cursor.executemany("INSERT INTO country (country) VALUES (%s)", countries)
        
        # Cities
        cities = [
            ('New York', 1), ('Toronto', 2), ('London', 3), ('Sydney', 4),
            ('Berlin', 5), ('Paris', 6), ('Tokyo', 7), ('Mumbai', 8),
            ('Los Angeles', 1), ('Vancouver', 2)
        ]
        self.cursor.executemany("INSERT INTO city (city, country_id) VALUES (%s, %s)", cities)
        
        # Languages
        languages = [('English',), ('Spanish',), ('French',), ('German',), ('Japanese',)]
        self.cursor.executemany("INSERT INTO language (name) VALUES (%s)", languages)
        
        # Categories
        categories = [
            ('Action',), ('Comedy',), ('Drama',), ('Horror',), ('Sci-Fi',),
            ('Romance',), ('Thriller',), ('Animation',)
        ]
        self.cursor.executemany("INSERT INTO category (name) VALUES (%s)", categories)
        
        # Actors (100 sample actors)
        first_names, last_names = self._get_first_and_last_names()
        
        actors = [(random.choice(first_names), random.choice(last_names)) for _ in range(100)]
        self.cursor.executemany("INSERT INTO actor (first_name, last_name) VALUES (%s, %s)", actors)
        
        self.conn.commit()
        logger.info("Base data seeded successfully")
    
    def seed_films(self, count: int = 100, start_date=None):
        """Seed films with realistic release years relative to simulation start date
        Uses unified_film_generator for consistent template-based titles.
        
        Args:
            count: Number of films to generate
            start_date: Simulation start date. Films will be from 10 years before to 1 year before this date.
                       If None, defaults to 1995-2000.
        """
        logger.info(f"Seeding {count} films using unified template-based generation...")
        
        # Import unified film generator from master_simulation module
        try:
            # Try to import from master_simulation/film_system
            import sys
            module_path = os.path.join(os.path.dirname(__file__), '..', 'level_3_master_simulation', 'film_system')
            if os.path.exists(module_path) and module_path not in sys.path:
                sys.path.insert(0, module_path)
            
            from unified_film_generator import generate_film_title, load_templates_from_files
            templates = load_templates_from_files()
            logger.info(f"✓ Loaded unified templates with {len(templates)} categories")
        except Exception as e:
            logger.warning(f"Could not load unified templates: {e}. Using fallback procedural generation.")
            # Fallback to basic titles if unified generator unavailable
            templates = None
        
        # Calculate year range based on simulation start date
        if start_date:
            from datetime import datetime
            if isinstance(start_date, str):
                sim_year = int(start_date.split('-')[0])
            else:
                sim_year = start_date.year
            year_min = sim_year - 10
            year_max = sim_year - 1
        else:
            # Default fallback
            year_min = 1995
            year_max = 2000
        
        # Generate unique titles
        used_titles = set()
        films = []
        categories_used = list(templates.keys()) if templates else ["Drama"]
        
        for i in range(count):
            if templates:
                # Use unified film generator for consistent titles
                category = random.choice(categories_used)
                title, description, rating = generate_film_title(category, templates)
            else:
                # Fallback: procedural generation
                film_adjectives = ['The', 'A', 'Silent', 'Crazy', 'Dark', 'Bright', 'Lost', 'Found']
                film_nouns = ['Matrix', 'Dream', 'Knight', 'Voyage', 'Dynasty', 'Heist', 'Forest', 'Redemption']
                film_modifiers = ['', ' Returns', ' Reloaded', ' Revolutions', ' Awakens', ' Strikes Back']
                
                adj = random.choice(film_adjectives)
                noun = random.choice(film_nouns)
                mod = random.choice(film_modifiers)
                title = f"{adj} {noun}{mod}"
                description = "A compelling film"
                rating = random.choice(['PG', 'PG-13', 'R'])
            
            # Ensure title uniqueness
            counter = 1
            original_title = title
            while title in used_titles and counter < 100:
                title = f"{original_title} ({counter})"
                counter += 1
            used_titles.add(title)
            
            # Generate films from 10 years before simulation to 1 year before
            release_year = random.randint(year_min, year_max)
            language_id = random.randint(1, 5)
            rental_duration = random.randint(self.rental_duration_min, self.rental_duration_max)
            rental_rate = round(random.uniform(self.film_rental_rate_min, self.film_rental_rate_max), 2)
            length = random.randint(self.film_length_min, self.film_length_max)
            replacement_cost = round(random.uniform(self.film_replacement_cost_min, self.film_replacement_cost_max), 2)
            special_features = json.dumps(['Deleted Scenes', 'Commentaries'])
            
            films.append((title, description, release_year, language_id, rental_duration,
                         rental_rate, length, replacement_cost, rating, special_features))
        
        self.cursor.executemany(
            """INSERT INTO film (title, description, release_year, language_id, rental_duration,
               rental_rate, length, replacement_cost, rating, special_features)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            films
        )
        
        # Assign actors to films
        for film_id in range(1, count + 1):
            num_actors = random.randint(3, 8)
            actor_ids = random.sample(range(1, 101), num_actors)
            for actor_id in actor_ids:
                self.cursor.execute(
                    "INSERT INTO film_actor (actor_id, film_id) VALUES (%s, %s)",
                    (actor_id, film_id)
                )
        
        # Assign categories to films
        for film_id in range(1, count + 1):
            num_categories = random.randint(1, 3)
            category_ids = random.sample(range(1, 9), num_categories)
            for category_id in category_ids:
                self.cursor.execute(
                    "INSERT INTO film_category (film_id, category_id) VALUES (%s, %s)",
                    (film_id, category_id)
                )
        
        self.conn.commit()
        logger.info(f"{count} films seeded successfully")
    
    def create_stores_and_staff(self, num_stores: int = 2):
        """Create stores and staff"""
        logger.info(f"Creating {num_stores} stores and staff...")
        
        # Create addresses for staff and stores
        addresses = []
        for i in range(num_stores * 2):
            address = f"{random.randint(100, 9999)} Main Street"
            district = random.choice(['Downtown', 'Uptown', 'Midtown', 'Suburbs'])
            city_id = random.randint(1, 10)
            postal_code = f"{random.randint(10000, 99999)}"
            phone = f"{random.randint(200, 999)}-{random.randint(200, 999)}-{random.randint(1000, 9999)}"
            addresses.append((address, None, district, city_id, postal_code, phone))
        
        self.cursor.executemany(
            """INSERT INTO address (address, address2, district, city_id, postal_code, phone)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            addresses
        )
        self.conn.commit()
        
        # Get address IDs
        self.cursor.execute(f"SELECT address_id FROM address ORDER BY address_id DESC LIMIT {num_stores * 2}")
        address_ids = [row[0] for row in reversed(self.cursor.fetchall())]
        
        # Create staff first
        staff_list = []
        for i in range(num_stores):
            first_name = random.choice(['John', 'Jane', 'Bob', 'Alice'])
            last_name = random.choice(['Smith', 'Johnson', 'Williams', 'Brown'])
            email = f"{first_name.lower()}.{last_name.lower()}@dvdrental.com"
            username = f"staff{i+1}"
            password = "password"
            
            staff_list.append((first_name, last_name, address_ids[i], email, None, 1, username, password, None))
        
        self.cursor.executemany(
            """INSERT INTO staff (first_name, last_name, address_id, email, store_id, active, username, password, picture)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            staff_list
        )
        self.conn.commit()
        
        # Get staff IDs
        self.cursor.execute("SELECT staff_id FROM staff")
        staff_ids = [row[0] for row in self.cursor.fetchall()]
        
        # Create stores with staff as managers
        for i in range(num_stores):
            manager_staff_id = staff_ids[i]
            address_id = address_ids[num_stores + i]
            self.cursor.execute(
                "INSERT INTO store (manager_staff_id, address_id) VALUES (%s, %s)",
                (manager_staff_id, address_id)
            )
        
        # Update staff store_id
        self.cursor.execute("SELECT store_id FROM store")
        store_ids = [row[0] for row in self.cursor.fetchall()]
        
        for i, staff_id in enumerate(staff_ids):
            store_id = store_ids[min(i, len(store_ids) - 1)]
            self.cursor.execute("UPDATE staff SET store_id = %s WHERE staff_id = %s", (store_id, staff_id))
        
        self.conn.commit()
        logger.info(f"{num_stores} stores and staff created successfully")
    
    def create_inventory(self):
        """Create inventory for films in stores"""
        logger.info("Creating inventory...")
        
        self.cursor.execute("SELECT film_id FROM film")
        film_ids = [row[0] for row in self.cursor.fetchall()]
        
        self.cursor.execute("SELECT store_id FROM store")
        store_ids = [row[0] for row in self.cursor.fetchall()]
        
        # Get staff IDs for random assignment
        self.cursor.execute("SELECT staff_id FROM staff")
        staff_ids = [row[0] for row in self.cursor.fetchall()]
        
        # Use start_date from config for initial inventory
        purchase_date = self.start_date
        
        # Create multiple copies of each film per store
        inventory = []
        for film_id in film_ids:
            for store_id in store_ids:
                # 2-5 copies per film per store
                for _ in range(random.randint(2, 5)):
                    staff_id = random.choice(staff_ids) if staff_ids else 1
                    inventory.append((film_id, store_id, purchase_date, staff_id))
        
        self.cursor.executemany(
            "INSERT INTO inventory (film_id, store_id, date_purchased, staff_id) VALUES (%s, %s, %s, %s)",
            inventory
        )
        self.conn.commit()
        logger.info(f"{len(inventory)} inventory items created successfully")
    
    def get_week_day_distribution(self, weeks_elapsed: int) -> Dict[int, float]:
        """
        Get day-of-week distribution based on weeks elapsed.
        Shifts from weekend-heavy to weekday-heavy over time.
        0=Monday, 6=Sunday
        """
        # First week_shift_threshold weeks: weekend heavy (Friday-Sunday)
        # After threshold: gradual shift to weekday heavy
        
        if weeks_elapsed < self.week_shift_threshold:
            # Weekends are busier: Fri(4): 0.15, Sat(5): 0.2, Sun(6): 0.15
            # Weekdays: Mon-Thu: 0.1 each
            distribution = {
                0: 0.1,  # Monday
                1: 0.1,  # Tuesday
                2: 0.1,  # Wednesday
                3: 0.1,  # Thursday
                4: 0.15, # Friday
                5: 0.2,  # Saturday
                6: 0.15  # Sunday
            }
        else:
            # After threshold: shift to weekday heavy
            progress = min((weeks_elapsed - self.week_shift_threshold) / self.week_shift_duration, 1.0)
            base_weekday = 0.12 + (0.08 * progress)
            base_weekend = 0.15 - (0.05 * progress)
            
            distribution = {
                0: base_weekday,      # Monday
                1: base_weekday,      # Tuesday
                2: base_weekday,      # Wednesday
                3: base_weekday + 0.01,  # Thursday (slightly higher)
                4: base_weekend,      # Friday
                5: base_weekend,      # Saturday
                6: base_weekend - 0.01   # Sunday
            }
        
        return distribution
    
    def is_spike_day(self, date: datetime, spike_probability: float = None) -> bool:
        """Randomly determine if a day is a spike day (multiplier x transactions)"""
        if spike_probability is None:
            spike_probability = self.spike_day_probability
        return random.random() < spike_probability
    
    def add_week_of_transactions(self, week_start_date, week_number: int):
        """
        Add a week's worth of transactions.
        
        Args:
            week_start_date: Monday of the week (as datetime.date)
            week_number: Which week this is (1-indexed)
        """
        logger.info(f"Adding transactions for week {week_number} starting {week_start_date}")
        
        # Determine number of new customers to add
        self.add_new_customers(week_number, self.weekly_new_customers)
        
        # Get active customers for this week
        active_customers = self.get_active_customers(week_number)
        if not active_customers:
            logger.warning(f"No active customers in week {week_number}")
            return
        
        # Calculate transaction volume
        volume_growth = 1 + (week_number * 0.02)  # 2% growth per week
        seasonal_factor = 1 + (self.seasonal_drift / 100)  # Convert percentage to multiplier
        expected_transactions = int(self.base_weekly_transactions * volume_growth * seasonal_factor)
        
        logger.info(f"Base volume: {self.base_weekly_transactions}, Growth: {volume_growth:.2f}x, "
                   f"Seasonal: {seasonal_factor:.2f}x ({self.seasonal_drift:+.1f}%), "
                   f"Total expected: {expected_transactions}")
        
        # Get day distribution for this week
        day_distribution = self.get_week_day_distribution(week_number)
        
        # Generate transactions for each day of the week
        transactions = []
        inventory_ids = self._get_all_inventory_ids()
        staff_ids = self._get_all_staff_ids()
        
        for day_offset in range(7):
            current_date = week_start_date + timedelta(days=day_offset)
            day_of_week = current_date.weekday()
            
            # Determine transaction count for this day
            base_count = int(expected_transactions / 7)
            day_transactions = int(base_count * day_distribution[day_of_week])
            
            # Check for spike day (multiplier x volume)
            if self.is_spike_day(current_date):
                day_transactions *= self.spike_day_multiplier
                logger.info(f"Spike day detected on {current_date}: {day_transactions} transactions")
            
            # Generate transactions
            for _ in range(day_transactions):
                transaction = self.generate_transaction(
                    current_date, active_customers, inventory_ids, staff_ids
                )
                transactions.append(transaction)
        
        # Insert all transactions
        if transactions:
            self._insert_transactions(transactions)
            logger.info(f"Added {len(transactions)} transactions for week {week_number}")
    
    def add_new_customers(self, week_number: int, count: int):
        """Add new customers for the week"""
        addresses = []
        customers = []
        
        self.cursor.execute("SELECT store_id FROM store")
        store_ids = [row[0] for row in self.cursor.fetchall()]
        
        if not store_ids:
            logger.warning("No stores found")
            return
        
        # Create addresses
        for i in range(count):
            address = f"{random.randint(100, 9999)} Street {i}"
            district = random.choice(['Downtown', 'Uptown', 'Midtown', 'Suburbs'])
            city_id = random.randint(1, 10)
            postal_code = f"{random.randint(10000, 99999)}"
            phone = f"{random.randint(200, 999)}-{random.randint(200, 999)}-{random.randint(1000, 9999)}"
            addresses.append((address, None, district, city_id, postal_code, phone))
        
        self.cursor.executemany(
            """INSERT INTO address (address, address2, district, city_id, postal_code, phone)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            addresses
        )
        self.conn.commit()
        
        # Get new address IDs
        self.cursor.execute("SELECT address_id FROM address ORDER BY address_id DESC LIMIT %s", (count,))
        address_ids = [row[0] for row in reversed(self.cursor.fetchall())]
        
        # Create customers
        first_names, last_names = self._get_first_and_last_names()
        
        create_date = self.start_date + timedelta(weeks=week_number-1)
        
        for i in range(count):
            store_id = random.choice(store_ids)
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            email = f"{first_name.lower()}.{last_name.lower()}{i}@email.com"
            address_id = address_ids[i]
            
            customers.append((store_id, first_name, last_name, email, address_id, True, create_date, 1))
        
        self.cursor.executemany(
            """INSERT INTO customer (store_id, first_name, last_name, email, address_id, activebool, create_date, active)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            customers
        )
        self.conn.commit()
    
    def get_active_customers(self, week_number: int) -> List[int]:
        """Get customers active in this week (considering permanent churn)"""
        # Churn configuration from config.json
        
        self.cursor.execute("""
            SELECT customer_id, DATEDIFF(CURDATE(), create_date) as days_since_creation
            FROM customer
            WHERE activebool = TRUE
        """)
        
        customers = self.cursor.fetchall()
        active = []
        
        for customer_id, days_since_creation in customers:
            if days_since_creation is None:
                continue
            
            # Skip permanently churned customers
            if customer_id in self.churned_customers:
                continue
            
            weeks_since_creation = days_since_creation // 7
            
            # First week_shift_threshold weeks: ramp-up period, accept ALL customers (no churn)
            if week_number <= self.week_shift_threshold:
                active.append(customer_id)
            # After ramp-up: apply permanent churn logic
            else:
                # loyal_customer_rate% of customers are always loyal (never churn)
                if random.random() < self.loyal_customer_rate:
                    active.append(customer_id)
                # For remaining: after churn_after_weeks weeks from creation, churn_rate% churn permanently
                elif weeks_since_creation < self.churn_after_weeks:
                    active.append(customer_id)
                else:
                    # Only apply churn to customers older than churn_after_weeks
                    if random.random() > self.churn_rate:  # (1 - churn_rate)% stay, churn_rate% churn
                        active.append(customer_id)
                    else:
                        # Mark as permanently churned
                        self.churned_customers.add(customer_id)
        
        return active
    
    def generate_transaction(self, rental_date: datetime, customers: List[int],
                            inventory_ids: List[int], staff_ids: List[int]) -> Tuple:
        """Generate a single rental transaction"""
        customer_id = random.choice(customers)
        
        # Get available inventory IDs that this customer hasn't rented recently
        available_inventory = self._get_available_inventory_for_customer(customer_id, rental_date)
        
        if not available_inventory:
            # If no available inventory, fall back to any inventory
            available_inventory = inventory_ids
        
        # Use weighted selection - newer inventory more likely to be rented
        # Pass rental_date for new movie boost calculation
        inventory_id = self._get_weighted_inventory_id_from_list(available_inventory, rental_date=rental_date)
        if not inventory_id:
            inventory_id = random.choice(available_inventory)  # Fallback
        
        staff_id = random.choice(staff_ids)
        
        # Rental duration with bias towards shorter periods
        rental_days = random.choices(
            list(range(self.rental_duration_min, self.rental_duration_max + 1)),
            weights=[0.3, 0.3, 0.2, 0.1, 0.1][:self.rental_duration_max - self.rental_duration_min + 1]
        )[0]
        
        # Return date logic - all rentals eventually get returned
        if random.random() < (1 - self.late_return_probability):
            # Return within rental period
            return_date = rental_date + timedelta(days=rental_days)
        else:
            # Return late
            late_days = random.randint(1, self.late_days_max)
            return_date = rental_date + timedelta(days=rental_days + late_days)
        
        return (rental_date, inventory_id, customer_id, return_date, staff_id)
    
    def _insert_transactions(self, transactions: List[Tuple]):
        """Insert rental transactions"""
        rental_data = [(t[0], t[1], t[2], t[3], t[4]) for t in transactions]
        
        self.cursor.executemany(
            """INSERT INTO rental (rental_date, inventory_id, customer_id, return_date, staff_id)
               VALUES (%s, %s, %s, %s, %s)""",
            rental_data
        )
        self.conn.commit()
        
        # Generate payments for completed rentals
        self.cursor.execute("""
            SELECT rental_id, customer_id, staff_id, rental_date
            FROM rental
            WHERE return_date IS NOT NULL
            ORDER BY rental_id DESC
            LIMIT %s
        """, (len(transactions),))
        
        rentals = self.cursor.fetchall()
        payments = []
        
        for rental_id, customer_id, staff_id, rental_date in rentals:
            # Check if payment already exists
            self.cursor.execute("SELECT payment_id FROM payment WHERE rental_id = %s", (rental_id,))
            if self.cursor.fetchone():
                continue
            
            amount = round(random.uniform(self.payment_amount_min, self.payment_amount_max), 2)
            payment_date = rental_date + timedelta(hours=random.randint(0, 23))
            payments.append((customer_id, staff_id, rental_id, amount, payment_date))
        
        if payments:
            self.cursor.executemany(
                """INSERT INTO payment (customer_id, staff_id, rental_id, amount, payment_date)
                   VALUES (%s, %s, %s, %s, %s)""",
                payments
            )
            self.conn.commit()
    
    def _get_all_inventory_ids(self) -> List[int]:
        """Get all inventory IDs"""
        self.cursor.execute("SELECT inventory_id FROM inventory")
        return [row[0] for row in self.cursor.fetchall()]
    
    def _get_weighted_inventory_id(self) -> int:
        """
        Get a weighted random inventory ID where newer inventory is more likely to be rented.
        Uses exponential weighting: newer items have higher probability.
        """
        # Get all inventory with creation times
        self.cursor.execute("""
            SELECT inventory_id, created_at
            FROM inventory
            ORDER BY created_at DESC
        """)
        inventory_data = self.cursor.fetchall()
        
        if not inventory_data:
            return None
        
        # Calculate weights: newer items get higher weight
        # Weight = e^(age_rank / total_items * 3) to create exponential distribution
        weights = []
        total = len(inventory_data)
        
        for rank in range(total):
            # Newer items (lower rank) get higher weight
            weight = math.exp(-rank / max(1, total / 3))
            weights.append(weight)
        
        # Normalize weights
        total_weight = sum(weights)
        normalized_weights = [w / total_weight for w in weights]
        
        # Select inventory based on weights
        inventory_ids = [item[0] for item in inventory_data]
        selected_id = random.choices(inventory_ids, weights=normalized_weights, k=1)[0]
        
        return selected_id
    
    def _get_weighted_inventory_id_from_list(self, inventory_ids: List[int], rental_date: datetime = None) -> int:
        """
        Get a weighted random inventory ID using a power law (Zipfian) distribution.
        This models realistic DVD rental patterns where popular films dominate rentals (80/20 rule).
        A percentage of newer movies get a temporary boost to compete with established popular films.
        """
        if not inventory_ids:
            return None
        
        # Get film rental statistics, film IDs, and release dates for the specified inventory IDs
        placeholders = ','.join(['%s'] * len(inventory_ids))
        try:
            # Try query with film_releases table first (preferred, has exact dates)
            self.cursor.execute(f"""
                SELECT i.inventory_id, f.film_id, COALESCE(COUNT(r.rental_id), 0) as rental_count, fr.release_date
                FROM inventory i
                JOIN film f ON i.film_id = f.film_id
                LEFT JOIN film_releases fr ON f.film_id = fr.film_id
                LEFT JOIN rental r ON i.inventory_id = r.inventory_id
                WHERE i.inventory_id IN ({placeholders})
                GROUP BY i.inventory_id, f.film_id, fr.release_date
                ORDER BY rental_count DESC
            """, inventory_ids)
            inventory_data = self.cursor.fetchall()
        except Exception:
            # Fallback: use film.release_year if film_releases table doesn't exist
            # Convert year to approximate date (January 1st of that year)
            self.cursor.execute(f"""
                SELECT i.inventory_id, f.film_id, COALESCE(COUNT(r.rental_id), 0) as rental_count,
                       DATE(CONCAT(f.release_year, '-01-01')) as release_date
                FROM inventory i
                JOIN film f ON i.film_id = f.film_id
                LEFT JOIN rental r ON i.inventory_id = r.inventory_id
                WHERE i.inventory_id IN ({placeholders})
                GROUP BY i.inventory_id, f.film_id, f.release_year
                ORDER BY rental_count DESC
            """, inventory_ids)
            inventory_data = self.cursor.fetchall()
        
        if not inventory_data:
            return None
        
        # Extract rental counts, film IDs, and release dates
        rental_counts = [item[2] for item in inventory_data]
        film_ids = [item[1] for item in inventory_data]
        release_dates = [item[3] for item in inventory_data]
        
        # Calculate Zipfian weights (power law distribution) with selective new movie boost
        # Use the configured alpha value for realistic distribution
        weights = self._calculate_zipfian_weights(
            rental_counts, 
            alpha=self.zipfian_alpha,
            release_dates=release_dates,
            current_date=rental_date,
            film_ids=film_ids
        )
        
        # Select inventory based on power law weights
        available_ids = [item[0] for item in inventory_data]
        selected_id = random.choices(available_ids, weights=weights, k=1)[0]
        
        return selected_id
    
    def _calculate_zipfian_weights(self, rental_counts: List[int], alpha: float = 1.0, 
                                   release_dates: List = None, current_date: datetime = None,
                                   film_ids: List[int] = None) -> List[float]:
        """
        Calculate Zipfian (power law) weights based on film popularity with selective boost for new movies.
        Implements Zipf's Law: weight ∝ 1 / (rank ^ alpha)
        
        This creates the classic 80/20 distribution where top films dominate rentals.
        NEW MOVIES: A percentage of recently released films get a temporary boost to compete with established popular films.
        This reflects reality where not all new releases are equally popular.
        
        Args:
            rental_counts: List of rental counts for each film
            alpha: Power law exponent (1.0 = moderate, 1.5 = more extreme)
            release_dates: List of release dates for each film (optional, for new movie boost)
            current_date: Current simulation date (optional, for new movie boost)
            film_ids: List of film IDs (optional, for selective boost determination)
        
        Returns:
            Normalized weights for random.choices()
        """
        if not rental_counts:
            return [1.0]
        
        # Get new movie boost config
        new_movie_config = self.generation_config.get('new_movie_boost', {})
        boost_enabled = new_movie_config.get('enabled', True)
        boost_days = new_movie_config.get('days_to_boost', 90)
        boost_factor = new_movie_config.get('boost_factor', 2.0)
        boost_percentage = new_movie_config.get('boost_percentage', 100)  # Default: all films get boost
        
        # Rank films by rental count (1 = most popular)
        sorted_counts = sorted(set(rental_counts), reverse=True)
        count_to_rank = {count: rank + 1 for rank, count in enumerate(sorted_counts)}
        
        # Calculate Zipfian weights: weight = 1 / (rank ^ alpha)
        weights = []
        for idx, count in enumerate(rental_counts):
            rank = count_to_rank[count]
            weight = 1.0 / ((rank + 1) ** alpha)
            
            # Apply new movie boost if configured
            if boost_enabled and release_dates and current_date and film_ids:
                release_date = release_dates[idx]
                film_id = film_ids[idx]
                if release_date:
                    days_since_release = (current_date.date() if isinstance(current_date, datetime) else current_date) - release_date
                    days_since_release = days_since_release.days if hasattr(days_since_release, 'days') else days_since_release
                    
                    # If film released recently, check if it gets boosted (based on boost_percentage)
                    if 0 <= days_since_release <= boost_days:
                        # Use film_id modulo to deterministically select which films get boosted
                        # This ensures consistent behavior and realistic distribution
                        if (film_id % 100) < boost_percentage:
                            # Linear boost: starts at boost_factor, decreases to 1.0 over boost_days
                            boost_multiplier = boost_factor - (days_since_release / boost_days) * (boost_factor - 1.0)
                            weight *= boost_multiplier
            
            weights.append(weight)
        
        # Normalize weights to sum to 1.0
        total_weight = sum(weights)
        if total_weight > 0:
            normalized_weights = [w / total_weight for w in weights]
        else:
            normalized_weights = [1.0 / len(weights) for _ in weights]
        
        return normalized_weights
    
    def _get_available_inventory_for_customer(self, customer_id: int, rental_date: datetime) -> List[int]:
        """
        Get inventory IDs that:
        1. Are not currently checked out (return_date IS NULL or in future)
        2. The customer hasn't rented recently (within last 30 days)
        
        This prevents double-checkout where same inventory item is rented twice simultaneously.
        Returns list of available inventory IDs.
        """
        # Check rentals from the last 30 days for this customer
        cutoff_date = rental_date - timedelta(days=30)
        
        self.cursor.execute("""
            SELECT DISTINCT i.film_id
            FROM rental r
            JOIN inventory i ON r.inventory_id = i.inventory_id
            WHERE r.customer_id = %s 
            AND r.rental_date >= %s
        """, (customer_id, cutoff_date))
        
        recently_rented_films = {row[0] for row in self.cursor.fetchall()}
        
        # Get all inventory IDs that are NOT currently checked out
        # Exclude inventory where return_date is NULL (still checked out) or in the future
        self.cursor.execute("""
            SELECT DISTINCT i.inventory_id, i.film_id
            FROM inventory i
            WHERE i.inventory_id NOT IN (
                SELECT DISTINCT r.inventory_id
                FROM rental r
                WHERE r.return_date IS NULL
            )
        """)
        all_inventory = self.cursor.fetchall()
        
        # Filter out inventory for recently rented films
        available_inventory = []
        for inventory_id, film_id in all_inventory:
            if film_id not in recently_rented_films:
                available_inventory.append(inventory_id)
        
        return available_inventory
    
    def _get_all_staff_ids(self) -> List[int]:
        """Get all staff IDs"""
        self.cursor.execute("SELECT staff_id FROM staff")
        return [row[0] for row in self.cursor.fetchall()]
    
    def initialize_and_seed(self):
        """Initialize database with schema and base data"""
        self.create_database()
        self.create_schema()
        self.seed_base_data()
        
        # Get values from config
        films_count = self.generation_config.get('films_count', 100)
        stores_count = self.generation_config.get('stores_count', 2)
        
        # Pass start_date for realistic film year generation (10 years before simulation)
        self.seed_films(films_count, start_date=self.start_date)
        self.create_stores_and_staff(stores_count)
        self.create_inventory()
        logger.info("Database initialized and seeded successfully")
    
    def generate_weeks(self, num_weeks: int, start_date=None):
        """Generate transaction data for multiple weeks"""
        # Use provided start_date or default to self.start_date from config
        if start_date is None:
            start_date = self.start_date
        
        # Ensure start_date is a date object
        if isinstance(start_date, str):
            from datetime import datetime as dt
            start_date = dt.strptime(start_date, '%Y-%m-%d').date()
        
        # Move to Monday if not already
        start_date = start_date - timedelta(days=start_date.weekday())
        
        for week_num in range(1, num_weeks + 1):
            week_start = start_date + timedelta(weeks=week_num - 1)
            self.add_week_of_transactions(week_start, week_num)


def main():
    """Main function to initialize and populate database"""
    parser = argparse.ArgumentParser(description='DVD Rental Data Generator')
    parser.add_argument('--database', type=str, help='Database name to use')
    parser.add_argument('--season', type=float, help='Seasonal boost percentage (e.g., 50 for 50% boost, 0 for no seasonality)')
    args = parser.parse_args()
    
    # Load configuration from config.json
    # Try to find config.json in multiple locations
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_paths = [
        'config.json',  # Current directory
        os.path.join(script_dir, 'config.json'),  # Same directory as script
        os.path.join(script_dir, '..', 'shared', 'configs', 'config.json'),  # Shared configs
    ]
    
    config_file = None
    config_data = None
    
    for path in config_paths:
        if os.path.exists(path):
            config_file = path
            logger.info(f"Found configuration at: {path}")
            break
    
    if config_file:
        try:
            with open(config_file, 'r') as f:
                config_data = json.load(f)
        except Exception as e:
            logger.warning(f"Error reading {config_file}: {e}")
    
    if config_data is None:
        logger.error(f"Configuration file not found in any of: {config_paths}")
        logger.info("Using default configuration...")
        config_data = {}
    
    mysql_config = config_data.get('mysql', {})
    if 'database' not in mysql_config:
        mysql_config['database'] = 'dvdrental_live'
    if 'host' not in mysql_config:
        mysql_config['host'] = 'localhost'
    if 'user' not in mysql_config:
        mysql_config['user'] = 'root'
    if 'password' not in mysql_config:
        mysql_config['password'] = 'root'
    
    simulation_config = config_data.get('simulation', {})
    start_date = simulation_config.get('start_date')
    initial_weeks = simulation_config.get('initial_weeks', 12)
    
    logger.info(f"Simulation config start_date: {start_date}")
    
    # Override database name if --database argument provided
    if args.database:
        mysql_config['database'] = args.database
    
    # Apply seasonal drift if --season argument provided
    if args.season is not None:
        logger.info(f"Seasonal boost: {args.season}%")
    
    # Merge generation config with start_date from simulation config
    generation_config = config_data.get('generation', {})
    if start_date:
        generation_config['start_date'] = start_date
        logger.info(f"Merged start_date into generation_config: {start_date}")
    else:
        logger.warning("No start_date found in simulation config!")
    
    generator = DVDRentalDataGenerator(mysql_config, generation_config)
    
    # Apply seasonal drift if provided
    if args.season is not None:
        generator.seasonal_drift = args.season
    
    try:
        generator.connect()
        generator.initialize_and_seed()
        
        # Generate data for configured number of weeks
        logger.info(f"Generating {initial_weeks} weeks of transaction data...")
        generator.generate_weeks(initial_weeks, start_date)
        
        logger.info("Database initialization complete!")
        
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        generator.disconnect()


if __name__ == '__main__':
    main()
