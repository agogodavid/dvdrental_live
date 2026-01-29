# Virtual Environment Quick Reference

## One-Line Activation

```bash
source ~/dev_dvdrental/dvdrental_live/venv/bin/activate
```

Or use the helper script:
```bash
bash ~/dev_dvdrental/dvdrental_live/activate.sh
```

## After Activation, You Can Run

```bash
# Level 1: Basic 12-week generator
cd ~/dev_dvdrental/dvdrental_live
python level_1_basic/generator.py --season 50 --database test_db

# Level 3: Master simulation (10 years)
python level_3_master_simulation/master_simulation.py --database master_test

# Level 4: Advanced simulation
python level_4_advanced_master/run_advanced_simulation.py --season 40
```

## Without Activation (Using Full Path)

```bash
~/dev_dvdrental/dvdrental_live/venv/bin/python level_1_basic/generator.py
```

## Complete Setup from Scratch

```bash
cd ~/dev_dvdrental/dvdrental_live
bash setup.sh        # Creates venv, activates it, installs deps, runs setup
```

## Verify It's Working

```bash
source ~/dev_dvdrental/dvdrental_live/venv/bin/activate
python --version    # Should show Python 3.x.x
pip list            # Should show mysql-connector-python and python-dateutil
```

## Deactivate When Done

```bash
deactivate
```

## Environment Location

```
/home/agogodavid/dev_dvdrental/dvdrental_live/venv/
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `command not found: activate` | Use full path: `source venv/bin/activate` |
| `No module named mysql.connector` | Run: `pip install mysql-connector-python` |
| `permission denied: setup.sh` | Run: `chmod +x setup.sh && bash setup.sh` |
| venv not found | Create it: `python3 -m venv venv` |

## Important Files

- `setup.sh` - Initial setup (creates venv, installs deps)
- `activate.sh` - Helper script to activate environment
- `venv/` - Virtual environment directory
- `requirements.txt` - Python dependencies
- `level_1_basic/generator.py` - Run after activating
- `level_3_master_simulation/master_simulation.py` - Run after activating
- `level_4_advanced_master/run_advanced_simulation.py` - Run after activating
