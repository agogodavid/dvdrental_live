# 📊 Project Structure Overview

## Complete Repository Organization

The DVD Rental Live project is now organized into **4 progressive levels**, each building on the previous one.

```
dvdrental_live/
│
├── 📚 DOCUMENTATION
│   ├── docs/
│   │   ├── START_HERE.md ⭐ BEGIN HERE
│   │   ├── guides/ (feature-specific docs)
│   │   └── archive/ (legacy documentation - 30+ old docs)
│   ├── README.md (quick reference)
│   └── PROJECT_STRUCTURE.md (this file)
│
├── 🎓 LEVEL 1: BASIC GENERATOR (12 weeks, ~6K transactions)
│   └── level_1_basic/
│       ├── generator.py (initialize & seed database)
│       ├── schema_base.sql (14 core tables)
│       └── README.md (Level 1 documentation)
│       └─ Use for: SQL fundamentals, learning, demos
│
├── 🔄 LEVEL 2: INCREMENTAL UPDATES (add weeks)
│   └── level_2_incremental/
│       ├── incremental_update.py (add weeks to L1 database)
│       └── README.md (Level 2 documentation)
│       └─ Use for: Data growth, ETL, time-series analysis
│
├── 📈 LEVEL 3: MASTER SIMULATION (10 years, ~250K transactions)
│   └── level_3_master_simulation/
│       ├── master_simulation.py (main orchestration)
│       ├── schema_film_releases.sql (film release tracking)
│       ├── film_system/
│       │   ├── film_generator.py (generate new films)
│       │   └── templates/
│       │       ├── action.txt
│       │       ├── comedy.txt
│       │       ├── drama.txt
│       │       └── ... (16 total film categories)
│       ├── inventory_system/
│       │   └── inventory_manager.py (inventory scheduling)
│       └── README.md (Level 3 documentation)
│       └─ Use for: Business cycles, film releases, inventory management
│
├── 🚀 LEVEL 4: ADVANCED MASTER (10 years, ~300K transactions)
│   └── level_4_advanced_master/
│       ├── run_advanced_simulation.py (main with seasonality)
│       ├── schema_advanced_features.sql (late fees, AR, tracking)
│       ├── tracking_system/
│       │   ├── advanced_incremental_update.py (late fees & AR)
│       │   └── advanced_incremental_update_demo.py (demo)
│       └── README.md (Level 4 documentation)
│       └─ Use for: Seasonality, AR/collections, advanced analytics
│
├── 🔧 SHARED UTILITIES
│   └── shared/
│       ├── configs/
│       │   ├── config.json (default - L1, L2)
│       │   ├── config_10year.json (L3 config)
│       │   ├── config_10year_advanced.json (L4 config)
│       │   └── README.md (configuration guide)
│       ├── analysis/
│       │   ├── analysis_queries.sql (10 pre-built queries)
│       │   └── late_fees_view.sql (L4 views)
│       ├── validate.py (verify database setup)
│       ├── maintain.py (backup, optimize, stats)
│       └─ Use for: Common tools, configs, analysis
│
├── 🧪 TESTS & UTILITIES
│   └── tests/ (empty - ready for user tests)
│
├── 📋 PROJECT FILES
│   ├── requirements.txt (Python dependencies)
│   ├── setup.sh (automated setup script)
│   ├── LICENSE (project license)
│   ├── .gitignore (git ignores)
│   └── README.md (project overview)
│
└── 🗂️ CONVENIENCE SCRIPTS (at root, point to levels)
    ├── generator.py → level_1_basic/generator.py
    ├── incremental_update.py → level_2_incremental/incremental_update.py
    ├── master_simulation.py → level_3_master_simulation/master_simulation.py
    └── run_advanced_simulation.py → level_4_advanced_master/run_advanced_simulation.py
```

---

## Files by Purpose

### 📍 Entry Point (Start Here!)
- **`docs/START_HERE.md`** - Complete navigation guide
- **`README.md`** - Quick reference

### 📚 Documentation
- **`level_X_*/README.md`** - Level-specific documentation
- **`shared/configs/README.md`** - Configuration guide
- **`docs/guides/`** - Feature-specific guides (coming)
- **`docs/archive/`** - Legacy documentation (30+ old docs)

