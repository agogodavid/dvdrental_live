# Film Release Feature - Quick Reference

## TL;DR

Master simulation now **generates realistic films** with genre-matched titles during the simulation. Films are automatically added to inventory with tracking.

## Quick Setup

### Default Film Releases (Already Configured)

```python
# 9 scheduled film releases across 3 years
(8, 3, "Action", "Q4 2001 - Action blockbusters")
(16, 3, "Comedy", "Q1 2002 - Comedy releases")
(26, 4, "Drama", "Q2 2002 - Award-worthy dramas")
(36, 3, "Horror", "Q3 2002 - Summer scares")
(48, 4, "Romance", "Q4 2002 - Holiday romances")
(60, 3, "Sci-Fi", "Q1 2003 - Sci-Fi adventures")
(72, 3, "Animation", "Q2 2003 - Animated features")
(84, 4, "Action", "Q3 2003 - Summer action")
(100, 3, "Family", "Q4 2003 - Holiday family")
```

### Run the Simulation

```bash
python master_simulation.py
```

Films will be auto-generated at scheduled weeks. 🎬

## What Gets Generated

Example films from each category:

| Category | Sample Title | Rating | Runtime | Cost |
|----------|-------------|--------|---------|------|
| Action | "Mission: Tokyo" | R | 112m | $22.50 |
| Comedy | "Crazy Love" | PG-13 | 95m | $18.50 |
| Drama | "When Sarah Returns" | PG-13 | 118m | $21.00 |
| Horror | "Haunted House" | R | 105m | $19.75 |
| Romance | "Love in Paris" | PG | 110m | $20.00 |
| Sci-Fi | "The Last Protocol" | PG-13 | 125m | $24.50 |
| Animation | "Luna's Adventure" | G | 95m | $22.00 |
| Family | "Christmas Wonder" | G | 85m | $18.00 |
| Thriller | "Edge of Truth" | R | 115m | $21.50 |

## Customize Film Releases

### Edit Release Schedule

In `master_simulation.py`, find `FILM_RELEASES`:

```python
FILM_RELEASES = [
    (week, num_films, "Category", "Description"),
]
```

Example: Add more sci-fi films in Q2

```python
(75, 5, "Sci-Fi", "Q2 2003 - Extended Sci-Fi collection")
```

### Add More Releases (10+ Year Simulation)

For extended simulations, add more entries:

```python
FILM_RELEASES = [
    # ... existing entries ...
    (116, 3, "Thriller", "Q1 2004 - Thriller releases"),
    (128, 3, "Comedy", "Q2 2004 - Comedy hits"),
    (140, 4, "Drama", "Q3 2004 - Award films"),
    (156, 3, "Action", "Q4 2004 - Holiday action"),
    # Continue pattern...
]
```

## Supported Categories

```
Action       - High-octane adventures
Comedy       - Humorous stories
Drama        - Serious narratives
Horror       - Scares and suspense
Romance      - Love stories
Sci-Fi       - Future/space themes
Animation    - Animated features
Family       - All-ages entertainment
Thriller     - Suspenseful plots
```

## Data Generated

Each film release creates:

✅ **New Films** (title, description, rating, runtime, cost)
✅ **Film Categories** (linked to appropriate genre)
✅ **Inventory** (2-3 copies per store)
✅ **Purchase Tracking** (date_purchased, staff_id for analysis)

## Analyze Films

### View All Released Films

```sql
SELECT f.title, c.name as category, f.replacement_cost, f.rental_rate
FROM film f
JOIN film_category fc ON f.film_id = fc.film_id
JOIN category c ON fc.category_id = c.category_id
WHERE YEAR(f.release_year) = 2002
ORDER BY c.name;
```

### Compare New vs. Old Films

```sql
SELECT 
    CASE WHEN f.release_year >= 2003 THEN 'New' ELSE 'Catalog' END as film_type,
    COUNT(*) as num_films,
    AVG(f.replacement_cost) as avg_cost,
    COUNT(r.rental_id) as total_rentals
FROM film f
LEFT JOIN inventory i ON f.film_id = i.film_id
LEFT JOIN rental r ON i.inventory_id = r.inventory_id
GROUP BY film_type;
```

### Track Release Success

```sql
SELECT 
    c.name as category,
    COUNT(DISTINCT f.film_id) as films,
    ROUND(SUM(f.rental_rate) * COUNT(r.rental_id), 2) as revenue,
    ROUND(SUM(f.rental_rate) * COUNT(r.rental_id) - SUM(f.replacement_cost), 2) as profit
FROM category c
JOIN film_category fc ON c.category_id = fc.category_id
JOIN film f ON fc.film_id = f.film_id
JOIN inventory i ON f.film_id = i.film_id
LEFT JOIN rental r ON i.inventory_id = r.inventory_id
WHERE YEAR(f.release_year) = 2003
GROUP BY c.category_id
ORDER BY profit DESC;
```

## Integration

Works seamlessly with:
- ✅ `inventory_analysis.py` - Analyze film batch profitability
- ✅ `inventory_manager.py` - Manual film/inventory additions
- ✅ `INVENTORY_ANALYSIS_GUIDE.md` - SQL analysis patterns
- ✅ Staff/date tracking for all films

## Example Analysis: Film Release Strategy

Students can analyze:

1. **Best time to release films?** (seasonal performance)
2. **Optimal inventory copies?** (rentals per copy)
3. **Most profitable category?** (ROI by genre)
4. **Staff performance?** (who stocks bestsellers?)
5. **Shelf life?** (how long films remain popular?)

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No films appearing | Check `FILM_RELEASES` week numbers |
| Wrong category | Verify category names in `FILM_TEMPLATES` |
| Titles too similar | Expected! Real stores have similar titles |
| Missing inventory | Ensure stores/staff exist in DB |

## File Reference

| File | Purpose |
|------|---------|
| `master_simulation.py` | Core simulation (contains film release logic) |
| `FILM_RELEASES_GUIDE.md` | Detailed film generation documentation |
| `FILM_RELEASES_QUICKSTART.md` | This file |
| `FILM_TEMPLATES` (in master_simulation.py) | Title/description templates |

## Next Steps

1. ✅ Run simulation: `python master_simulation.py`
2. ✅ Analyze: `python inventory_analysis.py`
3. ✅ Extend: Add more film releases for longer simulations
4. ✅ Customize: Modify templates to match your needs
5. ✅ Teach: Design student projects around film data

---

See `FILM_RELEASES_GUIDE.md` for complete documentation!
