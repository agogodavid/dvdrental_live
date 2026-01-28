"""
Unified Film Title Generation Module
Uses template files for consistent, realistic film generation across all contexts
"""

import os
import random
from typing import Tuple, Dict, List
import logging

logger = logging.getLogger(__name__)

# Global cache for loaded templates
_TEMPLATE_CACHE = {}


def load_templates_from_files(templates_dir: str = None) -> Dict:
    """Load all film templates from text files
    
    Args:
        templates_dir: Directory containing template files. 
                      If None, searches in multiple locations.
    
    Returns:
        Dictionary with category templates
    """
    global _TEMPLATE_CACHE
    
    if _TEMPLATE_CACHE:
        return _TEMPLATE_CACHE
    
    # Find templates directory
    if templates_dir is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        possible_dirs = [
            os.path.join(script_dir, 'templates'),
            os.path.join(script_dir, '..', 'film_system', 'templates'),
            os.path.join(script_dir, '..', '..', 'film_templates'),
            'film_templates',
            'templates'
        ]
        
        templates_dir = None
        for d in possible_dirs:
            if os.path.exists(d):
                templates_dir = d
                logger.debug(f"Found templates directory: {d}")
                break
    
    if not templates_dir or not os.path.exists(templates_dir):
        logger.warning(f"Templates directory not found, using hardcoded templates")
        return get_fallback_templates()
    
    templates = {}
    category_map = {
        'action.txt': 'Action',
        'animation.txt': 'Animation',
        'comedy.txt': 'Comedy',
        'crime.txt': 'Crime',
        'documentary.txt': 'Documentary',
        'drama.txt': 'Drama',
        'family.txt': 'Family',
        'fantasy.txt': 'Fantasy',
        'horror.txt': 'Horror',
        'musical.txt': 'Musical',
        'romance.txt': 'Romance',
        'sci_fi.txt': 'Sci-Fi',
        'sports.txt': 'Sports',
        'thriller.txt': 'Thriller',
        'war.txt': 'War',
        'western.txt': 'Western'
    }
    
    for filename, category_name in category_map.items():
        filepath = os.path.join(templates_dir, filename)
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    titles = [line.strip() for line in f if line.strip()]
                
                templates[category_name] = {
                    'titles': titles,
                    'rating_dist': get_rating_for_category(category_name),
                    'length_range': get_length_for_category(category_name),
                    'cost_range': get_cost_for_category(category_name),
                    'descriptions': get_descriptions_for_category(category_name)
                }
                logger.debug(f"Loaded {len(titles)} titles for {category_name}")
            except Exception as e:
                logger.warning(f"Failed to load {filename}: {e}")
        else:
            logger.warning(f"Template file not found: {filepath}")
    
    if templates:
        _TEMPLATE_CACHE = templates
        logger.info(f"Loaded templates for {len(templates)} categories")
    else:
        logger.warning("No template files loaded, using fallback templates")
        _TEMPLATE_CACHE = get_fallback_templates()
    
    return _TEMPLATE_CACHE


def get_fallback_templates() -> Dict:
    """Get hardcoded templates as fallback if template files unavailable"""
    return {
        "Action": {
            "titles": [
                "The {adjective} Agent", "Mission: {location}", "Operation {name}",
                "Escape from {location}", "The {adjective} Warrior", "Hunt for {name}",
                "The Last {name}", "Maximum {adjective}", "The {adjective} Siege"
            ],
            "descriptions": [
                "An elite agent must stop a dangerous criminal mastermind",
                "A former soldier returns for one final mission",
                "Special forces mount a desperate rescue operation"
            ],
            "rating_dist": [("PG-13", 0.4), ("R", 0.6)],
            "length_range": (90, 130),
            "cost_range": (15, 25)
        },
        "Comedy": {
            "titles": [
                "The {adjective} {noun}", "{adjective} Love", "Crazy {name}",
                "The {adjective} Plan", "Love at {location}", "Speed {noun}"
            ],
            "descriptions": [
                "A bumbling hero stumbles through misadventures",
                "Three friends try to navigate modern romance",
                "An ordinary person finds themselves in extraordinary situations"
            ],
            "rating_dist": [("G", 0.1), ("PG", 0.3), ("PG-13", 0.4), ("R", 0.2)],
            "length_range": (85, 110),
            "cost_range": (14, 20)
        },
        "Drama": {
            "titles": [
                "The {noun} of {name}", "When {name} {verb}", "A {adjective} Love",
                "The {name} Years", "Echoes of {noun}", "The Weight of {noun}"
            ],
            "descriptions": [
                "A powerful story of love and loss spanning decades",
                "Two people discover themselves through unexpected connection",
                "A journey of self-discovery and redemption"
            ],
            "rating_dist": [("PG", 0.2), ("PG-13", 0.4), ("R", 0.4)],
            "length_range": (100, 145),
            "cost_range": (16, 24)
        }
    }