### 🗄️ Schemas
- **`level_1_basic/schema_base.sql`** - Core 14 tables
- **`level_3_master_simulation/schema_film_releases.sql`** - Film releases + inventory tracking
- **`level_4_advanced_master/schema_advanced_features.sql`** - Late fees, AR, status, seasonality

### 🐍 Python Scripts by Level
| Level | Main Script | Purpose |
|-------|-------------|---------|
| L1 | `level_1_basic/generator.py` | Initialize DB with 12 weeks |
| L2 | `level_2_incremental/incremental_update.py` | Add weeks to L1 DB |
| L3 | `level_3_master_simulation/master_simulation.py` | 10-year with film releases |
| L4 | `level_4_advanced_master/run_advanced_simulation.py` | 10-year with seasonality |

### 🛠️ Supporting Scripts
| Script | Location | Purpose |
|--------|----------|---------|
| `validate.py` | `shared/` | Verify database setup |
| `maintain.py` | `shared/` | Backup, optimize, stats |
| `film_generator.py` | `level_3_master_simulation/film_system/` | Generate new films |
| `inventory_manager.py` | `level_3_master_simulation/inventory_system/` | Manage inventory |
| `advanced_incremental_update.py` | `level_4_advanced_master/tracking_system/` | Late fees & AR |

### ⚙️ Configuration Files
| File | Use For | Location |
|------|---------|----------|
| `config.json` | L1, L2 defaults | `shared/configs/` |
| `config_10year.json` | L3 master sim | `shared/configs/` |
| `config_10year_advanced.json` | L4 advanced sim | `shared/configs/` |

### 📊 Analysis & Queries
| File | Purpose | Location |
|------|---------|----------|
| `analysis_queries.sql` | 10 pre-built queries | `shared/analysis/` |
| `late_fees_view.sql` | L4 late fees view | `shared/analysis/` |

### 🎬 Film Templates (L3 only)
Located in `level_3_master_simulation/film_system/templates/`:
- `action.txt`, `animation.txt`, `comedy.txt`, `crime.txt`
- `documentary.txt`, `drama.txt`, `family.txt`, `fantasy.txt`
- `horror.txt`, `musical.txt`, `romance.txt`, `sci_fi.txt`
- `sports.txt`, `thriller.txt`, `war.txt`, `western.txt`

---

## Schema Progression

### Level 1: Core Schema (14 Tables)
```
Reference Tables:
  - country, city, address
  - language, category
  - actor, film, film_actor, film_category

Operations Tables:
  - staff, store

Customer Tables:
  - customer, inventory

Transaction Tables:
  - rental, payment
```

### Level 3: Add Film Release Tracking
```
New Tables:
  + film_releases (when films are released)
  + inventory_purchases (when inventory is purchased)
```

### Level 4: Add Advanced Features
```
New Tables:
  + inventory_status (real-time tracking)
  + late_fees (late fee calculations)
  + customer_ar (accounts receivable)
  + rental_status_tracking (rental lifecycle)
  + seasonality_log (seasonality adjustments)

New Views:
  + late_fees_view (for business analysis)
```

---

## Directory Statistics

| Directory | Files | Purpose |
|-----------|-------|---------|
| `level_1_basic/` | 3 | Core database generator |
| `level_2_incremental/` | 2 | Incremental week additions |
| `level_3_master_simulation/` | 23 | Multi-year with scheduling |
| `level_4_advanced_master/` | 4 | Advanced with seasonality |
| `shared/` | 8 | Shared utilities & configs |
| `docs/` | 35+ | Documentation |
| `tests/` | 0 | Ready for user tests |
| **Total** | **~70+** | Complete system |

---

## What's In Each Level

### Level 1 (Basic)
```
✅ 14 core tables
✅ 12 weeks of data (~6,000 rentals)
✅ Basic business patterns
✅ No add-ons or extensions
→ Perfect for: SQL learning
```

### Level 2 (Incremental)
```
✅ Everything from Level 1
✅ Add weeks to existing database
✅ Maintain customer lifecycle
✅ Realistic growth patterns
→ Perfect for: ETL, data engineering
```

