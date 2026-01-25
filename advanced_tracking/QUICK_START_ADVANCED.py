#!/usr/bin/env python3
"""
Quick Start - Advanced Incremental Update
==========================================

Copy and paste these exact commands to get started:
"""

# 1. FIRST TIME SETUP
commands = {
    "install_dependencies": "pip install mysql-connector-python",
    
    "initialize_tables": "python advanced_incremental_update.py --init",
    
    "run_first_update": "python advanced_incremental_update.py --update",
    
    "run_demo": "python advanced_incremental_update_demo.py",
}

# 2. DAILY OPERATIONS
daily = {
    "update_tracking": "python advanced_incremental_update.py --update",
    
    "daily_reconciliation": "python advanced_incremental_update.py --daily",
    
    "quick_ar_status": """
mysql -uroot -proot dvdrental_live << EOF
SELECT 
  c.first_name, c.last_name, ca.balance, ca.status
FROM customer_account ca
JOIN customer c ON ca.customer_id = c.customer_id
WHERE ca.balance > 0
ORDER BY ca.balance DESC
LIMIT 10;
EOF
    """.strip(),
    
    "quick_late_fees": """
mysql -uroot -proot dvdrental_live << EOF
SELECT COUNT(*) as overdue_count, SUM(fee_amount) as total_fees
FROM late_fees WHERE fee_status = 'pending';
EOF
    """.strip(),
}

# 3. KEY FILES
files = {
    "main_script": "advanced_incremental_update.py",
    "demo": "advanced_incremental_update_demo.py",
    "documentation": "ADVANCED_TRACKING_GUIDE.md",
    "config": "config.json",
    "data_quality": "DATA_QUALITY_NOTES.md",
}

# 4. WHAT IT DOES
features = """
✅ LATE FEE CALCULATION
   • Automatically calculates $1.50/day for overdue rentals
   • Updates daily as rentals age
   • Tracks payment status (pending, partially_paid, paid, written_off)

✅ INVENTORY STATUS TRACKING
   • Real-time availability (available, rented, damaged, missing)
   • Audit trail of all status changes
   • Shrinkage detection for damaged/missing items

✅ CUSTOMER AR MANAGEMENT
   • Account balance tracking
   • Customer status (good_standing, past_due, at_risk, suspended)
   • Outstanding balance by customer

✅ AUTOMATED REPORTING
   • Late fee report (top overdue rentals)
   • Customer AR aging report
   • Inventory status summary
   • Revenue tracking

✅ QUERY VIEWS
   • v_rental_status: Query all rentals with status and due date
   • late_fees: All late fee records with status
   • customer_account: AR by customer
   • inventory_audit: Complete status change history
"""

# 5. EXAMPLE QUERIES
example_queries = {
    "find_overdue_rentals": """
SELECT c.first_name, c.last_name, f.title, vrs.days_overdue
FROM v_rental_status vrs
JOIN customer c ON vrs.customer_id = c.customer_id
JOIN film f ON vrs.film_id = f.film_id
WHERE vrs.status = 'overdue'
ORDER BY vrs.days_overdue DESC;
    """.strip(),
    
    "ar_by_customer": """
SELECT c.first_name, c.last_name, ca.balance, ca.status
FROM customer_account ca
JOIN customer c ON ca.customer_id = c.customer_id
WHERE ca.balance > 0
ORDER BY ca.balance DESC;
    """.strip(),
    
    "late_fee_revenue": """
SELECT 
  SUM(fee_amount) as total_late_fees,
  SUM(fee_paid) as collected,
  SUM(fee_amount) - SUM(fee_paid) as outstanding
FROM late_fees
WHERE fee_status IN ('pending', 'partially_paid');
    """.strip(),
    
    "inventory_status": """
SELECT status, COUNT(*) as count
FROM inventory
GROUP BY status;
    """.strip(),
    
    "problem_customers": """
SELECT c.first_name, c.last_name, ca.overdue_rentals, ca.balance
FROM customer_account ca
JOIN customer c ON ca.customer_id = c.customer_id
WHERE ca.overdue_rentals > 2 OR ca.status = 'suspended'
ORDER BY ca.balance DESC;
    """.strip(),
}

# 6. SCHEDULING
scheduling = """
DAILY RECONCILIATION (add to crontab):

  # Update tracking daily at 2 AM
  0 2 * * * cd /path/to/dvdrental_live && python advanced_incremental_update.py --daily

  # Generate AR report weekly
  0 3 * * 1 cd /path/to/dvdrental_live && python advanced_incremental_update.py --update


TEST CRON JOB FIRST:
  # Run manually to verify
  python advanced_incremental_update.py --daily
  
  # Check logs
  tail -f /path/to/logs/tracking.log
"""

# 7. INDEPENDENCE GUARANTEE
independence = """
✅ COMPLETELY INDEPENDENT

  • Doesn't modify schema.sql or existing data
  • Doesn't interfere with generator.py or incremental_update.py
  • Only writes to its own tracking tables
  • Can run before, after, or alongside main generators
  • Safe to run multiple times (idempotent)

WORKFLOW:
  
  1. Your main system creates rentals, payments, inventory
  2. Advanced tracker reads those changes
  3. Advanced tracker calculates fees, statuses, AR
  4. Your analysts query tracking tables for insights
  
  NO CONFLICTS, NO INTERFERENCE
"""

# 8. TROUBLESHOOTING
troubleshooting = """
PROBLEM: Script won't start
FIX: pip install mysql-connector-python

PROBLEM: Can't connect to MySQL
FIX: Verify MySQL is running and config.json is correct

PROBLEM: No late fees showing
FIX: Run --init first to calculate initial fees

PROBLEM: Inventory status not updating
FIX: Ensure rentals are fully inserted, then run --update

PROBLEM: Duplicate entry errors
FIX: Normal - script uses ON DUPLICATE KEY UPDATE to recalculate

FOR MORE HELP:
  • See ADVANCED_TRACKING_GUIDE.md for detailed docs
  • See DATA_QUALITY_NOTES.md for data quality details
  • Run advanced_incremental_update_demo.py to see examples
"""

def print_section(title, content):
    """Print formatted section."""
    print(f"\n{'='*70}")
    print(f"{title.center(70)}")
    print('='*70)
    if isinstance(content, dict):
        for key, value in content.items():
            print(f"\n{key.replace('_', ' ').title()}:")
            print(f"  $ {value}")
    else:
        print(content)

if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════════════╗
║     ADVANCED INCREMENTAL UPDATE - QUICK START REFERENCE             ║
╚════════════════════════════════════════════════════════════════════╝
    """)
    
    print_section("1. FIRST TIME SETUP", commands)
    print_section("2. DAILY OPERATIONS", daily)
    print_section("3. KEY FILES", files)
    print_section("4. WHAT IT DOES", features)
    print_section("5. EXAMPLE QUERIES", example_queries)
    print_section("6. SCHEDULING", scheduling)
    print_section("7. INDEPENDENCE GUARANTEE", independence)
    print_section("8. TROUBLESHOOTING", troubleshooting)
    
    print("\n" + "="*70)
    print("READY TO START?".center(70))
    print("="*70)
    print("""
1. Install:        pip install mysql-connector-python
2. Initialize:     python advanced_incremental_update.py --init
3. Run Update:     python advanced_incremental_update.py --update
4. View Reports:   See output in terminal
5. Query Data:     Use example queries above

For complete documentation: see ADVANCED_TRACKING_GUIDE.md

Happy tracking! 🚀
    """)
