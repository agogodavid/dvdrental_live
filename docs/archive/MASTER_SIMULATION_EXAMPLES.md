# Master Simulation - Configuration Examples

Complete working examples for different simulation scenarios.

## Example 1: Standard 3-Year Simulation (Oct 2001 - Oct 2004)

**File:** `master_simulation.py` lines 28-54 (no changes needed, this is default)

```python
class SimulationConfig:
    """Configuration for the master simulation"""
    
    # Timeline
    START_DATE = datetime(2001, 10, 1).date()  # October 1, 2001 (Monday)
    TOTAL_WEEKS = 156  # 156 weeks = 3 years
    
    # Inventory Management
    INVENTORY_ADDITIONS = [
        (0, 0, "Initial inventory created by generator"),
        (12, 50, "Q1 2002 - Holiday season restock"),
        (26, 40, "Q2 2002 - Spring refresh"),
        (40, 60, "Q3 2002 - Summer prep"),
        (52, 50, "Q4 2002 - Holiday restock"),
        (66, 40, "Q1 2003 - Winter refresh"),
        (78, 60, "Q2 2003 - Spring collection expansion"),
        (92, 70, "Q3 2003 - Summer blockbuster prep"),
        (104, 50, "Q4 2003 - Holiday season expansion"),
    ]
    
    # Seasonal demand multipliers
    SEASONAL_MULTIPLIERS = {
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
```

**Run:**
```bash
python master_simulation.py
```

**Expected output:**
- 65,000+ rentals
- 1,200+ customers
- 700+ inventory items
- ~30 minute runtime

---

## Example 2: Extended 10-Year Simulation (Oct 2001 - Oct 2011)

**Changes needed:**
1. Line 30: `TOTAL_WEEKS = 520`
2. Lines 32-49: Extend `INVENTORY_ADDITIONS`

```python
class SimulationConfig:
    # Timeline
    START_DATE = datetime(2001, 10, 1).date()
    TOTAL_WEEKS = 520  # 520 weeks = 10 years ← CHANGED
    
    # Inventory Management - EXTENDED
    INVENTORY_ADDITIONS = [
        # Year 1 (Oct 2001 - Oct 2002)
        (0, 0, "Initial inventory created by generator"),
        (12, 50, "Q1 2002 - Holiday season restock"),
        (26, 40, "Q2 2002 - Spring refresh"),
        (40, 60, "Q3 2002 - Summer prep"),
        (52, 50, "Q4 2002 - Holiday restock"),
        
        # Year 2 (Oct 2002 - Oct 2003)
        (66, 40, "Q1 2003 - Winter refresh"),
        (78, 60, "Q2 2003 - Spring collection expansion"),
        (92, 70, "Q3 2003 - Summer blockbuster prep"),
        (104, 50, "Q4 2003 - Holiday season expansion"),
        
        # Year 3 (Oct 2003 - Oct 2004)
        (118, 60, "Q1 2004 - New year expansion"),
        (130, 50, "Q2 2004 - Spring refresh"),
        (144, 70, "Q3 2004 - Summer restock"),
        (156, 60, "Q4 2004 - Holiday preparation"),
        
        # Year 4 (Oct 2004 - Oct 2005)
        (170, 60, "Q1 2005 - New year collection"),
        (182, 50, "Q2 2005 - Spring expansion"),
        (196, 75, "Q3 2005 - Summer boost"),
        (208, 60, "Q4 2005 - Holiday restock"),
        
        # Year 5 (Oct 2005 - Oct 2006)
        (222, 70, "Q1 2006 - Expanded collection"),
        (234, 60, "Q2 2006 - Spring refresh"),
        (248, 80, "Q3 2006 - Summer blockbuster rush"),
        (260, 70, "Q4 2006 - Holiday expansion"),
        
        # Year 6 (Oct 2006 - Oct 2007)
        (274, 70, "Q1 2007 - New inventory cycle"),
        (286, 60, "Q2 2007 - Spring collection"),
        (300, 85, "Q3 2007 - Increased summer demand"),
        (312, 75, "Q4 2007 - Holiday season"),
        
        # Year 7 (Oct 2007 - Oct 2008)
        (326, 75, "Q1 2008 - Expanded collection"),
        (338, 65, "Q2 2008 - Spring refresh"),
        (352, 90, "Q3 2008 - Summer peak"),
        (364, 75, "Q4 2008 - Holiday restock"),
        
        # Year 8 (Oct 2008 - Oct 2009)
        (378, 70, "Q1 2009 - Regular expansion"),
        (390, 65, "Q2 2009 - Spring collection"),
        (404, 85, "Q3 2009 - Summer demand"),
        (416, 75, "Q4 2009 - Holiday season"),
        
        # Year 9 (Oct 2009 - Oct 2010)
        (430, 75, "Q1 2010 - New year collection"),
        (442, 70, "Q2 2010 - Spring expansion"),
        (456, 90, "Q3 2010 - Summer rush"),
        (468, 80, "Q4 2010 - Holiday preparation"),
        
        # Year 10 (Oct 2010 - Oct 2011)
        (482, 80, "Q1 2011 - Inventory refresh"),
        (494, 75, "Q2 2011 - Spring collection"),
        (508, 95, "Q3 2011 - Peak summer season"),
        (520, 85, "Q4 2011 - Final holiday season"),
    ]
    
    # Seasonal pattern (same as before)
    SEASONAL_MULTIPLIERS = { ... }  # Same as Example 1
```

