#!/usr/bin/env python3
"""
Film Generator Module - Generates new films for quarterly releases
Uses unified_film_generator for consistent, template-based title generation
"""

import mysql.connector
from mysql.connector import Error
import random
import json
import logging
from datetime import datetime, date
from typing import Dict, List, Tuple
import os

from unified_film_generator import generate_film_title, load_templates_from_files

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
    "Action": {
        "titles": [
            "The {adjective} Agent", "Mission: {location}", "Operation {name}",
            "Escape from {location}", "The {adjective} Warrior", "Hunt for {name}",
            "Raid on {location}", "The {adjective} Soldier", "Assault {location}",
            "The {adjective} Commando", "Strike Force {name}", "Combat {location}",
            "Siege of {location}", "The {adjective} Pursuit", "Midnight {name}",
            "The Last {name}", "Maximum {adjective}", "Extreme {name}",
            "The {adjective} Siege", "Operation Exodus", "The Final {name}"
        ],
        "adjectives": ["Last", "Final", "Ultimate", "Greatest", "Deadliest", "Fastest", "Bravest", "Wildest"],
        "locations": ["Tokyo", "Berlin", "Moscow", "Bangkok", "Istanbul", "Cairo", "Rio", "Vegas"],
        "names": ["Vendetta", "Retribution", "Reckoning", "Justice", "Thunder", "Inferno", "Phoenix", "Reborn"],
        "descriptions": [
            "An elite agent must stop a dangerous criminal mastermind",
            "A former soldier returns for one final mission",
            "Special forces mount a desperate rescue operation",
            "A lone warrior battles an international conspiracy",
            "A skilled operative infiltrates enemy territory"
        ],
        "rating_dist": [("PG-13", 0.4), ("R", 0.6)],
        "length_range": (90, 130),
        "cost_range": (15, 25)
    },
    
    "Comedy": {
        "titles": [
            "The {adjective} {noun}", "{adjective} Love", "Mr. {name}",
            "Crazy {name}", "The {adjective} Plan", "Love at {location}",
            "Office {adjective}", "The {name} Chronicles", "{name} Goes {location}",
            "Mistaken {noun}", "The {adjective} Wedding", "Speed {noun}",
            "Four {adjective} Friends", "The {location} {noun}", "A {adjective} Affair",
            "Little {name}", "Big {name}", "Zany {noun}", "{adjective} Business"
        ],
        "adjectives": ["Crazy", "Silly", "Angry","Hilarious", "Funny", "Awkward", "Wild", "Stupid", "Mad", "Bizarre"],
        "nouns": ["Dating", "Dates", "Weddings", "Vacation", "Holidays", "Office", "School", "Family"],
        "locations": ["in Paris", "in New York", "in Vegas", "in LA", "Down Under", "in Lagos","in Nairobi"],
        "names": ["Marco", "Lucy", "Sophie", "Charlie", "Sam", "Alex"],
        "descriptions": [
            "A bumbling hero stumbles through misadventures",
            "Three friends try to navigate modern romance",
            "An ordinary person finds themselves in extraordinary situations",
            "A workplace comedy with hilarious mishaps",
            "Friends reunite for a disastrous vacation"
        ],
        "rating_dist": [("G", 0.1), ("PG", 0.3), ("PG-13", 0.4), ("R", 0.2)],
        "length_range": (85, 110),
        "cost_range": (14, 20)
    },
    
    "Drama": {
        "titles": [
            "The {noun} of {name}", "When {name} {verb}", "A {adjective} Love",
            "The {name} Years", "Before {name}", "After {noun}",
            "Letters to {name}", "The {adjective} Heart", "Echoes of {noun}",
            "A Thousand {noun}", "The Burden of {noun}", "{name}'s Choice",
            "The Path to {noun}", "A Single {noun}", "The Weight of {noun}",
            "In the Shadow of {noun}", "The Price of {noun}", "Redemption"
        ],
        "adjectives": ["Broken", "Silent", "Beautiful", "Distant", "Fragile", "Hidden", "Lost", "Timeless"],
        "nouns": ["Souls", "Hearts", "Dreams", "Tears", "Secrets", "Memories", "Choices", "Promises"],
        "verbs": ["Falls", "Waits", "Returns", "Rises", "Fades"],
        "names": ["Sarah", "Michael", "Grace", "David", "Claire", "James"],
        "descriptions": [
            "A powerful story of love and loss spanning decades",
            "Two people discover themselves through unexpected connection",
            "A journey of self-discovery and redemption",
            "Family secrets threaten to tear them apart",
            "A powerful examination of human resilience"
        ],
        "rating_dist": [("PG", 0.2), ("PG-13", 0.4), ("R", 0.4)],
        "length_range": (100, 145),
        "cost_range": (16, 24)
    },
    
    "Horror": {
        "titles": [
            "The {noun} in {location}", "{name} Returns", "The {adjective} {noun}",
            "Curse of the {noun}", "The {noun} Awakens", "Dark {noun}",
            "Nightmare at {location}", "The {adjective} Dead", "Evil {noun}",
            "The {noun} from {location}", "Haunted {noun}", "Possession",
            "The Last {noun}", "Shadows {verb}", "The {adjective} Entity",
            "Something {adjective}", "{noun} Rising"
        ],
        "adjectives": ["Cursed", "Haunted", "Possessed", "Deadly", "Dark", "Evil", "Wicked", "Satanic"],
        "nouns": ["House", "Curse", "Entity", "Demon", "Spirit", "Creature", "Evil", "Darkness"],
        "locations": ["the Asylum", "the Cemetery", "the Mansion", "the Hospital", "the Village"],
        "verbs": ["awakens", "rises", "emerges", "hunts"],
        "names": ["Annabelle", "Exorcism", "Poltergeist"],
        "descriptions": [
            "A group of friends find themselves trapped in a nightmare",
            "An ancient curse is awakened with terrifying consequences",
            "Supernatural forces hunt the inhabitants of an old house",
            "A demonic presence tests the limits of human sanity",
            "Things that should stay buried refuse to rest"
        ],
        "rating_dist": [("PG-13", 0.2), ("R", 0.8)],
        "length_range": (85, 120),
        "cost_range": (15, 22)
    },
    
    "Romance": {
        "titles": [
            "Love in {location}", "{name} and {name2}", "The {adjective} Heart",
            "Eternal {noun}", "A {noun} Romance", "Second {noun}",
            "When Hearts {verb}", "Love After {noun}", "A {adjective} Proposal",
            "Kisses in {location}", "{name}'s Love", "The {adjective} Wedding",
            "A {noun} Story", "Meant to Be", "Against All {noun}",
            "Love Will {verb}", "The {noun} of Life"
        ],
        "adjectives": ["True", "Eternal", "Second", "Perfect", "Sweet", "Tender", "Pure", "Unforgettable"],
        "nouns": ["Love", "Chance", "Dream", "Fate", "Destiny", "Promise", "Hope", "Wishes"],
        "locations": ["Paris", "Rome", "Venice", "Barcelona", "the Beach", "the Mountains"],
        "verbs": ["Meet", "Collide", "Ignite"],
        "names": ["Emma", "Jack", "Sophie", "Marcus", "Grace", "Adam"],
        "names2": ["Lucas", "Nina", "Daniel", "Claire"],
        "descriptions": [
            "Two strangers discover an unexpected connection",
            "A second chance at love when they need it most",
            "Passion ignites between two unlikely souls",
            "Love conquers all obstacles and doubts",
            "A romance that transcends time and circumstance"
        ],
        "rating_dist": [("PG", 0.2), ("PG-13", 0.6), ("R", 0.2)],
        "length_range": (95, 130),
        "cost_range": (14, 22)
    },
    
    "Sci-Fi": {
        "titles": [
            "The Future of {noun}", "{name} Protocol", "Quantum {noun}",
            "The Last {noun}", "Star {name}", "Beyond {location}",
            "The {adjective} Frontier", "Time {verb}", "Android {noun}",
            "The {noun} War", "Cyber {name}", "The {noun} Horizon",
            "Dimension {name}", "Code {noun}", "The {noun} Experiment",
            "Genesis {noun}", "The {adjective} Planet"
        ],
        "adjectives": ["Final", "Unknown", "Last", "Secret", "Hidden", "Infinite", "Parallel", "Alternate"],
        "nouns": ["Protocol", "Wars", "Colonies", "Experiments", "Encounters", "Worlds", "Systems", "Dimensions"],
        "locations": ["Mars", "Venus", "Andromeda", "the Future", "the Past"],
        "verbs": ["Warp", "Jump", "Shift", "Loop"],
        "names": ["Nexus", "Genesis", "Omega", "Alpha", "Phoenix"],
        "descriptions": [
            "Humanity discovers it is not alone in the universe",
            "A mission to save Earth from extinction",
            "Artificial intelligence challenges human supremacy",
            "Time travel creates dangerous paradoxes",
            "Explorers venture into unknown dimensions"
        ],
        "rating_dist": [("PG", 0.1), ("PG-13", 0.6), ("R", 0.3)],
        "length_range": (105, 145),
        "cost_range": (17, 26)
    },
    
    "Animation": {
        "titles": [
            "The Adventures of {name}", "{name}'s Quest", "The {adjective} {noun}",
            "Journey to {location}", "{name} and Friends", "The {noun} Kingdom",
            "Tales of {location}", "The Legend of {name}", "The {adjective} Treasure",
            "Magic in {location}", "The Secret of {noun}", "{name}'s Big Adventure",
            "The {noun} Chronicles", "Legends of {location}", "The {noun} Returns"
        ],
        "adjectives": ["Amazing", "Magical", "Legendary", "Secret", "Hidden", "Lost", "Ancient", "Enchanted"],
        "nouns": ["Dragon", "Kingdom", "Quest", "Adventure", "Mystery", "Treasure", "Heroes", "Champions"],
        "locations": ["Atlantica", "Wonderland", "the Far East", "the Enchanted Forest", "the Mystic Land"],
        "names": ["Zephyr", "Aurora", "Kai", "Luna", "Blaze", "Crystal"],
        "descriptions": [
            "A young hero discovers their magical destiny",
            "Friends embark on an epic adventure",
            "A magical kingdom faces its greatest threat",
            "An outcast finds where they truly belong",
            "Animated adventure with heart and humor"
        ],
        "rating_dist": [("G", 0.6), ("PG", 0.4)],
        "length_range": (80, 120),
        "cost_range": (18, 25)
    },
    
    "Family": {
        "titles": [
            "The {adjective} {noun}", "{name}'s Christmas", "A {noun} Adventure",
            "The {noun} Lesson", "{name} Learns {noun}", "Family {noun}",
            "The Big {noun}", "{name}'s Journey", "A {adjective} Birthday",
            "The {noun} Challenge", "Together {verb}", "The {adjective} Surprise",
            "Our {noun} Story", "The {noun} of Home"
        ],
        "adjectives": ["Wonderful", "Special", "Amazing", "Perfect", "Greatest", "Precious", "Lucky", "Magical"],
        "nouns": ["Adventure", "Christmas", "Vacation", "Holiday", "Birthday", "Lesson", "Journey", "Story"],
        "verbs": ["Forever", "Always", "As One"],
        "names": ["Ollie", "Lily", "Tommy", "Sophie", "Max", "Annie"],
        "descriptions": [
            "A heartwarming tale about family bonds",
            "Children learn valuable lessons through adventure",
            "A holiday story the whole family will enjoy",
            "An adventure that brings a family closer",
            "A feel-good story celebrating togetherness"
        ],
        "rating_dist": [("G", 0.8), ("PG", 0.2)],
        "length_range": (80, 100),
        "cost_range": (14, 20)
    },
    
    "Thriller": {
        "titles": [
            "The {noun} Conspiracy", "Edge of {noun}", "The {adjective} Target",
            "{name} Protocol", "Silent {noun}", "The {noun} Game",
            "Deception {name}", "The {adjective} Hunt", "Lethal {noun}",
            "The {noun} Threat", "Hidden Agenda", "The {noun} Lies",
            "Zero {noun}", "The {adjective} Truth"
        ],
        "adjectives": ["Deadly", "Fatal", "Dangerous", "Hidden", "Secret", "Dark", "Twisted", "Shocking"],
        "nouns": ["Conspiracy", "Lies", "Truth", "Deception", "Threat", "Game", "Code", "Evidence"],
        "names": ["Nexus", "Cipher", "Black", "Shadow", "Eclipse"],
        "descriptions": [
            "A detective races against time to stop a killer",
            "Nothing is what it seems in this twisted tale",
            "A conspiracy threatens to destroy everything",
            "One woman must uncover a dangerous truth",
            "Suspense and betrayal at every turn"
        ],
        "rating_dist": [("PG-13", 0.3), ("R", 0.7)],
        "length_range": (95, 130),
        "cost_range": (15, 23)
    }
}


