# Virtual Environment Setup Guide

## Quick Start

### First Time Setup
```bash
cd /home/agogodavid/dev_dvdrental/dvdrental_live
bash setup.sh
```

This will:
1. ✓ Create a Python virtual environment (if needed)
2. ✓ Activate it
3. ✓ Install dependencies from requirements.txt
4. ✓ Run the initial database setup

### Activate Environment (After Setup)

**On Linux/macOS:**
```bash
cd /home/agogodavid/dev_dvdrental/dvdrental_live
source venv/bin/activate
```

You should see `(venv)` appear in your terminal prompt.

**On Windows (PowerShell):**
```powershell
cd C:\path\to\dvdrental_live
venv\Scripts\Activate.ps1
```

**On Windows (Command Prompt):**
```cmd
cd C:\path\to\dvdrental_live
venv\Scripts\activate.bat
```

### Deactivate Environment
```bash
deactivate
```

### Run Scripts with Environment

**Option 1: With activation**
```bash
source venv/bin/activate
python level_1_basic/generator.py --database test_db
```

**Option 2: Without activation**
```bash
venv/bin/python level_1_basic/generator.py --database test_db
```

## Troubleshooting

### Virtual environment not found
```bash
# Recreate it
python3 -m venv venv
source venv/bin/activate
```

### Permission denied when running setup.sh
```bash
chmod +x setup.sh
bash setup.sh
```

### Python packages not found
```bash
# Make sure you're in the activated environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### venv not recognized after closing terminal
This is normal - you need to reactivate it:
```bash
source venv/bin/activate
```

## Project Structure

```
dvdrental_live/
├── venv/                          ← Virtual environment (created by setup.sh)
├── level_1_basic/
│   └── generator.py              ← Run after activating venv
├── level_3_master_simulation/
│   └── master_simulation.py       ← Run after activating venv
├── level_4_advanced_master/
│   └── run_advanced_simulation.py ← Run after activating venv
├── shared/
├── setup.sh                       ← Initial setup script
└── requirements.txt               ← Python dependencies
```

## Next Steps

1. Activate the environment: `source venv/bin/activate`
2. Test it works: `python --version`
3. Run Level 1: `python level_1_basic/generator.py`
4. Or run Level 3: `python level_3_master_simulation/master_simulation.py`

See main [README.md](README.md) for more commands.
