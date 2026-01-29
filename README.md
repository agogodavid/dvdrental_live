# 🎓 DVD Rental Live - Progressive Database Simulation System

A **4-level progressive learning system** for database design, data engineering, business intelligence, and advanced analytics. From simple SQL fundamentals to sophisticated 10-year business lifecycle simulations.

> ⚠️ **NEW HERE?** If you're new to this project, **scroll to the very bottom** and read the "**Before You Start**" section first. Come back here after setup! 👇

---

## 🚀 Quick Start

### Level 4: Advanced 10-Year Simulation (Recommended) - takes around 40 minutes on localhost ⭐
```bash
cd level_4_advanced_master
python adv_master_simulation.py --database dvdrental_live
```

### Level 1-3: Quick Commands
```bash
# Level 1: Basic database (12 weeks), uses default settings in shared/config.json
cd level_1_basic && python generator.py

# Level 2: Add incremental weeks
cd level_2_incremental && python incremental_update.py 10

# Level 3: Master simulation (film releases)
cd level_3_master_simulation && python master_simulation.py
```

---

## 📚 Common Arguments

```bash
--database my_custom_db    # Custom database name. If you want to create a database with a specific name without changing config.json, always use this.
--season 50                # 50% seasonal boost during incremental_updates only
--season 0                 # No seasonality during incremental_updates only
--season -30               # 30% seasonal drop during incremental_updates only
--config config_file.json  # Use alternate config for level_4 run only
```

---

## 📖 Documentation

- **🌟 START HERE**: [`docs/START_HERE.md`](docs/START_HERE.md)
- **Level 1**: [`level_1_basic/README.md`](level_1_basic/README.md)
- **Level 2**: [`level_2_incremental/README.md`](level_2_incremental/README.md)
- **Level 3**: [`level_3_master_simulation/README.md`](level_3_master_simulation/README.md)
- **Level 4**: [`level_4_advanced_master/README.md`](level_4_advanced_master/README.md)
- **Shared**: [`shared/README.md`](shared/README.md)

## Repository Structure

```
dvdrental_live/
├── docs/                          # Main documentation
│   └── START_HERE.md ⭐
├── level_1_basic/                 # Basic 12-week database
├── level_2_incremental/           # Add weeks incrementally
├── level_3_master_simulation/     # 10-year simulation with film releases
├── level_4_advanced_master/       # Advanced 10-year with business lifecycle
├── shared/                        # Shared utilities & configs
├── archive/                       # Legacy files
├── work_files/                    # Development & reference files
├── setup.sh                       # Environment setup script
├── activate.sh                    # Virtual environment activation
├── requirements.txt               # Dependencies
├── LICENSE
└── README.md                      # This file
```

## 🔧 Common Commands

```bash
# Verify setup
python shared/validate.py

# Database maintenance
python shared/maintain.py stats
python shared/maintain.py optimize

# Analyze data
python shared/analysis.py
```

## 🎯 Key Features

### Power Law Distribution (Realistic Rental Patterns)

The simulation uses **Zipfian (Power Law) distribution** to model realistic movie rental behavior. Instead of all movies being equally popular, it follows the **80/20 rule**:

**What is Power Law?**
Power law is a mathematical relationship where a small percentage of items account for the majority of activity. In DVD rentals:
- **Top 4% of films** generate **50% of rentals** (blockbusters)
- **Bottom 90% of films** generate **30% of rentals** (niche films)
- This mirrors real-world behavior where blockbusters dominate while specialty films remain available

**The New Release Problem & Solution:**
Pure power law has a flaw: **new films with zero rental history would never get rented**! To fix this, the system includes a **New Movie Boost**:

- **First 90 days after release**: New films get **2.0x weight multiplier** (linearly decaying to 1.0x)
- **Selective boost**: Only **40% of new releases** get the boost (models marketing/promotion)
- **Realistic pattern**: Promoted blockbusters get initial attention, then settle into normal power law distribution
- **Configurable**: Adjust boost duration, strength, and percentage

**Example Timeline:**
```
Day 0:    New film gets 2.0x weight → 1.8% rental probability
Day 45:   New film gets 1.5x weight → 1.4% rental probability  
Day 90+:  Boost expires → 0.3% rental probability (power law takes over)
Year 2:   Established hit → 15% rental probability (earned through history)
```

**Why it matters:**
- 📊 **Realistic**: Models actual rental patterns (not theoretical uniform distribution)
- 🎬 **New release dynamics**: Solves cold-start problem for new movies
- 💰 **Business insights**: Shows why some films generate ROI while others don't
- 🎓 **Analytics learning**: Great for practicing skewed data analysis
- 🔧 **Configurable**: Adjust alpha parameter (0.5-1.5+) to control distribution intensity