def load_templates_from_files():
    """
    Load film templates from separate .txt files for easy expansion
    If files exist, they will override the default templates
    """
    global FILM_TEMPLATES
    
    # Check if template files exist in a 'templates' directory
    templates_dir = 'film_templates'
    if not os.path.exists(templates_dir):
        logger.info("Templates directory not found, using default templates")
        return
    
    logger.info(f"Loading templates from {templates_dir}")
    
    for category in FILM_TEMPLATES.keys():
        category_file = os.path.join(templates_dir, f"{category.lower()}.txt")
        if os.path.exists(category_file):
            try:
                with open(category_file, 'r') as f:
                    # Parse the file content
                    content = f.read().strip()
                    # Simple parsing - each line is a title template
                    titles = [line.strip() for line in content.split('\n') if line.strip()]
                    if titles:
                        # Preserve other template properties, just update titles
                        FILM_TEMPLATES[category]["titles"] = titles
                        logger.info(f"Loaded {len(titles)} titles for {category}")
            except Exception as e:
                logger.warning(f"Failed to load {category_file}: {e}")


def generate_film_title(category: str) -> Tuple[str, str, str]:
    """
    Generate a realistic film title, description, and rating based on category
    Returns: (title, description, rating)
    """
    # Load templates from files if they exist
    load_templates_from_files()
    
    if category not in FILM_TEMPLATES:
        category = "Drama"
    
    template = FILM_TEMPLATES[category]
    
    # Choose a title template
    title_template = random.choice(template["titles"])
    
    # Build the title by replacing placeholders
    title = title_template
    
    if "{adjective}" in title:
        adjectives = template.get("adjectives", ["The", "A", "Final", "Last", "Great", "Amazing"])
        title = title.replace("{adjective}", random.choice(adjectives))
    if "{noun}" in title:
        nouns = template.get("nouns", ["Adventure", "Journey", "Quest", "Mission", "Challenge"])
        title = title.replace("{noun}", random.choice(nouns))
    if "{location}" in title:
        locations = template.get("locations", ["City", "World", "Planet", "Galaxy", "Realm"])
        title = title.replace("{location}", random.choice(locations))
    if "{verb}" in title:
        verbs = template.get("verbs", ["Rises", "Falls", "Returns", "Awakens", "Ends"])
        title = title.replace("{verb}", random.choice(verbs))
    if "{name}" in title and "name2" not in template:
        names = template.get("names", ["Hero", "Warrior", "Legend", "Champion", "Guardian"])
        title = title.replace("{name}", random.choice(names))
    if "{name}" in title and "{name2}" in template:
        names = template.get("names", ["Hero", "Warrior", "Legend", "Champion", "Guardian"])
        title = title.replace("{name}", random.choice(names))
    if "{name2}" in title:
        names2 = template.get("names2", ["Villain", "Enemy", "Foe", "Antagonist", "Opponent"])
        title = title.replace("{name2}", random.choice(names2))
    
    # Choose description
    descriptions = template.get("descriptions", [
        "An epic adventure that will test the limits of courage",
        "A thrilling journey filled with unexpected twists and turns",
        "A compelling story of triumph against overwhelming odds"
    ])
    description = random.choice(descriptions)
    
    # Choose rating
    rating_dist = template.get("rating_dist", [("PG", 0.3), ("PG-13", 0.4), ("R", 0.3)])
    rating = random.choices([r[0] for r in rating_dist], weights=[r[1] for r in rating_dist])[0]
    
    return title, description, rating