**Run:**
```bash
python master_simulation.py
```

**Expected output:**
- 220,000+ rentals
- 4,000+ customers
- 2,500+ inventory items
- ~2 hour runtime

---

## Example 3: Aggressive Seasonal Pattern (Peak Summer, Quiet Winter)

**Changes:** Line 41-54 (SEASONAL_MULTIPLIERS)

```python
class SimulationConfig:
    START_DATE = datetime(2001, 10, 1).date()
    TOTAL_WEEKS = 156
    INVENTORY_ADDITIONS = [ ... ]  # Same as Example 1
    
    # Aggressive seasonal pattern
    SEASONAL_MULTIPLIERS = {
        1: -30,   # January: Severe slump after holidays
        2: -40,   # February: Dead month
        3: 0,     # March: Start of recovery
        4: 20,    # April: Spring break
        5: 60,    # May: Pre-summer
        6: 150,   # June: HUGE summer demand
        7: 200,   # July: PEAK season
        8: 150,   # August: Late summer
        9: 40,    # September: Back to school
        10: 0,    # October: Neutral
        11: 50,   # November: Thanksgiving weekend
        12: 100,  # December: Holiday rush
    }
```

**Effect:** Extreme seasonal variation - summer rentals 3x higher than winter

---

## Example 4: Consistent Year-Round Demand (Minimal Seasonality)

**Changes:** Line 41-54 (SEASONAL_MULTIPLIERS)

```python
class SimulationConfig:
    START_DATE = datetime(2001, 10, 1).date()
    TOTAL_WEEKS = 156
    INVENTORY_ADDITIONS = [ ... ]  # Same as Example 1
    
    # Flat seasonal pattern (consistent demand)
    SEASONAL_MULTIPLIERS = {
        1: 5,     # January: Slight increase
        2: 0,     # February: Flat
        3: 5,     # March: Slight increase
        4: 5,     # April: Slight increase
        5: 10,    # May: Mid boost
        6: 15,    # June: Modest summer
        7: 15,    # July: Modest summer
        8: 10,    # August: Modest summer
        9: 5,     # September: Slight increase
        10: 0,    # October: Flat
        11: 5,    # November: Slight increase
        12: 20,   # December: Holiday only
    }
```

**Effect:** Year-round demand relatively stable, only December spike

---

## Example 5: Recent Data (2020-2023)

**Changes:** Lines 29-30 (START_DATE)

```python
class SimulationConfig:
    # Timeline
    START_DATE = datetime(2020, 1, 6).date()  # January 6, 2020 (Monday)
    TOTAL_WEEKS = 156  # Jan 2020 - Jan 2023
    
    # Inventory Management (adjust quantities for modern era)
    INVENTORY_ADDITIONS = [
        (0, 0, "Initial inventory created by generator"),
        (12, 80, "Q1 2020 - Initial expansion"),
        (26, 100, "Q2 2020 - COVID streaming surge"),
        (40, 120, "Q3 2020 - Streaming peak"),
        (52, 80, "Q4 2020 - Holiday season"),
        (66, 60, "Q1 2021 - Recovery phase"),
        (78, 50, "Q2 2021 - Inventory adjustment"),
        (92, 60, "Q3 2021 - Summer collection"),
        (104, 55, "Q4 2021 - Holiday restock"),
    ]
    
    # 2020s seasonal pattern (COVID impact)
    SEASONAL_MULTIPLIERS = {
        1: 30,    # January 2020: Starting high (pre-COVID)
        2: 40,    # February: COVID begins
        3: 100,   # March: Lockdowns! Streaming boom
        4: 120,   # April: Peak lockdown
        5: 100,   # May: Still high
        6: 80,    # June: Vaccination begins, outdoors
        7: 70,    # July: Outdoor season
        8: 80,    # August: Late summer
        9: 50,    # September: Back to school
        10: 40,   # October: Return to work
        11: 50,   # November: Thanksgiving
        12: 100,  # December: Holiday + staying in
    }
```

