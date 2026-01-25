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

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DVDRentalDataGenerator:
    def __init__(self, config: Dict):
        """Initialize database connection and configuration"""
        self.config = config
        self.conn = None
        self.cursor = None
        self.db_name = config.get('database', 'dvdrental_live')
        self.seasonal_drift = 0.0  # Percentage change in transaction volume (-100 to 100+)
        self.churned_customers = set()  # Track permanently churned customers
        
    def connect(self):
        """Establish MySQL connection"""
        try:
            self.conn = mysql.connector.connect(
                host=self.config['host'],
                user=self.config['user'],
                password=self.config['password'],
                database=self.config.get('database', 'dvdrental_live')
            )
            self.cursor = self.conn.cursor()
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
    
    def create_schema(self, schema_file: str = 'schema.sql'):
        """Create tables from schema file"""
        try:
            with open(schema_file, 'r') as f:
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
        first_names = ['James', 'Mary', 'Robert', 'Patricia', 'Michael', 'Linda', 'William', 'Barbara',
                      'David', 'Elizabeth', 'Richard', 'Susan', 'Joseph', 'Jessica', 'Thomas', 'Sarah']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
                     'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson', 'Thomas']
        
        actors = [(random.choice(first_names), random.choice(last_names)) for _ in range(100)]
        self.cursor.executemany("INSERT INTO actor (first_name, last_name) VALUES (%s, %s)", actors)
        
        self.conn.commit()
        logger.info("Base data seeded successfully")
    
    def seed_films(self, count: int = 100):
        """Seed films"""
        logger.info(f"Seeding {count} films...")
        
        # Generate diverse, unique film titles
        film_adjectives = [
            'The', 'A', 'Silent', 'Crazy', 'Dark', 'Bright', 'Lost', 'Found', 'Hidden', 'Secret',
            'Last', 'First', 'Only', 'Final', 'Ultimate', 'Amazing', 'Incredible', 'Mysterious'
        ]
        film_nouns = [
            'Matrix', 'Dream', 'Knight', 'Voyage', 'Dynasty', 'Heist', 'Forest', 'Redemption',
            'Avenger', 'Avatar', 'Prophet', 'Shadow', 'Light', 'Truth', 'Illusion', 'Reality',
            'Kingdom', 'Empire', 'Revolution', 'Rebellion', 'Journey', 'Quest', 'Escape', 'Return',
            'Mystery', 'Enigma', 'Curse', 'Blessing', 'Judgment', 'Trial', 'Victory', 'Defeat',
            'Phoenix', 'Dragon', 'Sphinx', 'Minotaur', 'Odyssey', 'Inferno', 'Paradise', 'Purgatory'
        ]
        film_modifiers = [
            '', ' Returns', ' Reloaded', ' Revolutions', ' Rising', ' Falls', ' Awakens', ' Strikes Back',
            ' Forever', ' Again', ' Unleashed', ' Unbound', ' Eternal', ' Infinite', ' Absolute'
        ]
        
        descriptions = [
            'A computer programmer discovers an alternate reality',
            'A thief who steals corporate secrets from dreams',
            'A masked vigilante protects his city from corruption',
            'An expedition through a wormhole to save humanity',
            'The aging patriarch of an organized crime dynasty',
            'A pair of hit men navigate philosophical conversations',
            'A man finds redemption through unexpected friendship',
            'An ensemble of heroes band together against evil',
            'An explorer discovers a world unlike any other',
            'Two con artists plan an elaborate heist',
            'A detective uncovers a dark conspiracy',
            'A group of rebels fight against tyranny',
            'A lone warrior seeks revenge and justice',
            'An unlikely friendship changes everything',
            'A thrilling adventure across dangerous lands'
        ]
        
        ratings = ['G', 'PG', 'PG-13', 'R', 'NC-17']
        
        # Generate unique titles
        used_titles = set()
        films = []
        for i in range(count):
            # Create unique title
            while True:
                adj = random.choice(film_adjectives)
                noun = random.choice(film_nouns)
                mod = random.choice(film_modifiers)
                title = f"{adj} {noun}{mod}"
                if title not in used_titles:
                    used_titles.add(title)
                    break
            description = random.choice(descriptions)
            release_year = random.randint(1980, 2023)
            language_id = random.randint(1, 5)
            rental_duration = random.randint(2, 7)
            rental_rate = round(random.uniform(2.99, 9.99), 2)
            length = random.randint(80, 180)
            replacement_cost = round(random.uniform(10.0, 30.0), 2)
            rating = random.choice(ratings)
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
        
        # Create multiple copies of each film per store
        inventory = []
        for film_id in film_ids:
            for store_id in store_ids:
                # 2-5 copies per film per store
                for _ in range(random.randint(2, 5)):
                    staff_id = random.choice(staff_ids) if staff_ids else 1
                    inventory.append((film_id, store_id, self.start_date, staff_id))
        
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
        # First 8 weeks: weekend heavy (Friday-Sunday)
        # After 8 weeks: gradual shift to weekday heavy
        
        if weeks_elapsed < 8:
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
            # After 8 weeks: shift to weekday heavy
            progress = min((weeks_elapsed - 8) / 16, 1.0)  # Shift over 16 weeks
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
    
    def is_spike_day(self, date: datetime, spike_probability: float = 0.05) -> bool:
        """Randomly determine if a day is a spike day (4x transactions)"""
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
        new_customers = 10
        self.add_new_customers(week_number, new_customers)
        
        # Get active customers for this week
        active_customers = self.get_active_customers(week_number)
        if not active_customers:
            logger.warning(f"No active customers in week {week_number}")
            return
        
        # Calculate transaction volume
        base_volume = 500
        volume_growth = 1 + (week_number * 0.02)  # 2% growth per week
        seasonal_factor = 1 + (self.seasonal_drift / 100)  # Convert percentage to multiplier
        expected_transactions = int(base_volume * volume_growth * seasonal_factor)
        
        logger.info(f"Base volume: {base_volume}, Growth: {volume_growth:.2f}x, "
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
            
            # Check for spike day (4x volume)
            if self.is_spike_day(current_date):
                day_transactions *= 4
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
        first_names = ['James', 'Mary', 'Robert', 'Patricia', 'Michael', 'Linda', 'William', 'Barbara']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis']
        
        create_date = datetime.now().date() - timedelta(weeks=8-week_number)
        
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
        # Churn: 40% of customers churn permanently after 5 weeks, 15% are always loyal
        # Exception: First 8 weeks are ramp-up period with no churn (allow customer base to build)
        
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
            
            # First 8 weeks: ramp-up period, accept ALL customers (no churn)
            if week_number <= 8:
                active.append(customer_id)
            # After week 8: apply permanent churn logic
            else:
                # 15% of customers are always loyal
                if random.random() < 0.15:
                    active.append(customer_id)
                # After 5 weeks from creation, 40% permanently churn out
                elif weeks_since_creation < 5:
                    active.append(customer_id)
                elif random.random() > 0.4:  # 60% stay, 40% churn
                    active.append(customer_id)
                else:
                    # Mark as permanently churned
                    self.churned_customers.add(customer_id)
        
        return active
    
    def generate_transaction(self, rental_date: datetime, customers: List[int],
                            inventory_ids: List[int], staff_ids: List[int]) -> Tuple:
        """Generate a single rental transaction"""
        customer_id = random.choice(customers)
        # Use weighted selection - newer inventory more likely to be rented
        inventory_id = self._get_weighted_inventory_id()
        if not inventory_id:
            inventory_id = random.choice(inventory_ids)  # Fallback
        staff_id = random.choice(staff_ids)
        
        # Rental duration 3-7 days, with bias towards shorter periods
        rental_days = random.choices([3, 4, 5, 6, 7], weights=[0.3, 0.3, 0.2, 0.1, 0.1])[0]
        
        # Return date usually early in week (Mon-Wed)
        # Add rental days, then adjust to early week
        return_date = rental_date + timedelta(days=rental_days)
        days_until_next_monday = (7 - return_date.weekday()) % 7
        if days_until_next_monday == 0 and return_date.weekday() != 0:
            days_until_next_monday = 7
        
        # 70% chance return is within rental period or early next week
        if random.random() < 0.7:
            return_date = rental_date + timedelta(days=rental_days)
        else:
            return_date = None  # Not yet returned
        
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
            
            amount = round(random.uniform(2.99, 15.99), 2)
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
    
    def _get_all_staff_ids(self) -> List[int]:
        """Get all staff IDs"""
        self.cursor.execute("SELECT staff_id FROM staff")
        return [row[0] for row in self.cursor.fetchall()]
    
    def initialize_and_seed(self):
        """Initialize database with schema and base data"""
        self.create_database()
        self.create_schema()
        self.seed_base_data()
        self.seed_films(100)
        self.create_stores_and_staff(2)
        self.create_inventory()
        logger.info("Database initialized and seeded successfully")
    
    def generate_weeks(self, num_weeks: int, start_date=None):
        """Generate transaction data for multiple weeks"""
        # Use provided start_date or default to 8 weeks ago (rounded to Monday)
        if start_date is None:
            start_date = datetime.now().date() - timedelta(weeks=8)
        
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
    # Load configuration from config.json
    config_file = 'config.json'
    try:
        with open(config_file, 'r') as f:
            config_data = json.load(f)
            mysql_config = config_data.get('mysql', {})
            if 'database' not in mysql_config:
                mysql_config['database'] = 'dvdrental_live'
            
            simulation_config = config_data.get('simulation', {})
            start_date = simulation_config.get('start_date')
            initial_weeks = simulation_config.get('initial_weeks', 12)
    except FileNotFoundError:
        logger.error(f"Configuration file {config_file} not found")
        logger.info("Using default configuration...")
        mysql_config = {
            'host': 'localhost',
            'user': 'root',
            'password': 'root',
            'database': 'dvdrental_live'
        }
        start_date = None
        initial_weeks = 12
    
    generator = DVDRentalDataGenerator(mysql_config)
    
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
