# DVD Rental Simulation - Level Architecture & Organizational Narrative

## 📚 Complete System Overview

This project provides a **progressive learning path** for generating realistic DVD rental databases, from basic SQL fundamentals to advanced business intelligence. Each level builds on the previous, culminating in Level 4's sophisticated 10-year business lifecycle simulation.

---

## 🎯 Level Progression

### **Level 1: Basic Foundations**
**Purpose:** Learn SQL fundamentals with a simple starter database  
**Location:** `level_1_basic/`  
**Key Files:**
- `schema_base.sql` - Core database schema (customer, film, rental, inventory, etc.)
- `generator.py` - Basic data generator with simple patterns

**What You Get:**
- Base database schema with proper foreign keys
- Simple customer and film data
- Basic rental transactions
- Good for: SQL learning, JOIN practice, basic queries

**Run:**
```bash
python generator.py
```

**Output:** Small database (~100 films, ~200 customers, basic transactions)

---

### **Level 2: Incremental Growth**
**Purpose:** Add data incrementally with growth patterns  
**Location:** `level_2_incremental/`  
**Key Files:**
- `incremental_update.py` - Add weeks to existing database

**What You Get:**
- Week-by-week data additions
- Simple growth multipliers (1.02x per week)
- Spike day detection (weekend rushes)
- Seasonal drift support (`--seasonal` flag)

**Features:**
- Database override: `--database my_db`
- Custom seasonal boost: `--seasonal 50` (50% increase)
- Controlled growth: Add 1 week at a time or batch weeks

**Run:**
```bash
# Add 10 weeks to dvdrental_live database
python level_2_incremental/incremental_update.py 10 --database dvdrental_live

# Add 5 weeks with 30% seasonal boost
python level_2_incremental/incremental_update.py 5 --seasonal 30
```

**Output:** Extends existing database with realistic growth patterns

---

### **Level 3: Master Simulation**
**Purpose:** Multi-year simulation with film releases and inventory management  
**Location:** `level_3_master_simulation/`  
**Key Files:**
- `master_simulation.py` - Orchestrates full multi-year simulation
- `film_system/film_generator.py` - Generates realistic films with templates
- `film_system/enhanced_inventory_manager.py` - Strategic inventory purchasing

**What You Get:**
- **Film Releases:** Quarterly new film releases by genre
- **Inventory Purchasing:** Aggressive/stable/seasonal strategies
- **Seasonal Variations:** Month-based demand multipliers (Summer +100%, Winter +20%)
- **Film Templates:** 18 genre-specific templates (Action, Comedy, Drama, Horror, etc.)
- **Auto-Category Creation:** Automatically creates missing categories from templates

**Configuration:** `shared/configs/config.json`
```json
{
  "simulation": {
    "start_date": "2001-12-30",
    "initial_weeks": 260  // 5 years
  },
  "generation": {
    "films_count": 300,
    "base_weekly_transactions": 500
  },
  "inventory_purchasing": {
    "strategy": "aggressive"  // or "stable", "seasonal"
  }
}
```

**Run:**
```bash
# Generate 5 years of data
python level_3_master_simulation/master_simulation.py

# Use different database
python level_3_master_simulation/master_simulation.py --database my_dvdrental_5year
```

**Output:** 
- 5 years of rental data (~130,000 transactions)
- Film library grows from 300 → 500+ films
- Inventory grows strategically based on demand
- Realistic seasonal patterns

---

### **Level 4: Advanced Master (10-Year Business Lifecycle)** ⭐
**Purpose:** Complete enterprise-grade simulation with business lifecycle and advanced features  
**Location:** `level_4_advanced_master/`  
**Key File:** `master_simulation.py` - **THE DEFINITIVE 10-YEAR TOOL**

**What You Get (Everything from Level 3 PLUS):**

#### 🏢 **Business Lifecycle Modeling**
Four distinct phases over 10 years:
1. **Growth Phase (Years 1-2, Weeks 1-104)**
   - Aggressive expansion: +2.5% volume growth per week
   - Heavy inventory purchasing (50 items/quarter)
   - Customer acquisition focus
   
2. **Plateau Phase (Years 3-6, Weeks 105-312)**
   - Stable operations: 0% growth, sustained volume
   - Moderate inventory additions (30 items every 4 months)
   - Market saturation reached
   
3. **Decline Phase (Years 7-8, Weeks 313-416)**
   - Market contraction: -0.5% volume decline per week
   - Minimal inventory (15 items every 5 months)
   - Streaming competition impact
   
4. **Reactivation Phase (Years 9-10, Weeks 417-520)**
   - Recovery strategy: +1.5% growth per week
   - Strategic inventory refresh (25 items/quarter)
   - Niche market pivot

