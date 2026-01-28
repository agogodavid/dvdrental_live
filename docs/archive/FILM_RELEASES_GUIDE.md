# Film Release Schedule - Master Simulation

## Overview

The master simulation now includes **realistic film generation** with:
- 🎬 **Scheduled film releases** at specific weeks
- 📚 **Genre-matched titles** (Action, Comedy, Drama, Horror, etc.)
- 📝 **Realistic descriptions** and metadata
- 📊 **Automatic inventory allocation** to all stores
- 👥 **Staff tracking** for inventory purchases

## How It Works

### Film Title Generation

Each film generated includes:
- **Title**: Realistic, genre-appropriate titles generated from templates
- **Description**: Short, compelling summary matching the film category
- **Duration**: Genre-typical runtime (80-145 minutes)
- **Cost**: Realistic replacement cost ($14-26)
- **Rental Rate**: 20% of replacement cost
- **Rating**: Genre-appropriate MPAA rating

### Supported Film Categories

```
Action     - High octane adventures with agents and missions
Comedy     - Humorous tales and romantic comedies
Drama      - Serious stories about relationships and growth
Horror     - Supernatural scares and psychological terror
Romance    - Love stories and passionate encounters
Sci-Fi     - Future worlds and technological marvels
Animation  - Family-friendly animated adventures
Family     - Wholesome entertainment for all ages
Thriller   - Suspense and plot twists
```

### Example Generated Titles

**Action:**
- "Mission: Tokyo"
- "Escape from Moscow"
- "Operation Vendetta"

**Comedy:**
- "Crazy Love"
- "The Hilarious Wedding"
- "Office Chaos"

**Drama:**
- "Letters to Grace"
- "When Sarah Returns"
- "The Weight of Secrets"

**Horror:**
- "The Curse Awakens"
- "Haunted House"
- "Possession"

**Romance:**
- "Love in Paris"
- "Second Chance"
- "Eternal Heart"

**Sci-Fi:**
- "The Last Protocol"
- "Quantum Wars"
- "Time Jump"

**Animation:**
- "The Adventures of Luna"
- "Journey to Wonderland"
- "The Dragon Kingdom"

**Family:**
- "The Amazing Adventure"
- "Ollie's Christmas"
- "Together Always"

**Thriller:**
- "The Conspiracy Game"
- "Edge of Truth"
- "Silent Protocol"

## Configuration

### Adding Film Releases

Edit `FILM_RELEASES` in `master_simulation.py`:

```python
FILM_RELEASES = [
    (0, 0, None, "Initial catalog loaded by generator"),
    (8, 3, "Action", "Q4 2001 - Action blockbusters"),
    (16, 3, "Comedy", "Q1 2002 - Comedy releases"),
    # Add more as needed
]
```

Format: `(week_number, num_films, category_focus, description)`

### Parameters:

- **week_number**: Which week to release films (0 = simulation start)
- **num_films**: How many films to generate
- **category_focus**: Primary category (or None for mixed)
- **description**: Human-readable description

### Example: Add Films for 10 Year Simulation

```python
FILM_RELEASES = [
    (0, 0, None, "Initial catalog"),
    (8, 3, "Action", "Q4 2001 - Action blockbusters"),
    (20, 3, "Comedy", "Q1 2002 - Comedy releases"),
    (32, 4, "Drama", "Q2 2002 - Award-worthy dramas"),
    (44, 3, "Horror", "Q3 2002 - Summer scares"),
    # Continue every ~12 weeks for continuous releases
    (156, 3, "Sci-Fi", "Q1 2004 - Sci-Fi adventures"),
    (168, 3, "Romance", "Q2 2004 - Romance releases"),
    # ... and so on
]
```

## What Gets Created

When films are released, the system automatically:

1. **Creates new films** with realistic titles and metadata
2. **Categorizes them** appropriately
3. **Adds inventory** to all stores (2-3 copies per store)
4. **Tracks staff** who sourced the inventory
5. **Records purchase date** for profitability analysis

### Example Workflow

```
Week 8: Add 3 Action Films
  ├─ Generate Title: "Mission: Tokyo"
  ├─ Generate Description: "An elite agent must stop a criminal mastermind"
  ├─ Set Runtime: 112 minutes
  ├─ Set Cost: $22.50
  ├─ Set Rating: R
  └─ Add 6 inventory copies (2-3 per store)

Week 16: Add 3 Comedy Films
  ├─ Generate Title: "Crazy Love"
  ├─ Generate Description: "A bumbling hero stumbles through romantic mishaps"
  ├─ Set Runtime: 95 minutes
  ├─ Set Cost: $18.50
  ├─ Set Rating: PG-13
  └─ Add 6 inventory copies
```

## Analysis Integration

Films added through releases can be analyzed using:

### View New Films by Category
```sql
SELECT f.title, c.name as category, f.replacement_cost, f.rental_rate
FROM film f
JOIN film_category fc ON f.film_id = fc.film_id
JOIN category c ON fc.category_id = c.category_id
WHERE f.release_year = YEAR(NOW())
ORDER BY f.release_year DESC, c.name;
```

