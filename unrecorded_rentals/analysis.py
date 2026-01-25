#!/usr/bin/env python3
"""
Unrecorded Rentals Analysis Tool

Diagnoses the scope and implications of NULL return_date rentals
and provides metrics to understand the data quality issue.
"""

import mysql.connector
from datetime import datetime, timedelta
import json

def connect_db(config_file='config.json'):
    """Connect to the DVD rental database"""
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    conn = mysql.connector.connect(
        host=config['mysql']['host'],
        user=config['mysql']['user'],
        password=config['mysql']['password'],
        database=config['mysql']['database']
    )
    return conn

def analyze_unrecorded_rentals(conn):
    """Comprehensive analysis of NULL return_date rentals"""
    cursor = conn.cursor(dictionary=True)
    
    print("\n" + "="*70)
    print("UNRECORDED RENTALS ANALYSIS")
    print("="*70)
    
    # 1. Count overview
    print("\n1. SCALE OF THE PROBLEM")
    print("-" * 70)
    
    cursor.execute("SELECT COUNT(*) as total FROM rental")
    total_rentals = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) as unrecorded FROM rental WHERE return_date IS NULL")
    unrecorded = cursor.fetchone()['unrecorded']
    
    cursor.execute("SELECT COUNT(*) as recorded FROM rental WHERE return_date IS NOT NULL")
    recorded = cursor.fetchone()['recorded']
    
    pct_unrecorded = (unrecorded / total_rentals * 100) if total_rentals > 0 else 0
    
    print(f"Total Rentals:        {total_rentals:>10,}")
    print(f"With Return Date:     {recorded:>10,} ({100-pct_unrecorded:>5.1f}%)")
    print(f"WITHOUT Return Date:  {unrecorded:>10,} ({pct_unrecorded:>5.1f}%) ⚠️")
    
    # 2. Temporal analysis
    print("\n2. WHEN WERE UNRECORDED RENTALS MADE?")
    print("-" * 70)
    
    cursor.execute("""
        SELECT 
            YEAR(rental_date) as rental_year,
            MONTH(rental_date) as rental_month,
            COUNT(*) as count
        FROM rental
        WHERE return_date IS NULL
        GROUP BY YEAR(rental_date), MONTH(rental_date)
        ORDER BY rental_year DESC, rental_month DESC
        LIMIT 12
    """)
    
    for row in cursor.fetchall():
        year_month = f"{row['rental_year']}-{row['rental_month']:02d}"
        print(f"  {year_month}: {row['count']:>6,} unrecorded rentals")
    
    # 3. Revenue impact
    print("\n3. FINANCIAL IMPACT")
    print("-" * 70)
    
    cursor.execute("""
        SELECT 
            COUNT(*) as unrecorded_rentals,
            COALESCE(SUM(f.rental_rate), 0) as lost_revenue
        FROM rental r
        JOIN inventory i ON r.inventory_id = i.inventory_id
        JOIN film f ON i.film_id = f.film_id
        WHERE r.return_date IS NULL
    """)
    
    result = cursor.fetchone()
    lost_revenue = result['lost_revenue']
    
    print(f"Unrecorded Rentals:   {result['unrecorded_rentals']:>10,}")
    print(f"Lost Rental Revenue:  ${lost_revenue:>15,.2f}")
    print(f"Avg per Rental:       ${lost_revenue/result['unrecorded_rentals'] if result['unrecorded_rentals'] > 0 else 0:>15,.2f}")
    
    # 4. Missing payments
    print("\n4. MISSING PAYMENT RECORDS")
    print("-" * 70)
    
    cursor.execute("""
        SELECT COUNT(*) as orphan_rentals
        FROM rental r
        LEFT JOIN payment p ON r.rental_id = p.rental_id
        WHERE r.return_date IS NULL AND p.payment_id IS NULL
    """)
    
    orphan_rentals = cursor.fetchone()['orphan_rentals']
    
    print(f"Rentals with NO payments: {orphan_rentals:>10,}")
    print(f"These rentals have no:")
    print(f"  - Payment records")
    print(f"  - Return dates")
    print(f"  - Completion status")
    
    # 5. Inventory analysis
    print("\n5. INVENTORY IMPACT")
    print("-" * 70)
    
    cursor.execute("""
        SELECT 
            COUNT(DISTINCT i.inventory_id) as items_stuck,
            COUNT(DISTINCT r.customer_id) as customers_holding
        FROM rental r
        JOIN inventory i ON r.inventory_id = i.inventory_id
        WHERE r.return_date IS NULL
    """)
    
    result = cursor.fetchone()
    
    print(f"Inventory items 'stuck': {result['items_stuck']:>8,}")
    print(f"Customers 'holding':     {result['customers_holding']:>8,}")
    print(f"(These items appear unavailable indefinitely)")
    
    # 6. Age of oldest unrecorded rentals
    print("\n6. AGE OF UNRECORDED RENTALS")
    print("-" * 70)
    
    cursor.execute("""
        SELECT 
            MIN(rental_date) as oldest,
            MAX(rental_date) as newest,
            DATEDIFF(NOW(), MIN(rental_date)) as days_old_oldest
        FROM rental
        WHERE return_date IS NULL
    """)
    
    result = cursor.fetchone()
    
    print(f"Oldest unrecorded:    {result['oldest']}")
    print(f"Newest unrecorded:    {result['newest']}")
    print(f"Age of oldest:        {result['days_old_oldest']} days")
    
    # 7. Data quality metrics
    print("\n7. DATA QUALITY ASSESSMENT")
    print("-" * 70)
    
    quality_score = (recorded / total_rentals * 100) if total_rentals > 0 else 0
    
    if quality_score >= 95:
        status = "✅ EXCELLENT"
    elif quality_score >= 80:
        status = "⚠️  ACCEPTABLE"
    elif quality_score >= 60:
        status = "❌ POOR"
    else:
        status = "🔴 CRITICAL"
    
    print(f"Data Completeness: {quality_score:.1f}% {status}")
    print(f"Records with required data:")
    print(f"  - Return dates: {quality_score:.1f}%")
    print(f"  - Missing data: {pct_unrecorded:.1f}%")
    
    # 8. Recommendations
    print("\n8. RECOMMENDATIONS")
    print("-" * 70)
    print("""
✅ OPERATIONAL LAYER (DO NOT MODIFY):
   - Keep all original rental records intact
   - Preserve audit trail for compliance
   - Never alter return_date directly in rental table

✅ ANALYTICAL LAYER (SAFE TO CREATE):
   - Create views with estimated return dates
   - Use for reporting and analysis
   - Calculate with business logic (e.g., rental_date + 3-7 days)
   
✅ PREVENTION:
   - Fix the transaction generation to create matching returns
   - Add validation: every rental must get a return record
   - Implement data quality checks in ETL pipeline
    """)
    
    cursor.close()
    return {
        'total': total_rentals,
        'recorded': recorded,
        'unrecorded': unrecorded,
        'pct_unrecorded': pct_unrecorded,
        'lost_revenue': lost_revenue
    }

if __name__ == '__main__':
    try:
        conn = connect_db()
        stats = analyze_unrecorded_rentals(conn)
        conn.close()
        
        print("\n" + "="*70)
        print("SUMMARY")
        print("="*70)
        print(f"See solutions.md for recommended approaches")
        print(f"See data_integrity_principles.md for why this matters")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Make sure MySQL is running and config.json is set up correctly")