#### 👥 **Customer Segmentation & Churn**
Four customer segments with realistic behavior:
- **Super Loyal (10%):** 5% churn, 3.0x activity, 200-week lifetime
- **Loyal (20%):** 15% churn, 2.0x activity, 100-week lifetime
- **Average (30%):** 40% churn, 1.0x activity, 50-week lifetime
- **Occasional (40%):** 80% churn, 0.3x activity, 20-week lifetime

**Customer Reactivation:** 25% of churned customers can be reactivated starting Week 416

#### 💰 **Late Fees & Accounts Receivable (AR)**
- **Late Fees:** $1.50/day for rentals exceeding rental_duration
- **AR Tracking:** Maintains `customer_ar` table with balances
- **AR Aging Buckets:** 
  - Current (0-29 days overdue)
  - 30 Days (30-59 days)
  - 60 Days (60-89 days)
  - 90+ Days (90+ days)
- **Automatic Calculation:** Processes after every 4-week batch

#### 📦 **Inventory Status Tracking**
Tracks inventory lifecycle:
- **Available:** Ready to rent
- **Rented:** Currently checked out
- **Damaged:** Needs repair (2% probability)
- **Missing:** Lost items (1% probability)
- **Maintenance:** Routine maintenance (3% frequency)

#### 🌡️ **Advanced Seasonality**
Enhanced seasonal modeling with volatility:
- Winter (Nov-Jan): +25% base multiplier ±5% volatility
- Spring (Mar-May): +10% base multiplier
- Summer (Jun-Aug): +30% peak season multiplier
- Fall (Sep-Oct): +15% multiplier

**Configuration:** `shared/configs/config_10year_advanced.json`
```json
{
  "simulation": {
    "start_date": "2001-12-30",
    "initial_weeks": 520  // 10 years
  },
  "generation": {
    "base_weekly_transactions": 400,
    "business_lifecycle": {
      "growth_phase_weeks": 104,
      "plateau_phase_weeks": 208,
      "decline_phase_weeks": 104,
      "reactivation_phase_weeks": 104
    },
    "volume_modifiers": {
      "growth_factor": 0.025,
      "plateau_factor": 0.0,
      "decline_factor": -0.005,
      "reactivation_factor": 0.015
    },
    "customer_segments": { /* ... */ },
    "advanced_features": {
      "enable_late_fees": true,
      "enable_ar_tracking": true,
      "enable_inventory_status_tracking": true,
      "enable_seasonality": true,
      "enable_customer_churn": true,
      "late_fees": {
        "daily_rate": 1.50
      }
    }
  }
}
```

**Run:**
```bash
# Generate 10 years of advanced data (default database: dvdrental_10year_advanced)
python level_4_advanced_master/master_simulation.py

# Use custom database
python level_4_advanced_master/master_simulation.py --database my_10year_data

# Override seasonality (50% boost across all months)
python level_4_advanced_master/master_simulation.py --season 50
```

**Output:**
- **~200,000+ rental transactions** over 10 years
- **500+ films** with quarterly genre-focused releases
- **1,000+ inventory items** with strategic purchasing patterns
- **Customer lifecycle data** (acquisitions, churn, reactivations)
- **Late fees table** with $X,XXX in outstanding fees
- **Customer AR table** with aging analysis
- **Inventory status tracking** for asset management
- **Yearly performance metrics** showing business lifecycle
- **Customer segment analysis** (Heavy/Regular/Occasional/Light users)

---

## 📊 Feature Comparison Matrix

| Feature | Level 1 | Level 2 | Level 3 | Level 4 |
|---------|---------|---------|---------|---------|
| **Basic Schema** | ✅ | ✅ | ✅ | ✅ |
| **Simple Transactions** | ✅ | ✅ | ✅ | ✅ |
| **Growth Multipliers** | ❌ | ✅ | ✅ | ✅ |
| **Seasonal Variations** | ❌ | Basic | Advanced | Advanced+ |
| **Film Releases** | ❌ | ❌ | ✅ | ✅ |
| **Inventory Strategy** | ❌ | ❌ | ✅ | ✅ |
| **Film Templates** | ❌ | ❌ | ✅ | ✅ |
| **Auto-Category Creation** | ❌ | ❌ | ✅ | ✅ |
| **Business Lifecycle** | ❌ | ❌ | ❌ | ✅ |
| **Customer Segments** | ❌ | ❌ | ❌ | ✅ |
| **Customer Churn** | ❌ | ❌ | ❌ | ✅ |
| **Late Fees** | ❌ | ❌ | ❌ | ✅ |
| **AR Tracking** | ❌ | ❌ | ❌ | ✅ |
| **Inventory Status** | ❌ | ❌ | ❌ | ✅ |
| **Reactivation Logic** | ❌ | ❌ | ❌ | ✅ |
| **Duration** | Days | Weeks | Years | 10 Years |
| **Transactions** | ~100 | ~1,000 | ~50,000+ | ~200,000+ |