### Track Release Performance
```sql
SELECT 
    c.name as category,
    COUNT(DISTINCT f.film_id) as films_released,
    AVG(f.replacement_cost) as avg_cost,
    SUM(f.rental_rate) * COUNT(DISTINCT r.rental_id) as revenue,
    SUM(f.rental_rate) * COUNT(DISTINCT r.rental_id) - SUM(f.replacement_cost) * COUNT(DISTINCT i.inventory_id) as profit
FROM category c
JOIN film_category fc ON c.category_id = fc.category_id
JOIN film f ON fc.film_id = f.film_id
JOIN inventory i ON f.film_id = i.film_id
LEFT JOIN rental r ON i.inventory_id = r.inventory_id
WHERE YEAR(f.release_year) = YEAR(NOW())
GROUP BY c.category_id
ORDER BY profit DESC;
```

### Analyze Release vs. Inventory Growth
```sql
SELECT 
    YEAR(i.date_purchased) as year,
    MONTH(i.date_purchased) as month,
    COUNT(DISTINCT f.film_id) as unique_films,
    COUNT(i.inventory_id) as total_copies,
    COUNT(DISTINCT r.rental_id) as rentals
FROM inventory i
JOIN film f ON i.film_id = f.film_id
LEFT JOIN rental r ON i.inventory_id = r.inventory_id
GROUP BY YEAR(i.date_purchased), MONTH(i.date_purchased)
ORDER BY year DESC, month DESC;
```

## Sample Simulation Schedule

A balanced 3-year schedule might look like:

```python
FILM_RELEASES = [
    (0, 0, None, "Initial catalog - 1000 films"),
    (8, 3, "Action", "Q4 2001 - Action releases"),
    (16, 3, "Comedy", "Q1 2002 - Comedy releases"),
    (26, 4, "Drama", "Q2 2002 - Award season"),
    (36, 3, "Horror", "Q3 2002 - Summer horror"),
    (48, 4, "Romance", "Q4 2002 - Holiday romance"),
    (60, 3, "Sci-Fi", "Q1 2003 - Sci-Fi adventures"),
    (72, 3, "Animation", "Q2 2003 - Summer animation"),
    (84, 4, "Action", "Q3 2003 - Summer blockbusters"),
    (100, 3, "Family", "Q4 2003 - Holiday family"),
]
```

This distributes roughly 30-35 new films throughout the 3-year period, keeping the catalog fresh while emphasizing seasonal trends.

## Integration with Existing Features

Film releases work seamlessly with:

- ✅ **Inventory Tracking**: New films tracked with `date_purchased` and `staff_id`
- ✅ **Profitability Analysis**: Use `inventory_analysis.py` to compare film performance
- ✅ **Seasonal Demand**: Films interact with seasonal multipliers
- ✅ **Staff Accountability**: Film sourcing tracked to staff members
- ✅ **Batch Analysis**: Group films by release date for cohort analysis

## Learning Opportunities

Students can analyze:

1. **Release Performance**: How do newly released films perform vs. catalog?
2. **Category Trends**: Which genres are most profitable?
3. **Seasonal Impact**: Do releases at specific times perform better?
4. **Inventory Optimization**: Optimal number of copies per new release
5. **Staff Performance**: Comparing staff when stocking new releases

## Troubleshooting

**Issue**: Films not being added
- Check `FILM_RELEASES` configuration
- Verify week numbers match simulation timeline
- Ensure categories exist in database

**Issue**: Missing inventory for films
- Verify stores exist in database
- Check staff availability
- Ensure inventory table has proper constraints

**Issue**: Titles seem too similar
- This is expected! Real video rental stores have many similar titles
- Templates are designed to create realistic variety within categories

**Issue**: Categories don't match my expectations
- Edit `FILM_TEMPLATES` to customize titles and descriptions
- Add new categories as needed
- Rebalance ratings and attributes

## Customization

You can extend the system by:

1. **Adding new categories** to `FILM_TEMPLATES`
2. **Creating custom title templates** per category
3. **Adjusting cost/length ranges** for realism
4. **Modifying descriptions** for your use case
5. **Changing rating distributions** to match your audience

Example: Add a "Westerns" category

```python
"Westerns": {
    "titles": [
        "The {adjective} Gunslinger",
        "{name} at High Noon",
        "Showdown in {location}",
        # ... more templates
    ],
    "adjectives": ["Last", "Greatest", "Final", "Legendary"],
    "nouns": ["Duel", "Standoff", "Outlaw", "Justice"],
    "locations": ["Dodge City", "Tombstone", "Galveston"],
    "descriptions": [
        "A lone gunslinger faces his final duel",
        # ... more descriptions
    ],
    "rating_dist": [("PG", 0.1), ("PG-13", 0.4), ("R", 0.5)],
    "length_range": (90, 140),
    "cost_range": (16, 24)
}
```

## Next Steps

1. **Run simulation** with film releases: `python master_simulation.py`
2. **Analyze results** using `inventory_analysis.py`
3. **Create reports** on film release performance
4. **Customize** film templates for your needs
5. **Design student projects** around film analysis