def get_rating_for_category(category: str) -> List[Tuple[str, float]]:
    """Get rating distribution for category"""
    rating_map = {
        "Action": [("PG-13", 0.4), ("R", 0.6)],
        "Animation": [("G", 0.5), ("PG", 0.5)],
        "Comedy": [("G", 0.1), ("PG", 0.3), ("PG-13", 0.4), ("R", 0.2)],
        "Crime": [("PG-13", 0.3), ("R", 0.7)],
        "Documentary": [("G", 0.3), ("PG", 0.4), ("R", 0.3)],
        "Drama": [("PG", 0.2), ("PG-13", 0.4), ("R", 0.4)],
        "Family": [("G", 0.7), ("PG", 0.3)],
        "Fantasy": [("PG", 0.4), ("PG-13", 0.6)],
        "Horror": [("PG-13", 0.3), ("R", 0.7)],
        "Musical": [("G", 0.4), ("PG", 0.6)],
        "Romance": [("PG", 0.2), ("PG-13", 0.5), ("R", 0.3)],
        "Sci-Fi": [("PG", 0.3), ("PG-13", 0.5), ("R", 0.2)],
        "Sports": [("G", 0.4), ("PG", 0.6)],
        "Thriller": [("PG-13", 0.3), ("R", 0.7)],
        "War": [("PG-13", 0.3), ("R", 0.7)],
        "Western": [("PG", 0.3), ("PG-13", 0.4), ("R", 0.3)]
    }
    return rating_map.get(category, [("PG-13", 0.5), ("R", 0.5)])


def get_length_for_category(category: str) -> Tuple[int, int]:
    """Get typical film length range for category"""
    length_map = {
        "Action": (90, 130),
        "Animation": (80, 95),
        "Comedy": (85, 110),
        "Crime": (95, 130),
        "Documentary": (60, 120),
        "Drama": (100, 145),
        "Family": (85, 105),
        "Fantasy": (100, 140),
        "Horror": (85, 110),
        "Musical": (100, 135),
        "Romance": (95, 125),
        "Sci-Fi": (100, 140),
        "Sports": (90, 130),
        "Thriller": (95, 130),
        "War": (120, 160),
        "Western": (100, 140)
    }
    return length_map.get(category, (90, 120))


def get_cost_for_category(category: str) -> Tuple[float, float]:
    """Get typical replacement cost range for category"""
    cost_map = {
        "Action": (15, 25),
        "Animation": (14, 22),
        "Comedy": (14, 20),
        "Crime": (15, 24),
        "Documentary": (12, 18),
        "Drama": (16, 24),
        "Family": (14, 20),
        "Fantasy": (16, 26),
        "Horror": (13, 19),
        "Musical": (16, 26),
        "Romance": (14, 22),
        "Sci-Fi": (16, 26),
        "Sports": (13, 20),
        "Thriller": (15, 23),
        "War": (16, 26),
        "Western": (14, 22)
    }
    return cost_map.get(category, (14, 22))


