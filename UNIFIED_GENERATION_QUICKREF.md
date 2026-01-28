# Quick Reference: Unified Film Generation System

## TL;DR
- ✅ Film title generation now unified across all generators
- ✅ 16 film categories with template-based generation
- ✅ Film volume doubled: 520 → 1,040 films/year
- ✅ Hot category purchases increased 2-3x per week

## What Changed

### Before
```
level_1_basic/generator.py → Procedural (adjectives + nouns)
level_3_master_simulation/film_system/film_generator.py → FILM_TEMPLATES dict
Result: Duplicate code, inconsistent titles
```

### After
```
unified_film_generator.py (NEW)
    ↓
level_1_basic/generator.py ✓
level_3_master_simulation/film_system/film_generator.py ✓
Result: Single source, consistent 16 categories
```

## Film Release Parameters

**Current Config:**
- Market releases: **20/week** (1,040/year)
- Action purchases: **5** per release
- Comedy purchases: **4** per release  
- Drama purchases: **5** per release

**To Adjust:** Edit `shared/configs/config.json`
```json
"market_weekly_releases": 20      // Change this number
"purchase_per_release": 5         // Change per category
```

## Categories Available

| Category | Release Strategy |
|----------|------------------|
| Action | Weeks 0, 12, 24, 36, 48 (5/release) |
| Comedy | Weeks 4, 16, 28, 40 (4/release) |
| Drama | Weeks 8, 20, 32, 44 (5/release) |
| + 13 more | Not on rotation |

## Film Template Files

Location: `level_3_master_simulation/film_system/templates/`
- Each `.txt` file has 13-17 realistic film titles
- Categories: Action, Animation, Comedy, Crime, Documentary, Drama, Family, Fantasy, Horror, Musical, Romance, Sci-Fi, Sports, Thriller, War, Western

## Testing

```bash
python test_unified_generation.py
```

Expected: ✓ 5/5 tests passed

## Key Files

| File | Purpose |
|------|---------|
| `unified_film_generator.py` | Central module (loads templates) |
| `film_generator.py` | Uses unified module |
| `level_1_basic/generator.py` | Uses unified module |
| `templates/*.txt` | Template source files |
| `config.json` | Controls volume/strategy |

## How It Works

1. **At Import**: `unified_film_generator.py` loads all template files
2. **On Generation**: Calls `generate_film_title(category, templates)`
3. **Result**: Returns `(title, description, rating)`
4. **Fallback**: If templates unavailable, uses hardcoded defaults

## Scaling Examples

**Moderate Increase (30% more):**
```json
"market_weekly_releases": 26     // 1,352/year
"purchase_per_release": 5-6      // 6-7 per category
```

**Aggressive Growth (2x volume):**
```json
"market_weekly_releases": 40     // 2,080/year
"purchase_per_release": 8-10     // 10-12 per category
```

## Validation Checklist

Before running simulation:
- [ ] Config updated with desired `market_weekly_releases`
- [ ] Config updated with desired `purchase_per_release` values
- [ ] Ran `python test_unified_generation.py` → all pass
- [ ] Database tables exist (created by film_generator.py)

## Troubleshooting

**Templates not loading?**
- Check: `level_3_master_simulation/film_system/templates/` exists
- Check: All 16 `.txt` files present
- Fallback: Hardcoded templates will be used

**Can't import unified_film_generator?**
- Ensure sys.path includes `level_3_master_simulation/film_system`
- Check file exists and has no syntax errors
- Run: `python test_unified_generation.py` to diagnose

**Low film diversity?**
- Check template files have titles
- Verify config.json loaded correctly
- Each category should have 13-17 titles

---

✅ System ready to use. See `UNIFIED_GENERATION_SUMMARY.md` for full details.