---

## 🔄 How Configs Move Forward

### **config.json → config_10year_advanced.json Evolution**

**Base Config (`config.json`)** - Used by Levels 1-3:
```json
{
  "mysql": { "database": "dvdrental_live" },
  "simulation": { "initial_weeks": 260 },  // 5 years
  "generation": {
    "base_weekly_transactions": 500,
    "films_count": 300
  }
}
```

**Advanced Config (`config_10year_advanced.json`)** - Level 4 ONLY:
```json
{
  "mysql": { "database": "dvdrental_10year_advanced" },
  "simulation": { "initial_weeks": 520 },  // 10 years
  "generation": {
    "base_weekly_transactions": 400,
    
    // NEW: Business lifecycle phases
    "business_lifecycle": {
      "growth_phase_weeks": 104,
      "plateau_phase_weeks": 208,
      "decline_phase_weeks": 104,
      "reactivation_phase_weeks": 104
    },
    
    // NEW: Volume modifiers per phase
    "volume_modifiers": {
      "growth_factor": 0.025,
      "plateau_factor": 0.0,
      "decline_factor": -0.005,
      "reactivation_factor": 0.015
    },
    
    // NEW: Customer segmentation
    "customer_segments": {
      "super_loyal": { "percentage": 0.10, "churn_rate": 0.05, ... },
      "loyal": { "percentage": 0.20, "churn_rate": 0.15, ... },
      "average": { "percentage": 0.30, "churn_rate": 0.40, ... },
      "occasional": { "percentage": 0.40, "churn_rate": 0.80, ... }
    },
    
    // NEW: Reactivation settings
    "reactivation": {
      "enable_reactivation": true,
      "reactivation_probability": 0.25,
      "reactivation_start_week": 416,
      "reactivation_duration_weeks": 104
    },
    
    // NEW: Advanced features (Level 4 only)
    "advanced_features": {
      "enable_late_fees": true,
      "enable_ar_tracking": true,
      "enable_inventory_status_tracking": true,
      "enable_seasonality": true,
      
      "late_fees": {
        "daily_rate": 1.50,
        "calculation_frequency_days": 1,
        "overdue_threshold_days": 0
      },
      
      "seasonality": {
        "winter_multiplier": 1.25,
        "spring_multiplier": 1.10,
        "summer_multiplier": 1.30,
        "fall_multiplier": 1.15,
        "volatility": 0.05
      },
      
      "inventory_status": {
        "damage_probability": 0.02,
        "loss_probability": 0.01,
        "maintenance_frequency": 0.03
      },
      
      "customer_behavior": {
        "overdue_rental_probability": 0.08,
        "max_simultaneous_rentals": {
          "super_loyal": 10,
          "loyal": 6,
          "average": 4,
          "occasional": 2
        }
      }
    }
  }
}
```

### **Key Differences:**

1. **Duration:** 260 weeks (5 yrs) → 520 weeks (10 yrs)
2. **Business Phases:** None → 4 distinct phases with modifiers
3. **Customer Modeling:** Simple → 4 segments with churn/reactivation
4. **Advanced Features:** None → Late fees, AR, inventory status
5. **Configuration Complexity:** Simple → Sophisticated business logic

---

## 🎓 When to Use Each Level

### **Use Level 1 if:**
- Learning SQL basics (JOINs, WHERE, GROUP BY)
- Teaching database fundamentals
- Need small test dataset quickly
- Prototyping queries

### **Use Level 2 if:**
- Need to extend existing database
- Want controlled week-by-week growth
- Testing incremental data pipelines
- Need specific date ranges

### **Use Level 3 if:**
- Need multi-year dataset (2-5 years)
- Want film release patterns
- Need inventory purchasing strategies
- Teaching advanced SQL (window functions, CTEs)
- Building reporting dashboards

### **Use Level 4 if:** ⭐
- **Need complete 10-year business simulation**
- **Teaching business intelligence / data warehousing**
- **Building predictive models (churn, forecasting)**
- **Demonstrating advanced analytics (AR aging, cohort analysis)**
- **Data science projects with realistic business data**
- **Portfolio projects requiring sophisticated datasets**

---

## 🚀 Quick Start Guide

### **For SQL Learning (Beginner):**
```bash
# Start with Level 1
python generator.py
```

