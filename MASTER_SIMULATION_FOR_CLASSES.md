# Master Simulation for Classes & Groups

## Overview

Use the database override feature to create separate DVD rental databases for each class, group, or cohort. Each group gets their own isolated database with consistent connection credentials.

## Class/Group Setup

### Scenario: Multiple Student Groups

**Instructor:** You have 3 student groups working on database analysis projects.

**Setup:**
```bash
# Group A (Section 1)
python master_simulation.py dvdrental_group_a

# Group B (Section 2)
python master_simulation.py dvdrental_group_b

# Group C (Section 3)
python master_simulation.py dvdrental_group_c
```

**Result:**
- 3 separate databases with identical schema
- Each group works on their own data
- All use same connection credentials from config.json
- Original production database untouched

## Naming Conventions

### By Section/Group
```bash
python master_simulation.py dvdrental_section_1
python master_simulation.py dvdrental_section_2
python master_simulation.py dvdrental_group_a
python master_simulation.py dvdrental_cohort_2024
```

### By Team/Project
```bash
python master_simulation.py dvdrental_team_analytics
python master_simulation.py dvdrental_team_reporting
python master_simulation.py dvdrental_team_forecasting
```

### By Semester/Term
```bash
python master_simulation.py dvdrental_fall_2024_class_1
python master_simulation.py dvdrental_spring_2025_class_2
python master_simulation.py dvdrental_summer_2025_advanced
```

## Workflow for Instructors

### 1. Setup: Create Databases for Each Group

```bash
#!/bin/bash
# create_class_databases.sh

cd /workspaces/dvdrental_live

echo "Creating databases for SQL course groups..."

# Create for each group
python master_simulation.py dvdrental_group_a &
python master_simulation.py dvdrental_group_b &
python master_simulation.py dvdrental_group_c &

# Wait for all to complete
wait

echo "All group databases created successfully!"
```

Run:
```bash
chmod +x create_class_databases.sh
./create_class_databases.sh
```

Runs in parallel - takes ~30 minutes to create all 3 databases.

### 2. Provide Access Info to Students

**To Group A:**
```
Database: dvdrental_group_a
Host: localhost
User: root
Password: (from instructor)
```

**To Group B:**
```
Database: dvdrental_group_b
Host: localhost
User: root
Password: (from instructor)
```

**To Group C:**
```
Database: dvdrental_group_c
Host: localhost
User: root
Password: (from instructor)
```

All use same credentials, just different database names!

### 3. Students Work on Their Database

Each group connects to their database:

```bash
# Group A member
mysql -u root -p dvdrental_group_a

# Group B member
mysql -u root -p dvdrental_group_b

# Group C member
mysql -u root -p dvdrental_group_c
```

All see identical schema and similar (but different) data patterns.

## Teaching Scenarios

### Scenario 1: Hands-on SQL Workshop

**Setup (30 min):**
```bash
# Create one database per student (for large classes, use batch)
for i in {1..25}; do
  python master_simulation.py dvdrental_student_$i &
  if (( i % 5 == 0 )); then
    wait  # Batch every 5 to avoid overload
  fi
done
wait
```

Result: 25 separate databases for 25 students

**Assignment:**
> "Write SQL queries to find top 10 rental films in your database."

Each student works on their own data:
```bash
mysql -u root -p dvdrental_student_1 -e "SELECT ... FROM rental..."
mysql -u root -p dvdrental_student_2 -e "SELECT ... FROM rental..."
```

### Scenario 2: Comparative Analysis Project

**Setup:**
```bash
# Create databases with different configurations
# First: Conservative seasonality (edit SEASONAL_MULTIPLIERS)
python master_simulation.py dvdrental_conservative

# Second: Aggressive seasonality (edit SEASONAL_MULTIPLIERS)
python master_simulation.py dvdrental_aggressive

# Third: 10-year extended (edit TOTAL_WEEKS)
python master_simulation.py dvdrental_extended
```

**Assignment:**
> "Compare rental patterns across three datasets with different business models."

- Group 1 analyzes `dvdrental_conservative` (stable demand)
- Group 2 analyzes `dvdrental_aggressive` (volatile demand)
- Group 3 analyzes `dvdrental_extended` (10-year trends)

### Scenario 3: Database Performance Testing