**Effect:** Models realistic streaming boom from COVID pandemic

---

## Example 6: High-Growth Startup (Monthly Inventory Additions)

**Changes:** Line 32-49 (INVENTORY_ADDITIONS)

```python
class SimulationConfig:
    START_DATE = datetime(2001, 10, 1).date()
    TOTAL_WEEKS = 156
    
    # Monthly inventory additions - aggressive growth
    INVENTORY_ADDITIONS = [
        (0, 0, "Initial inventory created by generator"),
        (4, 20, "Month 1 - Initial expansion"),
        (8, 25, "Month 2 - Growth phase"),
        (12, 30, "Month 3 - Accelerating"),
        (16, 35, "Month 4 - Rapid expansion"),
        (20, 40, "Month 5 - Strong growth"),
        (24, 45, "Month 6 - Peak addition"),
        (28, 40, "Month 7 - Continued growth"),
        # ... continue monthly for next 9 months
        (156, 0, "Final week"),
    ]
    
    SEASONAL_MULTIPLIERS = { ... }  # Same as Example 1
```

**Effect:** Startup rapidly adding inventory every month instead of quarterly

---

## Example 7: Declining Business (Inventory Plateaus)

**Changes:** Line 32-49 (INVENTORY_ADDITIONS)

```python
class SimulationConfig:
    START_DATE = datetime(2001, 10, 1).date()
    TOTAL_WEEKS = 156
    
    # Declining additions - inventory growth slows over time
    INVENTORY_ADDITIONS = [
        (0, 0, "Initial inventory created by generator"),
        (12, 100, "Q1 2002 - Strong start"),
        (26, 80, "Q2 2002 - Good business"),
        (40, 60, "Q3 2002 - Slowing growth"),
        (52, 40, "Q4 2002 - Market pressure"),
        (66, 30, "Q1 2003 - Competition rising"),
        (78, 20, "Q2 2003 - Consolidation"),
        (92, 15, "Q3 2003 - Cost cutting"),
        (104, 10, "Q4 2003 - Maintenance only"),
    ]
    
    SEASONAL_MULTIPLIERS = { ... }  # Same as Example 1
```

**Effect:** Models declining business with inventory growth tapering off

---

## Example 8: 5-Year Simulation with Different Start

**Changes:** Lines 29-30

```python
class SimulationConfig:
    START_DATE = datetime(2015, 6, 1).date()  # June 1, 2015
    TOTAL_WEEKS = 260  # 260 weeks = 5 years
    
    INVENTORY_ADDITIONS = [
        # Years 1-5: Extend pattern...
        (0, 0, "Initial inventory"),
        (12, 60, "Q1 2016"),
        # ... 30+ more entries ...
    ]
    
    SEASONAL_MULTIPLIERS = { ... }  # Same as Example 1
```

**Run:**
```bash
python master_simulation.py
```

---

## How to Use These Examples

1. **Choose example** that matches your need
2. **Copy the relevant code** to `master_simulation.py`
3. **Replace lines 28-54** in the original file
4. **Save the file**
5. **Run:** `python master_simulation.py`

## Common Modifications Summary

| Goal | Change |
|------|--------|
| Different duration | `TOTAL_WEEKS = 520` |
| Different start year | `START_DATE = datetime(2010, 1, 4).date()` |
| More/less seasonality | Adjust `SEASONAL_MULTIPLIERS` values |
| More/less frequent inventory | Adjust weeks in `INVENTORY_ADDITIONS` |
| Different growth patterns | Adjust quantities in `INVENTORY_ADDITIONS` |

## Testing Your Configuration

Before running full simulation:

1. **Verify Python syntax:**
   ```bash
   python -m py_compile master_simulation.py
   ```

2. **Check specific values:**
   ```bash
   python -c "from master_simulation import SimulationConfig; \
   print(f'Weeks: {SimulationConfig.TOTAL_WEEKS}'); \
   print(f'Start: {SimulationConfig.START_DATE}')"
   ```

3. **Run small test** (e.g., 52 weeks = 1 year):
   ```python
   # Temporarily change:
   TOTAL_WEEKS = 52  # Test with 1 year
   ```

Then run full simulation when confident.
