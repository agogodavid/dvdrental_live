#!/usr/bin/env python3
"""
Inventory Analysis Examples
Demonstrates how to use the new date_purchased and staff_id columns
for analyzing inventory profitability and batch performance
"""

import mysql.connector
from mysql.connector import Error
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Tuple

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def load_config(config_file='config.json'):
    """Load configuration from JSON file"""
    with open(config_file, 'r') as f:
        return json.load(f)


class InventoryAnalyzer:
    """Analyze inventory profitability and batch performance"""
    
    def __init__(self, config: dict):
        self.config = config['mysql']
        self.db_name = self.config['database']
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """Establish connection"""
        try:
            self.conn = mysql.connector.connect(
                host=self.config['host'],
                user=self.config['user'],
                password=self.config['password'],
                database=self.db_name
            )
            self.cursor = self.conn.cursor(dictionary=True)
            logger.info(f"Connected to {self.db_name}")
        except Error as e:
            logger.error(f"Connection failed: {e}")
            raise
    
    def disconnect(self):
        """Close connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
    
    def get_batch_profitability(self, date_purchased=None):
        """
        Get profitability analysis for a specific purchase batch
        
        Args:
            date_purchased: Date string (YYYY-MM-DD) or None for all batches
        """
        logger.info("\n" + "=" * 80)
        logger.info("BATCH PROFITABILITY ANALYSIS")
        logger.info("=" * 80)
        
        query = """
        SELECT 
            i.date_purchased,
            CONCAT(s.first_name, ' ', s.last_name) as staff_member,
            COUNT(DISTINCT i.inventory_id) as items_purchased,
            COUNT(DISTINCT i.film_id) as unique_films,
            ROUND(SUM(f.replacement_cost), 2) as investment,
            ROUND(SUM(f.rental_rate) * COUNT(DISTINCT r.rental_id), 2) as revenue,
            ROUND(SUM(f.rental_rate) * COUNT(DISTINCT r.rental_id) - SUM(f.replacement_cost) * COUNT(DISTINCT i.inventory_id), 2) as profit,
            ROUND(((SUM(f.rental_rate) * COUNT(DISTINCT r.rental_id) - SUM(f.replacement_cost) * COUNT(DISTINCT i.inventory_id)) / SUM(f.replacement_cost) * 100), 2) as roi_percent,
            DATEDIFF(CURDATE(), i.date_purchased) as days_in_stock
        FROM inventory i
        JOIN film f ON i.film_id = f.film_id
        JOIN staff s ON i.staff_id = s.staff_id
        LEFT JOIN rental r ON i.inventory_id = r.inventory_id
        """
        
        params = []
        
        if date_purchased:
            query += " WHERE i.date_purchased = %s"
            params.append(date_purchased)
        
        query += """
        GROUP BY i.date_purchased, i.staff_id, s.staff_id
        ORDER BY profit DESC
        """
        
        try:
            self.cursor.execute(query, params)
            results = self.cursor.fetchall()
            
            if not results:
                logger.info("No inventory data found")
                return results
            
            for row in results:
                logger.info(f"\n📦 Batch: {row['date_purchased']} (Sourced by: {row['staff_member']})")
                logger.info(f"   Items: {row['items_purchased']} | Films: {row['unique_films']}")
                logger.info(f"   Investment: ${row['investment']}")
                logger.info(f"   Revenue: ${row['revenue']}")
                logger.info(f"   Profit: ${row['profit']}")
                logger.info(f"   ROI: {row['roi_percent']}%")
                logger.info(f"   Days in Stock: {row['days_in_stock']}")
            
            return results
        
        except Error as e:
            logger.error(f"Query error: {e}")
            return []
    
    def get_staff_performance(self):
        """Analyze performance of staff members based on inventory sourcing"""
        logger.info("\n" + "=" * 80)
        logger.info("STAFF PERFORMANCE ANALYSIS")
        logger.info("=" * 80)
        
        query = """
        SELECT 
            s.staff_id,
            CONCAT(s.first_name, ' ', s.last_name) as staff_member,
            COUNT(DISTINCT i.inventory_id) as total_items_sourced,
            COUNT(DISTINCT DATE(i.date_purchased)) as purchase_dates,
            ROUND(SUM(f.replacement_cost), 2) as total_investment,
            ROUND(SUM(f.rental_rate) * COUNT(DISTINCT r.rental_id), 2) as total_revenue,
            ROUND(SUM(f.rental_rate) * COUNT(DISTINCT r.rental_id) - SUM(f.replacement_cost), 2) as total_profit,
            ROUND(((SUM(f.rental_rate) * COUNT(DISTINCT r.rental_id) - SUM(f.replacement_cost)) / SUM(f.replacement_cost) * 100), 2) as roi_percent,
            ROUND(COUNT(DISTINCT r.rental_id) / NULLIF(COUNT(DISTINCT i.inventory_id), 0), 2) as avg_rentals_per_item
        FROM staff s
        JOIN inventory i ON s.staff_id = i.staff_id
        JOIN film f ON i.film_id = f.film_id
        LEFT JOIN rental r ON i.inventory_id = r.inventory_id
        GROUP BY s.staff_id, s.first_name, s.last_name
        ORDER BY total_profit DESC
        """
        
        try:
            self.cursor.execute(query)
            results = self.cursor.fetchall()
            
            if not results:
                logger.info("No staff inventory data found")
                return results
            
            for row in results:
                logger.info(f"\n👤 {row['staff_member']} (ID: {row['staff_id']})")
                logger.info(f"   Items Sourced: {row['total_items_sourced']}")
                logger.info(f"   Purchase Batches: {row['purchase_dates']}")
                logger.info(f"   Total Investment: ${row['total_investment']}")
                logger.info(f"   Total Revenue: ${row['total_revenue']}")
                logger.info(f"   Total Profit: ${row['total_profit']}")
                logger.info(f"   ROI: {row['roi_percent']}%")
                logger.info(f"   Avg Rentals per Item: {row['avg_rentals_per_item']}")
            
            return results
        
        except Error as e:
            logger.error(f"Query error: {e}")
            return []
    
    def get_aging_inventory(self, days_threshold: int = 30):
        """
        Identify slow-moving inventory
        
        Args:
            days_threshold: How many days before considering inventory "aged"
        """
        logger.info("\n" + "=" * 80)
        logger.info(f"AGING INVENTORY ANALYSIS (> {days_threshold} days)")
        logger.info("=" * 80)
        
        query = f"""
        SELECT 
            i.inventory_id,
            f.title,
            i.date_purchased,
            DATEDIFF(CURDATE(), i.date_purchased) as days_in_stock,
            COUNT(r.rental_id) as total_rentals,
            CASE 
                WHEN COUNT(r.rental_id) = 0 THEN 'Never Rented'
                WHEN COUNT(r.rental_id) < 3 THEN 'Low Activity'
                WHEN COUNT(r.rental_id) < 10 THEN 'Moderate Activity'
                ELSE 'High Activity'
            END as performance_tier,
            MAX(r.rental_date) as last_rental_date,
            ROUND(f.rental_rate * COUNT(r.rental_id), 2) as revenue_generated,
            ROUND(f.replacement_cost, 2) as cost
        FROM inventory i
        JOIN film f ON i.film_id = f.film_id
        LEFT JOIN rental r ON i.inventory_id = r.inventory_id
        GROUP BY i.inventory_id, i.date_purchased, f.film_id
        HAVING days_in_stock > {days_threshold}
        ORDER BY total_rentals ASC, days_in_stock DESC
        LIMIT 20
        """
        
        try:
            self.cursor.execute(query)
            results = self.cursor.fetchall()
            
            if not results:
                logger.info(f"No aged inventory found (threshold: {days_threshold} days)")
                return results
            
            logger.info(f"Found {len(results)} aged items")
            
            for row in results:
                logger.info(f"\n📼 {row['title']} (ID: {row['inventory_id']})")
                logger.info(f"   Purchase Date: {row['date_purchased']}")
                logger.info(f"   Days in Stock: {row['days_in_stock']}")
                logger.info(f"   Performance: {row['performance_tier']}")
                logger.info(f"   Rentals: {row['total_rentals']}")
                logger.info(f"   Revenue: ${row['revenue_generated']}")
                logger.info(f"   Cost: ${row['cost']}")
                logger.info(f"   Last Rented: {row['last_rental_date'] or 'Never'}")
            
            return results
        
        except Error as e:
            logger.error(f"Query error: {e}")
            return []
    
    def get_breakeven_analysis(self):
        """Analyze how quickly batches break even"""
        logger.info("\n" + "=" * 80)
        logger.info("BREAKEVEN ANALYSIS BY BATCH")
        logger.info("=" * 80)
        
        query = """
        SELECT 
            i.date_purchased,
            CONCAT(s.first_name, ' ', s.last_name) as staff_member,
            COUNT(DISTINCT i.inventory_id) as items,
            ROUND(SUM(f.replacement_cost), 2) as total_cost,
            ROUND(SUM(f.rental_rate), 2) as daily_rental_potential,
            CEIL(SUM(f.replacement_cost) / NULLIF(SUM(f.rental_rate), 0)) as rentals_to_breakeven,
            COUNT(DISTINCT r.rental_id) as actual_rentals,
            ROUND((COUNT(DISTINCT r.rental_id) / NULLIF(CEIL(SUM(f.replacement_cost) / NULLIF(SUM(f.rental_rate), 0)), 0)) * 100, 2) as breakeven_percent,
            DATEDIFF(CURDATE(), i.date_purchased) as days_to_breakeven_actual
        FROM inventory i
        JOIN film f ON i.film_id = f.film_id
        JOIN staff s ON i.staff_id = s.staff_id
        LEFT JOIN rental r ON i.inventory_id = r.inventory_id
        GROUP BY i.date_purchased, i.staff_id, s.staff_id
        ORDER BY breakeven_percent DESC
        """
        
        try:
            self.cursor.execute(query)
            results = self.cursor.fetchall()
            
            if not results:
                logger.info("No inventory data found")
                return results
            
            for row in results:
                status = "✓ PROFITABLE" if row['breakeven_percent'] >= 100 else "⚠ BELOW TARGET"
                logger.info(f"\n{status} - Batch: {row['date_purchased']}")
                logger.info(f"   Staff: {row['staff_member']}")
                logger.info(f"   Items: {row['items']}")
                logger.info(f"   Investment: ${row['total_cost']}")
                logger.info(f"   Rentals Needed to Breakeven: {row['rentals_to_breakeven']}")
                logger.info(f"   Actual Rentals: {row['actual_rentals']}")
                logger.info(f"   Breakeven Achievement: {row['breakeven_percent']}%")
            
            return results
        
        except Error as e:
            logger.error(f"Query error: {e}")
            return []
    
    def get_store_batch_performance(self):
        """Analyze how different stores perform with different batches"""
        logger.info("\n" + "=" * 80)
        logger.info("STORE PERFORMANCE BY BATCH")
        logger.info("=" * 80)
        
        query = """
        SELECT 
            i.date_purchased,
            st.store_id,
            a.city,
            COUNT(DISTINCT i.inventory_id) as items_from_batch,
            ROUND(SUM(f.rental_rate) * COUNT(DISTINCT r.rental_id), 2) as revenue,
            ROUND(SUM(f.rental_rate) * COUNT(DISTINCT r.rental_id) - SUM(f.replacement_cost), 2) as profit,
            ROUND(COUNT(DISTINCT r.rental_id) / NULLIF(COUNT(DISTINCT i.inventory_id), 0), 2) as utilization_rate
        FROM inventory i
        JOIN store st ON i.store_id = st.store_id
        JOIN address a ON st.address_id = a.address_id
        JOIN film f ON i.film_id = f.film_id
        LEFT JOIN rental r ON i.inventory_id = r.inventory_id
        GROUP BY i.date_purchased, st.store_id, a.city
        ORDER BY i.date_purchased DESC, profit DESC
        """
        
        try:
            self.cursor.execute(query)
            results = self.cursor.fetchall()
            
            if not results:
                logger.info("No store data found")
                return results
            
            for row in results:
                logger.info(f"\n🏪 Store {row['store_id']} ({row['city']}) - Batch: {row['date_purchased']}")
                logger.info(f"   Items: {row['items_from_batch']}")
                logger.info(f"   Revenue: ${row['revenue']}")
                logger.info(f"   Profit: ${row['profit']}")
                logger.info(f"   Utilization: {row['utilization_rate']} rentals/item")
            
            return results
        
        except Error as e:
            logger.error(f"Query error: {e}")
            return []


def main():
    """Run all analyses"""
    config = load_config()
    analyzer = InventoryAnalyzer(config)
    
    try:
        analyzer.connect()
        
        # Run all analyses
        analyzer.get_batch_profitability()
        analyzer.get_staff_performance()
        analyzer.get_aging_inventory(days_threshold=30)
        analyzer.get_breakeven_analysis()
        analyzer.get_store_batch_performance()
        
        logger.info("\n" + "=" * 80)
        logger.info("✅ ANALYSIS COMPLETE")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        analyzer.disconnect()


if __name__ == '__main__':
    main()