### **For Multi-Year Projects (Intermediate):**
```bash
# Use Level 3 for 5 years of data
python level_3_master_simulation/master_simulation.py
```

### **For Complete 10-Year Simulation (Advanced):** ⭐
```bash
# Level 4 is your definitive tool
python level_4_advanced_master/master_simulation.py
```

---

## 📈 Sample Outputs by Level

### **Level 1 Output:**
```
✓ 100 films created
✓ 200 customers created
✓ 500 inventory items
✓ 1,000 rental transactions
Database: dvdrental_live
```

### **Level 2 Output:**
```
✓ Added 10 weeks
✓ 5,423 total transactions
✓ Seasonal boost: +30%
✓ 2 spike days detected
```

### **Level 3 Output:**
```
✓ 130,000 rental transactions
✓ 450 films (150 added via releases)
✓ 850 inventory items
✓ 5 years of data (2002-2006)
✓ Quarterly film releases
✓ Strategic inventory growth
```

### **Level 4 Output:** ⭐
```
╔══════════════════════════════════════════════════════════╗
║    LEVEL 4 - ADVANCED SIMULATION SUCCESSFUL!            ║
╚══════════════════════════════════════════════════════════╝

✓ Total Rentals: 203,547
✓ Active Customers: 1,247
✓ Total Inventory Items: 1,123
✓ Inventory Growth: 55.3% (from 723 to 1,123)
✓ Data Range: 2001-12-24 to 2011-12-18
✓ Currently Checked Out: 234 items
✓ Average Rentals per Week: 391

📊 Yearly Performance:
   Year 2002: 18,234 rentals (avg 4.2 days)
   Year 2003: 24,156 rentals (avg 4.5 days)
   Year 2004: 26,789 rentals (avg 4.3 days)
   Year 2005: 27,234 rentals (avg 4.4 days)
   Year 2006: 26,890 rentals (avg 4.6 days)
   Year 2007: 25,678 rentals (avg 4.7 days)
   Year 2008: 23,456 rentals (avg 4.8 days)
   Year 2009: 21,234 rentals (avg 4.9 days)
   Year 2010: 18,890 rentals (avg 5.0 days)
   Year 2011: 10,986 rentals (avg 5.1 days)

👥 Customer Segments:
   Heavy Users: 124 customers (avg 78.3 rentals each)
   Regular Users: 312 customers (avg 35.7 rentals each)
   Occasional Users: 456 customers (avg 12.4 rentals each)
   Light Users: 355 customers (avg 3.2 rentals each)

💰 Late Fees & Accounts Receivable:
   Overdue Rentals: 1,847
   Total Late Fees Owed: $12,456.50
   Customers with AR: 234
   Total AR Balance: $11,234.75
   AR Aging Breakdown:
      current: 89 customers
      30_days: 67 customers
      60_days: 45 customers
      90_days_plus: 33 customers

Database 'dvdrental_10year_advanced' contains 10 years of
sophisticated business simulation with:
  • Complete business lifecycle (growth → plateau → decline → reactivation)
  • Advanced customer segmentation and behavior modeling
  • Late fees and accounts receivable tracking
  • Inventory status management
  • Realistic seasonal variations and market dynamics
  • Customer churn and reactivation patterns
  • Comprehensive business intelligence data
```

---

## 🎯 Summary: Why Level 4 is the Definitive Tool

**Level 4 `master_simulation.py` is your ONE SCRIPT for complete 10-year simulations because:**

1. ✅ **All-in-One:** Combines everything from Levels 1-3 + advanced features
2. ✅ **Business Lifecycle:** Real-world growth/plateau/decline/reactivation phases
3. ✅ **Customer Intelligence:** Segmentation, churn, reactivation modeling
4. ✅ **Financial Tracking:** Late fees and AR with aging analysis
5. ✅ **Asset Management:** Inventory status lifecycle tracking
6. ✅ **Configuration-Driven:** Enable/disable features via JSON flags
7. ✅ **Production-Ready:** Performance optimizations, batch processing, error handling
8. ✅ **Analytics-Friendly:** Generates data perfect for BI tools, dashboards, ML models

**You will only ever need to run Level 4 for generating 10-year datasets.**

---

## 📝 Final Notes

- **Backward Compatibility:** Levels 1-3 remain completely untouched and functional
- **Progressive Learning:** Each level builds naturally on the previous
- **Level 4 Independence:** Can run standalone - does not require running Levels 1-3 first
- **Config Flexibility:** Easily adjust business phases, segments, and features via JSON
- **Enterprise-Grade:** Level 4 produces datasets suitable for professional portfolios

**Start with Level 1 for learning. Graduate to Level 4 for complete business simulations.** 🚀
