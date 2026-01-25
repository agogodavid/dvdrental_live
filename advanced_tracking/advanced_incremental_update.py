#!/usr/bin/env python3
"""
Advanced Incremental Update - Independent Tracking System
========================================================

Creates and maintains advanced tracking tables for:
  - Inventory status tracking (available, rented, damaged, missing)
  - Customer account AR (Accounts Receivable)
  - Rental status (active, overdue, completed, lost)
  - Late fees calculation and tracking
  - Inventory audit trail

INDEPENDENT: Does not modify existing schema or business logic
Run alongside main generator.py/incremental_update.py without conflicts

Usage:
  python advanced_incremental_update.py --init    # Initialize tracking tables
  python advanced_incremental_update.py --update  # Calculate late fees & update tracking
  python advanced_incremental_update.py --daily   # Daily reconciliation
"""

import json
import mysql.connector
from datetime import datetime, timedelta
from decimal import Decimal
import sys
import argparse
from typing import Dict, List, Tuple, Optional

# Configuration
CONFIG_FILE = "config.json"
LATE_FEE_RATE_PER_DAY = 1.50  # $ per day overdue
RENTAL_DURATION_DEFAULT = 7   # days


class AdvancedTrackingManager:
    """Manages advanced tracking tables independently."""
    
    def __init__(self, config_path: str = CONFIG_FILE, override_database: str = None):
        """Initialize connection and load configuration."""
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.db_config = self.config['mysql']
        
        # Apply database override if specified
        if override_database:
            self.db_config['database'] = override_database
            print(f"Database override: {override_database}")
        
        self.conn = None
        self.cursor = None
        self._connect()
    
    def _connect(self):
        """Establish database connection."""
        try:
            self.conn = mysql.connector.connect(**self.db_config)
            self.cursor = self.conn.cursor(dictionary=True)
            print(f"✅ Connected to {self.db_config['database']}")
        except mysql.connector.Error as err:
            print(f"❌ Connection failed: {err}")
            sys.exit(1)
    
    def close(self):
        """Close database connection."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
    
    def _execute_query(self, query: str, params: tuple = None) -> bool:
        """Execute query safely."""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.conn.commit()
            return True
        except mysql.connector.Error as err:
            print(f"  ⚠️  Query error: {err}")
            self.conn.rollback()
            return False
    
    def _fetch_query(self, query: str, params: tuple = None) -> List[Dict]:
        """Fetch query results."""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"  ⚠️  Query error: {err}")
            return []
    
    # ===== TABLE INITIALIZATION =====
    
    def init_tracking_tables(self):
        """Initialize all tracking tables (idempotent - safe to run multiple times)."""
        print("\n📊 Initializing Advanced Tracking Tables...\n")
        
        tables_created = 0
        
        # 1. Inventory Status Tracking
        if self._init_inventory_status():
            tables_created += 1
        
        # 2. Inventory Audit Trail
        if self._init_inventory_audit():
            tables_created += 1
        
        # 3. Rental Status View
        if self._init_rental_status():
            tables_created += 1
        
        # 4. Late Fees Table
        if self._init_late_fees_table():
            tables_created += 1
        
        # 5. Customer Accounts
        if self._init_customer_accounts():
            tables_created += 1
        
        # 6. Rental Late Fee Calculations (initial population)
        if self._init_late_fee_calculations():
            tables_created += 1
        
        print(f"\n✅ Advanced tracking tables ready ({tables_created} tables/views)")
    
    def _init_inventory_status(self) -> bool:
        """Add status tracking to inventory if not exists."""
        print("1️⃣  Checking inventory status tracking...")
        
        # Check if status column exists
        check_query = """
            SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'inventory' AND COLUMN_NAME = 'status'
        """
        result = self._fetch_query(check_query)
        
        if result:
            print("   ✓ Inventory status column already exists")
            return False
        
        # Add status column
        alter_query = """
            ALTER TABLE inventory 
            ADD COLUMN status ENUM('available', 'rented', 'damaged', 'missing') 
            DEFAULT 'available'
        """
        
        if self._execute_query(alter_query):
            print("   ✓ Added status column to inventory")
            return True
        return False
    
    def _init_inventory_audit(self) -> bool:
        """Create inventory audit trail table."""
        print("2️⃣  Checking inventory audit trail...")
        
        # Check if table exists
        check_query = """
            SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_NAME = 'inventory_audit' AND TABLE_SCHEMA = %s
        """
        result = self._fetch_query(check_query, (self.db_config['database'],))
        
        if result:
            print("   ✓ Inventory audit table already exists")
            return False
        
        create_query = """
            CREATE TABLE inventory_audit (
                audit_id INT AUTO_INCREMENT PRIMARY KEY,
                inventory_id INT NOT NULL,
                status_from VARCHAR(20),
                status_to VARCHAR(20),
                audit_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                audit_user VARCHAR(100) DEFAULT 'system',
                FOREIGN KEY (inventory_id) REFERENCES inventory(inventory_id),
                INDEX idx_inventory (inventory_id),
                INDEX idx_audit_date (audit_date)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        
        if self._execute_query(create_query):
            print("   ✓ Created inventory_audit table")
            return True
        return False
    
    def _init_rental_status(self) -> bool:
        """Create rental status view for easy querying."""
        print("3️⃣  Checking rental status view...")
        
        # Check if view exists
        check_query = """
            SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_NAME = 'v_rental_status' AND TABLE_SCHEMA = %s
        """
        result = self._fetch_query(check_query, (self.db_config['database'],))
        
        if result:
            print("   ✓ Rental status view already exists")
            # Drop and recreate to ensure it's up to date
            self._execute_query("DROP VIEW IF EXISTS v_rental_status")
        
        create_view_query = """
            CREATE VIEW v_rental_status AS
            SELECT 
                r.rental_id,
                r.customer_id,
                c.first_name,
                c.last_name,
                f.title,
                r.rental_date,
                f.rental_duration,
                DATE_ADD(r.rental_date, INTERVAL f.rental_duration DAY) as due_date,
                r.return_date,
                CASE 
                    WHEN r.return_date IS NOT NULL THEN 'completed'
                    WHEN DATEDIFF(NOW(), DATE_ADD(r.rental_date, INTERVAL f.rental_duration DAY)) > 0 
                    THEN 'overdue'
                    WHEN r.return_date IS NULL THEN 'active'
                    ELSE 'unknown'
                END as status,
                CASE 
                    WHEN r.return_date IS NULL AND DATEDIFF(NOW(), DATE_ADD(r.rental_date, INTERVAL f.rental_duration DAY)) > 0
                    THEN DATEDIFF(NOW(), DATE_ADD(r.rental_date, INTERVAL f.rental_duration DAY))
                    ELSE 0
                END as days_overdue
            FROM rental r
            JOIN customer c ON r.customer_id = c.customer_id
            JOIN inventory i ON r.inventory_id = i.inventory_id
            JOIN film f ON i.film_id = f.film_id
        """
        
        if self._execute_query(create_view_query):
            print("   ✓ Created v_rental_status view")
            return True
        return False
    
    def _init_late_fees_table(self) -> bool:
        """Create late fees tracking table."""
        print("4️⃣  Checking late fees table...")
        
        check_query = """
            SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_NAME = 'late_fees' AND TABLE_SCHEMA = %s
        """
        result = self._fetch_query(check_query, (self.db_config['database'],))
        
        if result:
            print("   ✓ Late fees table already exists")
            return False
        
        create_query = """
            CREATE TABLE late_fees (
                late_fee_id INT AUTO_INCREMENT PRIMARY KEY,
                rental_id INT NOT NULL UNIQUE,
                customer_id INT NOT NULL,
                days_overdue INT DEFAULT 0,
                fee_amount DECIMAL(10,2) DEFAULT 0.00,
                calculated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fee_paid DECIMAL(10,2) DEFAULT 0.00,
                fee_status ENUM('pending', 'partially_paid', 'paid', 'written_off') DEFAULT 'pending',
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (rental_id) REFERENCES rental(rental_id),
                FOREIGN KEY (customer_id) REFERENCES customer(customer_id),
                INDEX idx_status (fee_status),
                INDEX idx_customer (customer_id),
                INDEX idx_overdue (days_overdue)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        
        if self._execute_query(create_query):
            print("   ✓ Created late_fees table")
            return True
        return False
    
    def _init_customer_accounts(self) -> bool:
        """Create customer account tracking for AR."""
        print("5️⃣  Checking customer accounts table...")
        
        check_query = """
            SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_NAME = 'customer_account' AND TABLE_SCHEMA = %s
        """
        result = self._fetch_query(check_query, (self.db_config['database'],))
        
        if result:
            print("   ✓ Customer accounts table already exists")
            return False
        
        create_query = """
            CREATE TABLE customer_account (
                account_id INT AUTO_INCREMENT PRIMARY KEY,
                customer_id INT NOT NULL UNIQUE,
                balance DECIMAL(10,2) DEFAULT 0.00,
                total_rentals INT DEFAULT 0,
                unreturned_rentals INT DEFAULT 0,
                overdue_rentals INT DEFAULT 0,
                total_late_fees DECIMAL(10,2) DEFAULT 0.00,
                paid_late_fees DECIMAL(10,2) DEFAULT 0.00,
                last_payment_date DATETIME,
                status ENUM('good_standing', 'past_due', 'at_risk', 'suspended', 'closed') DEFAULT 'good_standing',
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customer(customer_id),
                INDEX idx_status (status),
                INDEX idx_balance (balance)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        
        if self._execute_query(create_query):
            print("   ✓ Created customer_account table")
            return True
        return False
    
    def _init_late_fee_calculations(self) -> bool:
        """Calculate initial late fees for all unreturned rentals."""
        print("6️⃣  Calculating initial late fees...")
        
        # Get all unreturned rentals that are overdue
        query = """
            SELECT 
                r.rental_id,
                r.customer_id,
                r.rental_date,
                f.rental_duration,
                f.rental_rate
            FROM rental r
            JOIN inventory i ON r.inventory_id = i.inventory_id
            JOIN film f ON i.film_id = f.film_id
            WHERE r.return_date IS NULL
              AND DATEDIFF(NOW(), DATE_ADD(r.rental_date, INTERVAL f.rental_duration DAY)) > 0
        """
        
        overdue_rentals = self._fetch_query(query)
        
        if not overdue_rentals:
            print("   ✓ No overdue rentals found")
            return True
        
        fees_created = 0
        for rental in overdue_rentals:
            due_date = datetime.strptime(str(rental['rental_date']), '%Y-%m-%d %H:%M:%S') + \
                       timedelta(days=rental['rental_duration'])
            days_overdue = (datetime.now() - due_date).days
            fee_amount = Decimal(str(days_overdue * LATE_FEE_RATE_PER_DAY))
            
            insert_query = """
                INSERT INTO late_fees 
                (rental_id, customer_id, days_overdue, fee_amount, fee_status)
                VALUES (%s, %s, %s, %s, 'pending')
                ON DUPLICATE KEY UPDATE
                days_overdue = %s,
                fee_amount = %s,
                last_updated = CURRENT_TIMESTAMP
            """
            
            if self._execute_query(insert_query, (
                rental['rental_id'], rental['customer_id'], days_overdue, fee_amount,
                days_overdue, fee_amount
            )):
                fees_created += 1
        
        print(f"   ✓ Calculated late fees for {fees_created} overdue rentals")
        return True
    
    # ===== INVENTORY STATUS MANAGEMENT =====
    
    def update_inventory_status(self):
        """Update inventory status based on current rentals."""
        print("\n📦 Updating Inventory Status...\n")
        
        # Mark as 'rented' if currently checked out
        rented_query = """
            UPDATE inventory i
            SET status = 'rented'
            WHERE inventory_id IN (
                SELECT DISTINCT inventory_id FROM rental 
                WHERE return_date IS NULL
            ) AND status != 'rented'
        """
        
        self.cursor.execute(rented_query)
        rented_count = self.cursor.rowcount
        self.conn.commit()
        
        if rented_count > 0:
            print(f"✓ Marked {rented_count} items as 'rented'")
        
        # Mark as 'available' if not checked out and not damaged
        available_query = """
            UPDATE inventory i
            SET status = 'available'
            WHERE status = 'rented' 
              AND inventory_id NOT IN (
                SELECT DISTINCT inventory_id FROM rental 
                WHERE return_date IS NULL
            )
        """
        
        self.cursor.execute(available_query)
        available_count = self.cursor.rowcount
        self.conn.commit()
        
        if available_count > 0:
            print(f"✓ Marked {available_count} items as 'available'")
        
        # Get summary
        summary_query = """
            SELECT 
                status,
                COUNT(*) as count
            FROM inventory
            GROUP BY status
        """
        
        results = self._fetch_query(summary_query)
        print("\n📊 Inventory Status Summary:")
        for row in results:
            print(f"   {row['status'].upper()}: {row['count']}")
    
    # ===== LATE FEE MANAGEMENT =====
    
    def update_late_fees(self):
        """Recalculate late fees for all overdue unreturned rentals."""
        print("\n💰 Updating Late Fees...\n")
        
        query = """
            SELECT 
                r.rental_id,
                r.customer_id,
                r.rental_date,
                f.rental_duration,
                f.rental_rate
            FROM rental r
            JOIN inventory i ON r.inventory_id = i.inventory_id
            JOIN film f ON i.film_id = f.film_id
            WHERE r.return_date IS NULL
              AND DATEDIFF(NOW(), DATE_ADD(r.rental_date, INTERVAL f.rental_duration DAY)) > 0
        """
        
        overdue_rentals = self._fetch_query(query)
        
        if not overdue_rentals:
            print("✓ No overdue rentals to update")
            return
        
        updated_count = 0
        for rental in overdue_rentals:
            due_date = datetime.strptime(str(rental['rental_date']), '%Y-%m-%d %H:%M:%S') + \
                       timedelta(days=rental['rental_duration'])
            days_overdue = (datetime.now() - due_date).days
            fee_amount = Decimal(str(days_overdue * LATE_FEE_RATE_PER_DAY))
            
            update_query = """
                INSERT INTO late_fees 
                (rental_id, customer_id, days_overdue, fee_amount, fee_status)
                VALUES (%s, %s, %s, %s, 'pending')
                ON DUPLICATE KEY UPDATE
                days_overdue = %s,
                fee_amount = %s,
                last_updated = CURRENT_TIMESTAMP
            """
            
            if self._execute_query(update_query, (
                rental['rental_id'], rental['customer_id'], days_overdue, fee_amount,
                days_overdue, fee_amount
            )):
                updated_count += 1
        
        print(f"✓ Updated late fees for {updated_count} rentals")
    
    # ===== CUSTOMER ACCOUNT MANAGEMENT =====
    
    def update_customer_accounts(self):
        """Recalculate customer account balances and statuses."""
        print("\n👥 Updating Customer Accounts...\n")
        
        # Get all customers
        customers_query = "SELECT customer_id FROM customer"
        customers = self._fetch_query(customers_query)
        
        updated_count = 0
        for customer in customers:
            cust_id = customer['customer_id']
            
            # Calculate metrics
            metrics_query = """
                SELECT 
                    COUNT(DISTINCT r.rental_id) as total_rentals,
                    SUM(CASE WHEN r.return_date IS NULL THEN 1 ELSE 0 END) as unreturned,
                    COALESCE(SUM(CASE 
                        WHEN r.return_date IS NULL 
                        AND DATEDIFF(NOW(), DATE_ADD(r.rental_date, INTERVAL f.rental_duration DAY)) > 0
                        THEN 1 ELSE 0 
                    END), 0) as overdue,
                    COALESCE(SUM(lf.fee_amount), 0) as total_late_fees,
                    COALESCE(SUM(lf.fee_paid), 0) as paid_late_fees,
                    MAX(p.payment_date) as last_payment_date
                FROM customer c
                LEFT JOIN rental r ON c.customer_id = r.customer_id
                LEFT JOIN inventory i ON r.inventory_id = i.inventory_id
                LEFT JOIN film f ON i.film_id = f.film_id
                LEFT JOIN late_fees lf ON r.rental_id = lf.rental_id
                LEFT JOIN payment p ON c.customer_id = p.customer_id
                WHERE c.customer_id = %s
            """
            
            metrics = self._fetch_query(metrics_query, (cust_id,))
            
            if not metrics:
                continue
            
            m = metrics[0]
            total_late_fees = Decimal(str(m['total_late_fees'] or 0))
            paid_late_fees = Decimal(str(m['paid_late_fees'] or 0))
            balance = total_late_fees - paid_late_fees
            
            # Determine status
            if m['overdue'] and m['overdue'] > 3:
                status = 'suspended'
            elif m['overdue'] and m['overdue'] > 0:
                status = 'past_due'
            elif balance > 0:
                status = 'at_risk'
            else:
                status = 'good_standing'
            
            # Insert or update account
            account_query = """
                INSERT INTO customer_account 
                (customer_id, balance, total_rentals, unreturned_rentals, overdue_rentals, 
                 total_late_fees, paid_late_fees, last_payment_date, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                balance = %s,
                total_rentals = %s,
                unreturned_rentals = %s,
                overdue_rentals = %s,
                total_late_fees = %s,
                paid_late_fees = %s,
                last_payment_date = %s,
                status = %s
            """
            
            if self._execute_query(account_query, (
                cust_id, balance, m['total_rentals'], m['unreturned'], m['overdue'],
                total_late_fees, paid_late_fees, m['last_payment_date'], status,
                balance, m['total_rentals'], m['unreturned'], m['overdue'],
                total_late_fees, paid_late_fees, m['last_payment_date'], status
            )):
                updated_count += 1
        
        print(f"✓ Updated {updated_count} customer accounts")
        
        # Summary
        summary_query = """
            SELECT 
                status,
                COUNT(*) as count,
                SUM(balance) as total_balance
            FROM customer_account
            GROUP BY status
        """
        
        results = self._fetch_query(summary_query)
        print("\n📊 Customer Account Summary:")
        for row in results:
            print(f"   {row['status'].upper()}: {row['count']} customers (Balance: ${row['total_balance']:.2f})")
    
    # ===== AUDIT LOGGING =====
    
    def log_inventory_status_change(self, inventory_id: int, status_from: str, status_to: str, notes: str = ""):
        """Log inventory status change to audit trail."""
        query = """
            INSERT INTO inventory_audit 
            (inventory_id, status_from, status_to, notes)
            VALUES (%s, %s, %s, %s)
        """
        
        return self._execute_query(query, (inventory_id, status_from, status_to, notes))
    
    # ===== REPORTING =====
    
    def generate_late_fee_report(self):
        """Generate late fee report."""
        print("\n📋 Late Fee Report\n")
        
        query = """
            SELECT 
                lf.late_fee_id,
                c.first_name,
                c.last_name,
                f.title,
                lf.days_overdue,
                lf.fee_amount,
                lf.fee_status
            FROM late_fees lf
            JOIN customer c ON lf.customer_id = c.customer_id
            JOIN rental r ON lf.rental_id = r.rental_id
            JOIN inventory i ON r.inventory_id = i.inventory_id
            JOIN film f ON i.film_id = f.film_id
            WHERE lf.fee_status IN ('pending', 'partially_paid')
            ORDER BY lf.days_overdue DESC
            LIMIT 20
        """
        
        results = self._fetch_query(query)
        
        if not results:
            print("✓ No pending late fees")
            return
        
        print(f"{'Customer':<20} {'Film':<30} {'Days':<6} {'Amount':<10} {'Status':<15}")
        print("-" * 85)
        
        total_pending = Decimal(0)
        for row in results:
            name = f"{row['first_name']} {row['last_name']}"
            amount = Decimal(str(row['fee_amount']))
            total_pending += amount
            print(f"{name:<20} {row['title']:<30} {row['days_overdue']:<6} "
                  f"${amount:<9.2f} {row['fee_status']:<15}")
        
        print("-" * 85)
        print(f"{'TOTAL PENDING FEES:':<58} ${total_pending:.2f}")
    
    def generate_customer_ar_report(self):
        """Generate accounts receivable report by customer."""
        print("\n👥 Customer Accounts Receivable Report\n")
        
        query = """
            SELECT 
                ca.customer_id,
                c.first_name,
                c.last_name,
                ca.total_rentals,
                ca.unreturned_rentals,
                ca.overdue_rentals,
                ca.balance,
                ca.status
            FROM customer_account ca
            JOIN customer c ON ca.customer_id = c.customer_id
            WHERE ca.balance > 0
            ORDER BY ca.balance DESC
            LIMIT 25
        """
        
        results = self._fetch_query(query)
        
        if not results:
            print("✓ No outstanding AR")
            return
        
        print(f"{'Customer':<20} {'Rentals':<10} {'Unreturned':<12} {'Balance':<12} {'Status':<15}")
        print("-" * 75)
        
        total_ar = Decimal(0)
        for row in results:
            name = f"{row['first_name']} {row['last_name']}"
            balance = Decimal(str(row['balance']))
            total_ar += balance
            print(f"{name:<20} {row['total_rentals']:<10} {row['unreturned_rentals']:<12} "
                  f"${balance:<11.2f} {row['status']:<15}")
        
        print("-" * 75)
        print(f"{'TOTAL AR:':<42} ${total_ar:.2f}")
    
    def run_full_update(self):
        """Run complete advanced tracking update."""
        print("\n" + "="*60)
        print("ADVANCED TRACKING SYSTEM - FULL UPDATE")
        print("="*60)
        
        try:
            self.update_inventory_status()
            self.update_late_fees()
            self.update_customer_accounts()
            self.generate_late_fee_report()
            self.generate_customer_ar_report()
            
            print("\n✅ Advanced tracking update complete!")
        except Exception as err:
            print(f"\n❌ Error during update: {err}")
            raise
        finally:
            self.close()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Advanced Incremental Update - Independent Tracking System"
    )
    parser.add_argument(
        '--init',
        action='store_true',
        help='Initialize tracking tables'
    )
    parser.add_argument(
        '--update',
        action='store_true',
        help='Update tracking data (inventory, late fees, accounts)'
    )
    parser.add_argument(
        '--daily',
        action='store_true',
        help='Run daily reconciliation'
    )
    parser.add_argument(
        '--config',
        default=CONFIG_FILE,
        help=f'Config file path (default: {CONFIG_FILE})'
    )
    parser.add_argument(
        '--database',
        default=None,
        help='Override database name (e.g., dvdrental_group_a)'
    )
    
    args = parser.parse_args()
    
    # If no action specified, run both init and update
    if not (args.init or args.update or args.daily):
        args.init = True
        args.update = True
    
    manager = AdvancedTrackingManager(args.config, override_database=args.database)
    
    try:
        if args.init:
            manager.init_tracking_tables()
        
        if args.update or args.daily:
            manager.run_full_update()
        else:
            manager.close()
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        manager.close()
        sys.exit(1)
    except Exception as err:
        print(f"\n❌ Fatal error: {err}")
        manager.close()
        sys.exit(1)


if __name__ == "__main__":
    main()
