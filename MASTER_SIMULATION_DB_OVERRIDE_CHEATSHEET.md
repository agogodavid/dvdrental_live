# Master Simulation - Database Override Cheat Sheet

## TL;DR

Run simulation in **new database without touching config.json:**

```bash
python master_simulation.py dvdrental_new
```

**That's it!** All connection info (host, user, password) comes from config.json. Only database name changes.

---

## Connection Flow

```
Your Command:
    python master_simulation.py dvdrental_test
    
Master Simulation:
    1. Read config.json → host, user, password, database
    2. Override database name: dvdrental_test
    3. Connect to MySQL: host:user:password → CREATE dvdrental_test
    4. Run simulation
    
Result:
    Original database: untouched
    New database: dvdrental_test with fresh data
```

---

## What Gets Used From config.json

| Field | Source | Can Override? |
|-------|--------|---------------|
| host | config.json | ❌ No |
| user | config.json | ❌ No |
| password | config.json | ❌ No |
| database | config.json or CLI arg | ✅ Yes |

---

## Examples

### Example 1: Default (no override)
```bash
python master_simulation.py
```
Uses database from config.json (typically `dvdrental_live`)

### Example 2: New database
```bash
python master_simulation.py dvdrental_test
```
Uses: config.json host/user/password + database name `dvdrental_test`

### Example 3: Multiple simulations
```bash
# All use same credentials from config.json, different database names
python master_simulation.py dvdrental_sim1
python master_simulation.py dvdrental_sim2
python master_simulation.py dvdrental_sim3
```

### Example 4: Original database safe
```bash
# Original in config.json is safe
cat config.json
# Shows: "database": "dvdrental_live"

python master_simulation.py dvdrental_live_backup

# Check both exist
mysql -u root -p -e "SHOW DATABASES LIKE 'dvdrental%';"
# Shows: dvdrental_live AND dvdrental_live_backup
```

---

## Config.json Not Modified

Before:
```json
{
  "mysql": {
    "host": "localhost",
    "user": "root",
    "password": "password123",
    "database": "dvdrental_live"
  }
}
```

After running `python master_simulation.py dvdrental_test`:
```json
{
  "mysql": {
    "host": "localhost",        ← SAME
    "user": "root",             ← SAME
    "password": "password123",  ← SAME
    "database": "dvdrental_live" ← SAME (file not changed)
  }
}
```

Only the runtime uses `dvdrental_test`. File never touched.

---

## Summary

✅ Connection credentials: From config.json (always)  
✅ Database name: From CLI arg if provided, else config.json  
✅ Config.json: Never modified  
✅ Original database: Always safe  

Just pass database name and you're done! 🚀