**Configuration:**
```json
// In shared/configs/config.json
"rental_distribution": {
  "enabled": true,
  "type": "power_law",
  "alpha": 1.0,
  "description": "Zipfian distribution for realistic rental patterns"
},
"new_movie_boost": {
  "enabled": true,
  "days_to_boost": 90,
  "boost_factor": 2.0,
  "boost_percentage": 40,
  "description": "2x multiplier for first 90 days, only 40% of new films"
}
```

**Tuning Alpha:**
- `alpha: 0.5` → Gentle distribution (more balanced)
- `alpha: 1.0` → Recommended (classic 80/20)
- `alpha: 1.5+` → Extreme (blockbuster-heavy)

---

### Intelligent Film Generation

**Level 1 (Basic Generator)**
- Procedural titles: Random combinations (e.g., "The Silent Knight Returns")
- 500 initial films seeded with realistic release years
- Simple but non-specific to genre

**Level 3+ (Advanced Film System)**
- **Template-based generation**: Category-specific templates (Action, Comedy, Drama, Horror, etc.)
- **Smart naming**: Uses location, character, and action keywords per genre
- **Genre-matched**: Titles fit their category (no action comedies mislabeled)
- **Realistic metadata**: Release year, length, cost, rating distributed by category

**8 New Films Per Week**: During simulation, new movies are released based on:
- Real market rhythm (weekly releases)
- Hot category boost (high-demand genres get more releases)
- Seasonal adjustments (more releases before holidays)

---

### Making Movies More Interesting for Classes

**Student Names Integration** - Personalize your simulation for teaching:

```python
# Add to shared/configs/config.json
"film_generation": {
  "use_student_names": true,
  "student_names": [
    "Alice", "Bob", "Charlie", "Diana", "Ethan",
    "Fiona", "George", "Hannah", "Ivan", "Julia"
  ],
  "use_names_in": ["character_names", "actor_names", "descriptions"]
}
```

**Example Customizations:**

1. **Class Names in Titles**:
   - "Alice's Secret Mission" (Action)
   - "The Bob Adventure" (Adventure)
   - "Charlie's Redemption" (Drama)

2. **Inside Jokes & References**:
   - Add course names: "Data Science: The Movie"
   - Add location references: "Lost in the Library"
   - Add inside jokes: "The SQL Injection Chronicles"

3. **Custom Categories**:
   - Create film templates for your specific topics
   - Example: "Data Analysis Thriller", "Blockchain Romance", "AI Horror"

4. **Implementation Steps**:
   ```bash
   # 1. Edit config.json with student names
   # 2. Or modify shared/film_system/film_generator.py directly
   # 3. Add new templates to FILM_TEMPLATES dictionary
   # 4. Regenerate database with custom movies
   ```

---

## 🎯 Learning Paths

| Path | Duration | Focus |
|------|----------|-------|
| **SQL Teaching** | 4 weeks | Level 1 schema exploration, queries, JOINs |
| **Data Engineering** | 6 weeks | Level 1 → Level 2 ETL pipeline |
| **Business Modeling** | 8 weeks | Level 1 → Level 3 film releases & inventory |
| **Advanced Analytics** | 10 weeks | Level 1 → Level 4 complete simulation |

## 📚 Additional Resources

For detailed guides, implementation notes, and troubleshooting, see the [`work_files/`](work_files/) folder:

- **Power Law Details**: [`work_files/POWER_LAW_COMPLETE.md`](work_files/POWER_LAW_COMPLETE.md)
- **Film Generation**: [`work_files/FILM_TITLE_GENERATION_GUIDE.md`](work_files/FILM_TITLE_GENERATION_GUIDE.md)
- **Full Architecture**: [`work_files/LEVEL_ARCHITECTURE.md`](work_files/LEVEL_ARCHITECTURE.md)

## 🚀 Next Steps

1. **New users**: Start with [`docs/START_HERE.md`](docs/START_HERE.md)
2. **Instructors**: See each level's `README.md` for teaching guides
3. **Advanced users**: Check [`level_4_advanced_master/README.md`](level_4_advanced_master/README.md)
4. **Customize for your class**: Edit [`shared/configs/config.json`](shared/configs/config.json)

---

## ⚙️ Before You Start

**This section is for first-time setup.** Follow these steps before running any commands above.

### Quick Setup (All Platforms)

#### **Windows Users (Recommended)**
Use Python directly (most reliable on Windows):

```powershell
# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Done! You're ready to use the system
```

**OR if you have Git Bash/WSL/MSYS2:**
```bash
chmod +x setup.sh
.\setup.sh        # With .\  prefix
```

#### **Mac/Linux Users**
Use the automated setup script:

```bash
# Make setup script executable (first time only)
chmod +x setup.sh activate.sh

# Run setup (creates venv + installs dependencies + generates database)
./setup.sh

# For future sessions, just activate the environment
source activate.sh
```

