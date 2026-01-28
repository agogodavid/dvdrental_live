# Season Argument Update - Numeric Boost Multiplier

## Summary
✅ **Updated `--season` argument across all levels to accept numeric boost percentage instead of yes/no**

The `--season` argument now accepts percentage values to control seasonal demand boost. For example:
- `--season 50` = 50% seasonal boost (1.5x multiplier)
- `--season 0` = No seasonal boost (1.0x multiplier, neutral)
- `--season -25` = 25% seasonal reduction (0.75x multiplier)

## Changes Made

### Level 1 - `level_1_basic/generator.py`
- ✅ Changed `--season` argument type from `str` to `float`
- ✅ Applied seasonal boost to `generator.seasonal_drift` attribute
- ✅ Logs seasonal boost percentage when provided
- **Usage:**
  ```bash
  python generator.py --season 50           # 50% boost
  python generator.py --season 0            # No seasonality
  python generator.py --database test --season 30
  ```

### Level 3 - `level_3_master_simulation/master_simulation.py`
- ✅ Changed `--season` argument type from `str` to `float`
- ✅ When `--season` is provided, overrides automatic date-based seasonal calculation
- ✅ Applies fixed seasonal boost throughout simulation
- **Usage:**
  ```bash
  python master_simulation.py --season 40           # 40% boost for all weeks
  python master_simulation.py --season 0            # No seasonality (neutral)
  python master_simulation.py --database test --season 25
  ```

### Level 4 - `level_4_advanced_master/run_advanced_simulation.py`
- ✅ Changed `--season` argument type from `str` to `float`
- ✅ Converts percentage to multiplier: `seasonal_multiplier = 1.0 + (percentage / 100.0)`
- ✅ Applies boost to each week's calculation
- **Usage:**
  ```bash
  python run_advanced_simulation.py --season 50         # 50% boost
  python run_advanced_simulation.py --season 0          # No seasonality
  python run_advanced_simulation.py --config config_10year.json --season 35
  ```

## Seasonal Boost Calculation

The seasonal boost is applied as a multiplier:
```
final_volume = base_volume × (1 + boost_percentage / 100)

Examples:
--season 50  → 1 + (50 / 100) = 1.5x (50% increase)
--season 0   → 1 + (0 / 100) = 1.0x (no change)
--season -25 → 1 + (-25 / 100) = 0.75x (25% decrease)
```

## Testing Examples

### Basic Testing
```bash
# Test Level 1 with 50% boost
cd level_1_basic
python generator.py --season 50 --database test_season_50

# Test Level 1 with no seasonality
python generator.py --season 0 --database test_season_0
```

### Master Simulation Testing
```bash
# Test Level 3 with 30% boost
cd level_3_master_simulation
python master_simulation.py --season 30 --database test_master_30

# Test Level 3 with no seasonality
python master_simulation.py --season 0 --database test_master_neutral
```

### Advanced Simulation Testing
```bash
# Test Level 4 with 40% boost
cd level_4_advanced_master
python run_advanced_simulation.py --season 40 --database test_adv_40

# Test Level 4 with 20% reduction
python run_advanced_simulation.py --season -20 --database test_adv_decline
```

## Documentation Updates

- ✅ [README.md](README.md) - Updated with numeric examples
- ✅ [level_1_basic/README.md](level_1_basic/README.md) - Updated argument reference
- ✅ [level_3_master_simulation/README.md](level_3_master_simulation/README.md) - Updated with numeric examples
- ✅ [level_4_advanced_master/README.md](level_4_advanced_master/README.md) - Updated argument table
- ✅ [shared/configs/README.md](shared/configs/README.md) - Updated argument reference table

## Key Differences from Previous Implementation

| Previous | Current |
|----------|---------|
| `--season yes` | `--season 0` to `--season 100+` (numeric percentage) |
| `--season no` | `--season 0` (no seasonal boost) |
| Boolean logic | Percentage-based multiplier |
| Enabled/disabled | Boost amount control |

## Verification

All Python files compile successfully:
- ✅ level_1_basic/generator.py
- ✅ level_3_master_simulation/master_simulation.py
- ✅ level_4_advanced_master/run_advanced_simulation.py

## Default Behavior

**Level 1**: No seasonal boost by default (0%)
**Level 3**: Automatic date-based seasonal calculation (unless --season overrides)
**Level 4**: Config-based seasonal variations (unless --season overrides)

## Backward Compatibility

❌ **Not backward compatible** - Old yes/no values will now be interpreted as percentages:
- `--season yes` (old) = `--season NaN` (new) - Invalid
- `--season no` (old) = `--season NaN` (new) - Invalid

**Migration Path**: Use `--season 0` for no seasonality, `--season 50` for 50% boost, etc.