### Level 3 (Master Simulation)
```
✅ Everything from Levels 1-2
✅ Film release scheduling (quarterly)
✅ Inventory management system
✅ Business lifecycle phases
✅ 10-year dataset (~250,000 rentals)
→ Perfect for: Business modeling, cycles
```

### Level 4 (Advanced Master)
```
✅ Everything from Levels 1-3
✅ Seasonality (monthly variations)
✅ Customer segmentation (4 segments)
✅ Late fees tracking ($1.50/day)
✅ AR (Accounts Receivable) aging
✅ Inventory status tracking
✅ Rental lifecycle tracking
✅ 10-year dataset with "story"
→ Perfect for: Advanced analytics, BI
```

---

## Using This Structure

### For Learning
1. Start with `docs/START_HERE.md`
2. Choose your level based on learning goals
3. Read the level-specific README
4. Run the generator for that level
5. Work with the data

### For Teaching
1. Choose which level(s) to teach
2. Customize config in `shared/configs/`
3. Generate dataset for your class
4. Use level-specific README for lesson plans
5. Distribute to students

### For Production
1. Start with Level 1 or 3
2. Customize config for your needs
3. Run generator once
4. Use Level 2 or 4 for ongoing data
5. Monitor with `shared/validate.py`

---

## Configuration Management

All configs centralized in **`shared/configs/`**:
- `config.json` - Used by Levels 1 & 2
- `config_10year.json` - Used by Level 3
- `config_10year_advanced.json` - Used by Level 4

See `shared/configs/README.md` for:
- How to use each config
- How to customize
- How to create new variants

---

## Command Reference

### Basic Setup
```bash
# Initialize Level 1 database
python level_1_basic/generator.py

# Verify setup
python shared/validate.py

# View database stats
python shared/maintain.py stats
```

### Level 2: Incremental
```bash
# Add 1 week
python level_2_incremental/incremental_update.py

# Add 4 weeks
python level_2_incremental/incremental_update.py 4
```

### Level 3: Master Simulation
```bash
cd level_3_master_simulation
python master_simulation.py ../shared/configs/config_10year.json
```

### Level 4: Advanced Master
```bash
cd level_4_advanced_master
python run_advanced_simulation.py ../shared/configs/config_10year_advanced.json
```

### Analysis
```bash
# Run analysis queries
mysql -u root -p dvdrental_live < shared/analysis/analysis_queries.sql

# Backup database
python shared/maintain.py backup

# Optimize database
python shared/maintain.py optimize
```

---

## Key Improvements (After Reorganization)

✅ **Clear progression** - Each level builds logically on the previous
✅ **Organized by level** - No confusion about which files go together
✅ **Centralized configs** - All in `shared/configs/`
✅ **Centralized utilities** - All in `shared/`
✅ **Reduced clutter** - 30+ old docs moved to `docs/archive/`
✅ **Single entry point** - `docs/START_HERE.md`
✅ **Schema clarity** - Each level has explicit schema files
✅ **Featured grouping** - Film system, inventory system, tracking in subfolders

---

## Navigation Tips

1. **New to project?** → Start with `docs/START_HERE.md`
2. **Choose a level?** → Each `level_X_*/README.md`
3. **Configure?** → See `shared/configs/README.md`
4. **Troubleshoot?** → Check level-specific README or main README.md
5. **Find old docs?** → See `docs/archive/`

---

## File Count Summary

| Category | Count | Location |
|----------|-------|----------|
| Schema files | 3 | level_*_basic/*, master_simulation/, advanced_master/ |
| Python scripts | 8 | Distributed across levels |
| Configuration files | 3 | shared/configs/ |
| Documentation | 35+ | docs/ (+ 30+ archived) |
| Film templates | 16 | level_3_master_simulation/film_system/templates/ |
| SQL queries | 2 | shared/analysis/ |
| Supporting files | 5+ | requirements.txt, LICENSE, etc. |
| **Total Organized** | **~70+** | Across 8 main directories |

---

**Last Updated:** January 27, 2026  
**Status:** ✅ Complete Reorganization  
**Next Step:** Read [`docs/START_HERE.md`](docs/START_HERE.md)