**Setup:**
```bash
# Multiple replicas for load testing
for i in {1..5}; do
  python master_simulation.py dvdrental_replica_$i &
done
wait
```

**Assignment:**
> "Test query performance across multiple identical databases."

Each group runs tests on their replica:
```bash
# Team 1
mysql -u root -p dvdrental_replica_1 < benchmark_queries.sql

# Team 2
mysql -u root -p dvdrental_replica_2 < benchmark_queries.sql
```

## Script Examples for Instructors

### Batch Create for Large Classes

```bash
#!/bin/bash
# create_batch_databases.sh - Create databases for multiple groups

COURSE="data_analysis"
GROUP_COUNT=10
SCRIPT_DIR="/workspaces/dvdrental_live"

cd "$SCRIPT_DIR"

echo "Creating $GROUP_COUNT databases for $COURSE course..."

for i in $(seq 1 $GROUP_COUNT); do
    DB_NAME="${COURSE}_group_$(printf "%02d" $i)"
    echo "Creating $DB_NAME..."
    python master_simulation.py "$DB_NAME" > /tmp/${DB_NAME}_creation.log 2>&1 &
done

wait
echo "All databases created successfully!"

# Verify
echo -e "\nVerifying created databases:"
mysql -u root -p -e "SHOW DATABASES LIKE '${COURSE}%';"
```

### Verify All Databases Created

```bash
#!/bin/bash
# verify_databases.sh

PATTERN="dvdrental_group"

echo "Checking databases matching pattern: $PATTERN"
mysql -u root -p -e "SHOW DATABASES LIKE '${PATTERN}%';" | tail -n +2 | while read db; do
    COUNT=$(mysql -u root -p "$db" -e "SELECT COUNT(*) FROM rental;" 2>/dev/null | tail -n1)
    echo "  $db: $COUNT rentals"
done
```

### Cleanup After Class

```bash
#!/bin/bash
# cleanup_databases.sh - Remove class databases

PATTERN="dvdrental_group"
read -p "Drop all databases matching '$PATTERN'? (yes/no) " -n 3 -r
echo

if [[ $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    mysql -u root -p -e "SHOW DATABASES LIKE '${PATTERN}%';" | tail -n +2 | while read db; do
        echo "Dropping $db..."
        mysql -u root -p -e "DROP DATABASE $db;"
    done
    echo "Cleanup complete!"
fi
```

## Connection Info Template for Students

**To share with your students:**

```
═══════════════════════════════════════════════════════════════
  SQL Workshop - Database Connection Information
═══════════════════════════════════════════════════════════════

Group/Team: GROUP_A
Database:   dvdrental_group_a
Host:       localhost
User:       root
Password:   [provided by instructor]

═══════════════════════════════════════════════════════════════

How to Connect:

Command Line:
  mysql -u root -p dvdrental_group_a

MySQL Workbench:
  1. Click "+" to create new connection
  2. Connection Name: Group A
  3. Hostname: localhost
  4. Username: root
  5. Password: [provided by instructor]
  6. Default Schema: dvdrental_group_a
  7. Click "Test Connection"
  8. Click "OK"

═══════════════════════════════════════════════════════════════

Sample Queries to Get Started:

-- Show number of rentals
SELECT COUNT(*) as total_rentals FROM rental;

-- Top 10 rented films
SELECT f.title, COUNT(r.rental_id) as rentals
FROM rental r
JOIN inventory i ON r.inventory_id = i.inventory_id
JOIN film f ON i.film_id = f.film_id
GROUP BY f.film_id
ORDER BY rentals DESC
LIMIT 10;

-- Revenue by month
SELECT DATE_FORMAT(payment_date, '%Y-%m') as month, SUM(amount) as revenue
FROM payment
GROUP BY month
ORDER BY month;

═══════════════════════════════════════════════════════════════
```

## Benefits for Teaching

✅ **Isolation:** Each group/student has their own database  
✅ **Consistency:** Same connection credentials for all  
✅ **Scale:** Easy to create many databases at once  
✅ **Flexibility:** Different configurations per group  
✅ **Safety:** Production database stays separate  
✅ **Cleanup:** Easy to remove after class  

## Naming Best Practices