**What these scripts do:**
- `setup.sh` - Complete one-time setup (creates venv, installs Python packages, sets up database)
- `activate.sh` - Quick activation of existing environment (use this for future sessions)

---

### Manual Setup (If Scripts Don't Work)

#### 1️⃣ Install Python (Required)

The entire system runs on Python 3.8+. Check if you have it:

```bash
python --version
# Should show: Python 3.x.x
```

**If Python is not installed:**
- **Windows**: Download from [python.org](https://www.python.org/downloads/)
- **Mac**: `brew install python3`
- **Linux**: `sudo apt-get install python3`

#### 2️⃣ Set Up Python Virtual Environment (Recommended)

A virtual environment keeps dependencies isolated per project:

**Windows (PowerShell):**
```powershell
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux (Bash):**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` at the start of your terminal prompt.

#### 3️⃣ Install Python Dependencies

Install all required packages in one command:

```bash
pip install -r requirements.txt
```

**Key packages installed:**
- `mysql-connector-python` - Connect to MySQL databases
- `python-dotenv` - Load configuration from files
- Additional dependencies for data processing

#### 4️⃣ Install MySQL (Required)

The simulation generates data into a MySQL database. You need either:

**Option A: Local MySQL Installation** (Recommended for learning)
- **Windows**: Download [MySQL Community Server](https://dev.mysql.com/downloads/mysql/)
- **Mac**: `brew install mysql-server`
- **Linux**: `sudo apt-get install mysql-server`

Start the MySQL server:
```bash
# Windows: MySQL runs as a service (usually starts automatically)
# Mac: brew services start mysql
# Linux: sudo service mysql start
```

Test the connection:
```bash
mysql -u root -p
# Enter password (default is blank for new installations)
# Type: exit
```

**Option B: Managed MySQL (Cloud)** 
- AWS RDS, Google Cloud SQL, Azure Database for MySQL
- Update connection info in `shared/configs/config.json`

#### 5️⃣ Configure Database Connection

Edit [`shared/configs/config.json`](shared/configs/config.json):

```json
{
  "mysql": {
    "host": "localhost",      // Change to your server IP
    "user": "root",           // Your MySQL username
    "password": "",           // Your MySQL password
    "database": "dvdrental_live"
  }
}
```

**Test your connection:**
```bash
python shared/validate.py
# Should say: "✅ Database connection successful"
```

---

### Daily Workflow

**First time each day, activate the environment:**

**Windows (PowerShell):**
```powershell
venv\Scripts\activate
```

**Mac/Linux (Bash):**
```bash
source activate.sh
```

**Then run your simulations:**
```bash
cd level_1_basic && python generator.py
# or
cd level_4_advanced_master && python adv_master_simulation.py --database dvdrental_live
```

---

### First Run Test

After setup, test Level 1:

```bash
cd level_1_basic
python generator.py
```

**Expected output:**
- Database `dvdrental_live` created ✅
- 500 films seeded ✅
- 12 weeks of transactions generated ✅
- Takes ~2-5 minutes

**Next:** Go back to the "Quick Start" section at the top and try Level 2 or 4!

### ❓ Troubleshooting

**"Python was not found" (Windows PowerShell)**
- Python is not installed or not in your PATH
- **Solution 1** (Recommended): Download Python from [python.org](https://www.python.org/downloads/) and reinstall, making sure to check "Add Python to PATH" during installation
- **Solution 2**: Disable Microsoft Store Python shortcut:
  - Settings → Apps → Advanced app settings → App execution aliases
  - Toggle OFF: "python" and "python3.x"
- **Solution 3**: Use the full path to Python:
  ```powershell
  C:\Users\YourUsername\AppData\Local\Programs\Python\Python311\python.exe -m venv venv
  ```

**"setup.sh not recognized" (Windows PowerShell)**
- setup.sh is a bash script, requires Git Bash/WSL
- Use Python direct setup instead: `python -m venv venv && venv\Scripts\activate && pip install -r requirements.txt`
- Or use PowerShell with `.\setup.sh` if bash is installed

**"Python command not found"**
- Make sure Python is installed and in your PATH
- Try `python3` instead of `python`
- Check installation: `where python` (should show Python path)

**"mysql-connector-python not found"**
- Make sure virtual environment is activated (see `(venv)` in prompt)
- Run `pip install -r requirements.txt` again

**"Cannot connect to MySQL"**
- Verify MySQL is running: `mysql -u root -p`
- Check connection details in `shared/configs/config.json`
- Try: `python shared/validate.py`

**"Permission denied on setup.sh"** (Mac/Linux)
```bash
chmod +x setup.sh activate.sh
./setup.sh
```

### ✅ Ready to Go?

Once setup is complete, return to the "Quick Start" section above and pick a level to explore! 🚀