class FilmGenerator:
    def __init__(self, mysql_config: Dict):
        """Initialize with MySQL configuration"""
        self.mysql_config = mysql_config
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """Establish MySQL connection"""
        try:
            self.conn = mysql.connector.connect(**self.mysql_config)
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
    
    def create_film_releases_table(self):
        """Create the film_releases table if it doesn't exist"""
        try:
            # Create film_releases table for tracking movie market releases
            create_releases_table_query = """
            CREATE TABLE IF NOT EXISTS film_releases (
                release_id INT AUTO_INCREMENT PRIMARY KEY,
                film_id INT NOT NULL,
                release_quarter VARCHAR(10) NOT NULL,
                release_date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (film_id) REFERENCES film(film_id),
                INDEX idx_release_quarter (release_quarter),
                INDEX idx_release_date (release_date)
            ) ENGINE=InnoDB
            """
            self.cursor.execute(create_releases_table_query)
            
            # Create inventory_purchases table for tracking inventory ordering
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
            self.cursor.execute(create_purchases_table_query)
            
            self.conn.commit()
            logger.info("Film releases and inventory purchases tables created/verified successfully")
        except Error as e:
            logger.error(f"Error creating film tables: {e}")
            raise
    
    def get_quarter_for_date(self, date_obj: date) -> str:
        """
        Get quarter designation for a given date
        Returns: String like "Q1 2023"
        """
        quarter = (date_obj.month - 1) // 3 + 1
        return f"Q{quarter} {date_obj.year}"
    
    def get_random_staff_member(self) -> int:
        """Get a random staff member ID"""
        try:
            self.cursor.execute("SELECT staff_id FROM staff WHERE active = TRUE LIMIT 10")
            staff_members = self.cursor.fetchall()
            if staff_members:
                return random.choice(staff_members)[0]
            else:
                # Fallback to any staff member
                self.cursor.execute("SELECT staff_id FROM staff LIMIT 1")
                result = self.cursor.fetchone()
                return result[0] if result else 1
        except Exception as e:
            logger.warning(f"Failed to get staff member: {e}")
            return 1
    
    def add_film_batch(self, num_films: int, category_focus: str = None, 
                      description: str = "", release_date: date = None, add_inventory: bool = True) -> int:
        """
        Add new films to the database with optional inventory copies and track releases
        
        Args:
            num_films: Number of films to generate
            category_focus: Focus on specific category
            description: Description of the batch
            release_date: When films are being released
            add_inventory: Whether to add inventory copies (True) or just record release (False)
        
        Returns: number of films added
        """
        try:
            # Get language_id for English
            self.cursor.execute("SELECT language_id FROM language WHERE name = 'English' LIMIT 1")
            lang_result = self.cursor.fetchone()
            language_id = lang_result[0] if lang_result else 1
            
            # Get or create categories
            if category_focus:
                self.cursor.execute("SELECT category_id FROM category WHERE name = %s", (category_focus,))
                cat_result = self.cursor.fetchone()
                if cat_result:
                    categories = [cat_result[0]]
                else:
                    # Create category if it doesn't exist
                    self.cursor.execute("INSERT INTO category (name) VALUES (%s)", (category_focus,))
                    self.conn.commit()
                    categories = [self.cursor.lastrowid]
            else:
                self.cursor.execute("SELECT category_id FROM category")
                categories = [row[0] for row in self.cursor.fetchall()]
            
            if not categories:
                logger.warning("No categories available")
                return 0
            
            # Get stores for inventory
            self.cursor.execute("SELECT DISTINCT store_id FROM store")
            store_ids = [row[0] for row in self.cursor.fetchall()]
            
            # Get staff for inventory and film releases
            self.cursor.execute("SELECT staff_id FROM staff WHERE active = TRUE")
            staff_results = self.cursor.fetchall()
            logger.debug(f"Found staff results: {staff_results}")
            if staff_results:
                staff_ids = [row[0] for row in staff_results]
            else:
                # Fallback to any staff member
                self.cursor.execute("SELECT staff_id FROM staff LIMIT 1")
                staff_row = self.cursor.fetchone()
                logger.debug(f"Fallback staff row: {staff_row}")
                if staff_row:
                    staff_ids = [staff_row[0]]
                else:
                    # If no staff at all, use a default value (this should not happen in a properly set up DB)
                    staff_ids = [1]
                    logger.warning("No staff found, using default staff ID 1")
            
            logger.debug(f"Using staff IDs: {staff_ids}")
            
            if not store_ids:
                logger.warning("Missing stores")
                return 0
            
            # Generate and add films
            films_added = 0
            # Always use the provided release_date, never default to today
            if release_date is None:
                logger.warning("No release_date provided, using simulation start date from config")
                # Fall back to config start date if available, otherwise use a reasonable default
                try:
                    import json
                    with open('config.json', 'r') as f:
                        config = json.load(f)
                    start_date_str = config.get('simulation', {}).get('start_date', '2001-10-01')
                    from datetime import datetime
                    release_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                except:
                    # Final fallback
                    release_date = date(2001, 10, 1)
            
            film_date = release_date
            film_year = film_date.year
            
            # Create film_releases table if it doesn't exist
            self.create_film_releases_table()
            
            for _ in range(num_films):
                category_choice = category_focus or random.choice(list(FILM_TEMPLATES.keys()))
                title, desc, rating = generate_film_title(category_choice)
                
                # Get template for this category
                template = FILM_TEMPLATES.get(category_choice, FILM_TEMPLATES["Drama"])
                length = random.randint(template["length_range"][0], template["length_range"][1])
                cost = round(random.uniform(template["cost_range"][0], template["cost_range"][1]), 2)
                rental_rate = round(cost * 0.2, 2)  # 20% of cost as rental rate
                release_year = film_year
                
                # Insert film
                self.cursor.execute("""
                    INSERT INTO film (title, description, release_year, language_id, 
                                     rental_duration, rental_rate, length, replacement_cost, rating)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (title, desc, release_year, language_id, 3, rental_rate, length, cost, rating))
                
                film_id = self.cursor.lastrowid
                
                # Link to category
                category_id = random.choice(categories)
                self.cursor.execute("""
                    INSERT INTO film_category (film_id, category_id)
                    VALUES (%s, %s)
                """, (film_id, category_id))
                
                # Record film release to market
                release_quarter = self.get_quarter_for_date(film_date)
                self.cursor.execute("""
                    INSERT INTO film_releases (film_id, release_quarter, release_date)
                    VALUES (%s, %s, %s)
                """, (film_id, release_quarter, film_date))
                
                # Optionally add inventory copies (can be skipped for market releases)
                if add_inventory:
                    # Add inventory copies to stores
                    inventory = []
                    for store_id in store_ids:
                        # Add 5-7 copies per store for more substantial inventory growth
                        for _ in range(random.randint(5, 7)):
                            staff_id = random.choice(staff_ids)
                            inventory.append((film_id, store_id, film_date, staff_id))
                    
                    logger.debug(f"Inserting {len(inventory)} inventory items with staff IDs: {[item[3] for item in inventory]}")
                    
                    self.cursor.executemany(
                        "INSERT INTO inventory (film_id, store_id, date_purchased, staff_id) VALUES (%s, %s, %s, %s)",
                        inventory
                    )
                    
                    # Get the inserted inventory IDs and record purchases
                    # We need to get the actual inserted IDs, not guess them
                    self.cursor.execute("SELECT LAST_INSERT_ID()")
                    first_inventory_id = self.cursor.fetchone()[0]
                    
                    # Record inventory purchases
                    purchase_records = []
                    for i in range(len(inventory)):
                        inventory_id = first_inventory_id + i
                        # For film releases, we'll link to a staff member for purchase decisions
                        staff_id = inventory[i][3] if inventory[i][3] else None
                        purchase_records.append((film_id, inventory_id, staff_id, film_date))
                    
                    self.cursor.executemany("""
                        INSERT INTO inventory_purchases (film_id, inventory_id, staff_id, purchase_date)
                        VALUES (%s, %s, %s, %s)
                    """, purchase_records)
                
                films_added += 1
            
            self.conn.commit()
            
            if add_inventory:
                logger.info(f"✓ Added {films_added} new films with inventory - {description}")
                logger.info(f"  • Category focus: {category_focus or 'Mixed'}")
                logger.info(f"  • Release quarter: {self.get_quarter_for_date(film_date)}")
                logger.info(f"  • Total inventory copies added: {films_added * len(store_ids) * 2}-{films_added * len(store_ids) * 3}")
            else:
                logger.info(f"✓ Added {films_added} films to market (film_releases) - {description}")
                logger.info(f"  • Category focus: {category_focus or 'Mixed'}")
                logger.info(f"  • Release quarter: {self.get_quarter_for_date(film_date)}")
                logger.info(f"  • Note: Not added to inventory, available for purchase decisions")
            
            return films_added
            
        except Exception as e:
            logger.error(f"Failed to add films: {e}")
            self.conn.rollback()
            return 0
    
    def generate_quarterly_films(self, quarter: str, num_films: int, 
                                category_focus: str = None) -> int:
        """
        Generate films for a specific quarter
        Args:
            quarter: Quarter designation like "Q1 2023"
            num_films: Number of films to generate
            category_focus: Optional category focus
        Returns: Number of films added
        """
        try:
            self.connect()
            
            # Parse quarter to get approximate date
            # Format: "Q1 2023"
            parts = quarter.split()
            if len(parts) == 2:
                q_num = int(parts[0][1])  # Extract number from "Q1"
                year = int(parts[1])
                
                # Map quarter to approximate month
                quarter_months = {1: 2, 2: 5, 3: 8, 4: 11}  # Middle month of each quarter
                month = quarter_months.get(q_num, 1)
                release_date = date(year, month, 15)  # Middle of the month
            else:
                release_date = date.today()
            
            description = f"Quarterly release for {quarter}"
            films_added = self.add_film_batch(
                num_films, category_focus, description, release_date
            )
            
            self.disconnect()
            return films_added
            
        except Exception as e:
            logger.error(f"Error generating quarterly films: {e}")
            if self.conn:
                self.disconnect()
            return 0


def main():
    """Main function for testing"""
    # This would typically be called from master_simulation.py
    pass


if __name__ == '__main__':
    main()