| Use Case | Pattern | Example |
|----------|---------|---------|
| By Group | `dvdrental_group_X` | `dvdrental_group_a` |
| By Section | `dvdrental_section_X` | `dvdrental_section_1` |
| By Team | `dvdrental_team_X` | `dvdrental_team_analytics` |
| By Semester | `dvdrental_TERM_YEAR_CLASS` | `dvdrental_fall_2024_sql_101` |
| By Student | `dvdrental_student_X` | `dvdrental_student_01` |
| By Cohort | `dvdrental_cohort_YEAR` | `dvdrental_cohort_2024` |

## Example: Full Class Setup

**Scenario:** Teaching "SQL Fundamentals" with 20 students in 4 groups

### Step 1: Create Databases (run once)

```bash
#!/bin/bash
# setup_sql_class.sh

cd /workspaces/dvdrental_live

echo "SQL Fundamentals - Setting up 4 group databases..."

python master_simulation.py dvdrental_sql_group_1 &
python master_simulation.py dvdrental_sql_group_2 &
python master_simulation.py dvdrental_sql_group_3 &
python master_simulation.py dvdrental_sql_group_4 &

wait
echo "Setup complete! 4 databases ready for SQL class."
```

### Step 2: Distribute to Students

| Group | Database | Members |
|-------|----------|---------|
| Group 1 | dvdrental_sql_group_1 | Alice, Bob, Charlie, David, Eve |
| Group 2 | dvdrental_sql_group_2 | Frank, Grace, Henry, Ivy, Jack |
| Group 3 | dvdrental_sql_group_3 | Karen, Leo, Mia, Nathan, Olivia |
| Group 4 | dvdrental_sql_group_4 | Patricia, Quinn, Rachel, Samuel, Tina |

### Step 3: Students Work on Assignments

Each group submits SQL queries that work on their database:

```sql
-- Group 1 submits
SELECT * FROM dvdrental_sql_group_1.rental WHERE YEAR(rental_date) = 2002;

-- Group 2 submits
SELECT * FROM dvdrental_sql_group_2.rental WHERE YEAR(rental_date) = 2002;

-- Results differ slightly (different data generation patterns)
-- but schema is identical
```

### Step 4: Cleanup (after semester)

```bash
#!/bin/bash
# cleanup_sql_class.sh

echo "Removing SQL Fundamentals class databases..."

for i in {1..4}; do
    mysql -u root -p -e "DROP DATABASE dvdrental_sql_group_$i;"
done

echo "Cleanup complete!"
```

## Advanced: Scripted Batch Processing

```bash
#!/bin/bash
# batch_create_with_config.sh
# Create databases with different configurations

COURSE="database_design"
NUM_GROUPS=3

cd /workspaces/dvdrental_live

# Configuration variations
create_config_1() {
    # Conservative seasonality
    sed -i 's/TOTAL_WEEKS = 156/TOTAL_WEEKS = 156/' master_simulation.py
    echo "Config 1: Standard 3-year data"
}

create_config_2() {
    # More aggressive growth
    echo "Config 2: Aggressive growth variant"
}

create_config_3() {
    # Extended 10-year data
    echo "Config 3: Extended 10-year data"
}

# Create databases
for i in $(seq 1 $NUM_GROUPS); do
    DB_NAME="${COURSE}_variant_$i"
    echo "Creating $DB_NAME with config $i..."
    create_config_$i
    python master_simulation.py "$DB_NAME" > /tmp/${DB_NAME}.log 2>&1 &
done

wait
echo "All variants created!"
```

## Tips for Instructors

1. **Naming:** Use consistent, descriptive names (makes cleanup easier)
2. **Documentation:** Keep a spreadsheet of database-to-group mappings
3. **Credentials:** Create separate MySQL user per class if possible (`class2024_user`)
4. **Backup:** Before cleanup, consider backing up a representative database
5. **Monitoring:** Check `/tmp` logs to verify all creations succeeded
6. **Batch Processing:** Create multiple in parallel but monitor disk space
7. **Cleanup:** Schedule regular cleanup to free disk space

## Connection String for Your Students

If they use connection strings (Python, Node.js, etc.):

```
mysql+pymysql://root:PASSWORD@localhost/dvdrental_group_a
mysql://root:PASSWORD@localhost/dvdrental_group_b
```

(Replace `PASSWORD` with actual password, `GROUP_X` with their database)

---

This approach gives each class/group their own isolated, realistic database while keeping all connection credentials centralized in config.json. Perfect for teaching scenarios! 📚
