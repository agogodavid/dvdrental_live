# Film Title Generation Strategy

## Overview
The system has **two different film title generation approaches** for different contexts:

1. **Level 1 (generator.py)** - Basic procedural title generation
2. **Level 3 (film_system/film_generator.py)** - Template-based generation from category files

---

## Path 1: Level 1 Basic Generator (generator.py)

### Usage
- **When**: Initial database seeding (Week 0)
- **Called from**: `run_initial_setup()` → `initialize_and_seed()` → `seed_films()`
- **Films generated**: 500 initial films (configurable)

### Method
**Procedural Title Generation** - Random combinations of components:

```python
film_adjectives = ['The', 'A', 'Silent', 'Crazy', 'Dark', 'Bright', ...]
film_nouns = ['Matrix', 'Dream', 'Knight', 'Voyage', 'Dynasty', ...]
film_modifiers = ['', ' Returns', ' Reloaded', ' Revolutions', ...]

# Example output: "The Silent Knight", "Crazy Dream Returns", etc.
```

### Characteristics
- ✅ Simple and fast
- ✅ Generates unique combinations
- ✅ Release years based on simulation start date (10 years before to 1 year before)
- ❌ Not category-specific (random category assignment)
- ❌ No template-based genre matching

### Code Location
- File: [level_1_basic/generator.py](level_1_basic/generator.py#L174)
- Method: `seed_films(count, start_date)`
- Lines: 174-260

---

## Path 2: Level 3 Master Simulation (film_system/film_generator.py)

### Usage
- **When**: During simulation (weekly market releases + hot category purchases)
- **Called from**: `master_simulation.py` → `add_film_batch()` → `FilmGenerator.add_film_batch()`
- **Films generated**: 8/week × 52 weeks = 416 market releases + hot category purchases

### Method
**Template-Based Title Generation** - Uses category-specific templates:

```python
FILM_TEMPLATES = {
    "Action": {
        "titles": ["The {adjective} Agent", "Mission: {location}", ...],
        "adjectives": ["Last", "Final", "Ultimate", ...],
        "locations": ["Tokyo", "Berlin", "Moscow", ...],
        "names": ["Vendetta", "Retribution", ...],
        "descriptions": [...],
        "rating_dist": [("PG-13", 0.4), ("R", 0.6)],
        "length_range": (90, 130),
        "cost_range": (15, 25)
    },
    "Comedy": { ... },
    "Drama": { ... },
    # ... more categories
}
```

### Function: `generate_film_title(category)`

```python
def generate_film_title(category: str) -> Tuple[str, str, str]:
    """
    Generate title, description, and rating based on category
    Returns: (title, description, rating)
    """
    template = FILM_TEMPLATES[category]
    
    # Select components from template
    title_pattern = random.choice(template["titles"])
    # Fill in placeholders with category-specific values
    title = title_pattern.format(
        adjective=random.choice(template["adjectives"]),
        location=random.choice(template["locations"]),
        ...
    )
    description = random.choice(template["descriptions"])
    rating = random.choice(template["rating_dist"])[0]
    
    return (title, description, rating)
```

### Characteristics
- ✅ Category-specific titles ("Mission: Tokyo" for Action, "Crazy Love" for Comedy)
- ✅ Realistic descriptions matching genre
- ✅ Proper rating distributions by category
- ✅ Configurable film length and cost ranges
- ✅ Can load titles from external files (`film_templates/` directory)
- ❌ More complex, requires template maintenance

### Code Location
- File: [level_3_master_simulation/film_system/film_generator.py](level_3_master_simulation/film_system/film_generator.py#L20)
- Constants: `FILM_TEMPLATES` (lines 20-250)
- Function: `generate_film_title()` (lines 280+)
- Method: `add_film_batch()` (lines 510-520)

### Categories Supported
Action, Animation, Comedy, Crime, Documentary, Drama, Family, Fantasy, Horror, Musical, Romance, Sci-Fi, Sports, Thriller, War, Western

---

## Integration: How They Connect

### Timeline in Master Simulation:

```
WEEK 0 (Initial Setup - Phase 1)
├─ generator.py::seed_films(500)
│  └─ Creates 500 initial films (1991-2000)
│  └─ Random categories (drama, action, etc.)
│  └─ Procedural titles: "The Silent Knight", etc.
│
WEEKS 1-52 (Incremental Updates - Phase 2)
├─ EVERY WEEK: Market releases
│  ├─ film_generator.py::add_film_batch(8 films, add_inventory=False)
│  │  └─ Calls generate_film_title() for each film
│  │  └─ Category: random selection from all categories
│  │  └─ Template-based titles: "Mission: Tokyo", "Crazy Love", etc.
│  │  └─ Records to film_releases table (market availability)
│  │
├─ HOT CATEGORY WEEKS: Selective purchases
   ├─ Week 0, 12, 24, 36, 48: Action films
   │  └─ film_generator.py::add_film_batch(3 films, category="Action", add_inventory=True)
   │  └─ Template-based Action titles: "The Last Commando", etc.
   │  └─ Records to film_releases + inventory_purchases
   │
   ├─ Week 4, 16, 28, 40: Comedy films
   │  └─ Template-based Comedy titles: "Speed Dating", etc.
   │
   └─ Week 8, 20, 32, 44: Drama films
      └─ Template-based Drama titles: "The Timeless Heart", etc.
```

---

## Data Quality Comparison

### Level 1 Generator (Initial Seed)
- **Quantity**: 500 films
- **Categories**: Random assignment
- **Titles**: Procedural combinations (can be generic)
- **Example**: "The Last Dynasty", "Bright Redemption Returns"
- **Realism**: Medium (works, but not genre-specific)

### Level 3 Film Generator (Weekly Market)
- **Quantity**: 8/week × 52 weeks = 416 market releases
- **Categories**: Focused (hot categories) + random (market background)
- **Titles**: Template-based, category-matched
- **Example**: 
  - Action: "Mission: Bangkok", "The Ultimate Soldier"
  - Comedy: "Crazy Marco in Vegas", "Speed Dating"
  - Drama: "The Timeless Heart", "Echoes of Souls"
- **Realism**: High (realistic genre-appropriate titles)

---

## Configuration & Customization

### To Add New Film Templates
1. Edit [level_3_master_simulation/film_system/film_generator.py](level_3_master_simulation/film_system/film_generator.py#L20)
2. Add to `FILM_TEMPLATES` dictionary:
```python
"MyCategory": {
    "titles": ["Template 1 {adjective}", "Template 2 {name}", ...],
    "adjectives": [...],
    "names": [...],
    "descriptions": [...],
    "rating_dist": [("PG", 0.5), ("R", 0.5)],
    "length_range": (90, 120),
    "cost_range": (15, 20)
}
```

3. Add category to hot_categories in [config.json](shared/configs/config.json)

### To Modify Initial Seed Generation
- Edit [level_1_basic/generator.py](level_1_basic/generator.py#L194)
- Adjust: `film_adjectives`, `film_nouns`, `film_modifiers` lists

---

## Analysis for Students

### Available for Analysis:
- **film_releases table**: All 416 market releases (title, release_date, category)
- **inventory table**: Only purchased films (linked via film_id)
- **inventory_purchases table**: Staff purchasing decisions

### Student Questions:
1. "Of the 416 films released, we only purchased 50. What patterns did we miss?"
2. "Which unpurchased films would have generated more revenue?"
3. "Did our hot category focus strategy work?"
4. "Which staff members made the best purchasing decisions?"
5. "Could a different category strategy have been more profitable?"

---

## Notes

- **incremental_update.py**: Does NOT generate films, only rental transactions
- **Both generators** use `add_film_batch()` signature but with different behavior via `add_inventory` flag
- **Film years**: Always tied to simulation start_date for realism
- **Category matching**: Only in Level 3 (master_simulation phase), Level 1 is random