def get_descriptions_for_category(category: str) -> List[str]:
    """Get typical descriptions for category"""
    desc_map = {
        "Action": [
            "An elite agent must stop a dangerous criminal mastermind",
            "A former soldier returns for one final mission",
            "Special forces mount a desperate rescue operation",
            "A lone warrior battles an international conspiracy",
            "A skilled operative infiltrates enemy territory"
        ],
        "Animation": [
            "A magical adventure through a fantastical world",
            "A heartwarming story of friendship and courage",
            "An epic journey to save the kingdom",
            "Colorful characters embark on an exciting quest",
            "A tale of adventure, humor, and life lessons"
        ],
        "Comedy": [
            "A bumbling hero stumbles through misadventures",
            "Three friends try to navigate modern romance",
            "An ordinary person finds themselves in extraordinary situations",
            "A workplace comedy with hilarious mishaps",
            "Friends reunite for a disastrous vacation"
        ],
        "Drama": [
            "A powerful story of love and loss spanning decades",
            "Two people discover themselves through unexpected connection",
            "A journey of self-discovery and redemption",
            "Family secrets threaten to tear them apart",
            "A powerful examination of human resilience"
        ],
        "Horror": [
            "A chilling tale of supernatural terror",
            "Something sinister awakens in the darkness",
            "A group must survive the night of horrors",
            "An ancient evil returns to haunt the living",
            "Unspeakable terror stalks the innocent"
        ],
        "Romance": [
            "Two hearts collide across impossible odds",
            "A second chance at love when least expected",
            "Passion ignites between unlikely partners",
            "A timeless love story spanning generations",
            "Love blooms in the most unexpected place"
        ],
        "Sci-Fi": [
            "A journey to distant worlds and alternate realities",
            "Humanity faces an existential threat from the stars",
            "A visionary discovers technology that changes everything",
            "Time travel creates paradoxes that threaten existence",
            "Space explorers encounter alien civilizations"
        ],
        "Thriller": [
            "A deadly game of cat and mouse ensues",
            "Someone harbors a dangerous secret",
            "Trust no one in this twisted tale of betrayal",
            "A shocking truth threatens to destroy everything",
            "Every moment brings new peril and suspense"
        ]
    }
    return desc_map.get(category, ["An engaging story", "A memorable tale", "An unforgettable experience"])


def generate_film_title(category: str, templates: Dict = None) -> Tuple[str, str, str]:
    """
    Generate a realistic film title, description, and rating based on category
    
    Args:
        category: Film category
        templates: Template dictionary (loads if not provided)
    
    Returns:
        Tuple of (title, description, rating)
    """
    if templates is None:
        templates = load_templates_from_files()
    
    if category not in templates:
        logger.warning(f"Category {category} not in templates, using Drama")
        category = "Drama"
    
    template = templates[category]
    
    # Select title from template
    if template['titles']:
        title_template = random.choice(template['titles'])
    else:
        title_template = f"The {category} Film"
    
    # Try to fill in placeholders if present
    try:
        title = title_template.format(
            adjective=random.choice(['Last', 'Final', 'Ultimate', 'Greatest', 'Deadly']),
            location=random.choice(['Tokyo', 'Berlin', 'Moscow', 'Bangkok', 'Cairo']),
            name=random.choice(['Vendetta', 'Justice', 'Retribution', 'Thunder', 'Phoenix']),
            noun=random.choice(['Knight', 'Dream', 'Heart', 'Soul', 'Truth']),
            verb=random.choice(['Falls', 'Waits', 'Returns', 'Rises', 'Fades'])
        )
    except (KeyError, IndexError):
        title = title_template
    
    # Select description
    description = random.choice(template.get('descriptions', ["A great film"]))
    
    # Select rating
    rating_dist = template.get('rating_dist', [("PG-13", 1.0)])
    rating = random.choices(
        [r[0] for r in rating_dist],
        weights=[r[1] for r in rating_dist],
        k=1
    )[0]
    
    return (title, description, rating)


# Preload templates on import
_TEMPLATES = load_templates_from_files()


if __name__ == "__main__":
    # Test the generator
    for _ in range(5):
        for category in ["Action", "Comedy", "Drama", "Horror", "Sci-Fi"]:
            title, desc, rating = generate_film_title(category)
            print(f"{category:12s} ({rating:5s}): {title}")
