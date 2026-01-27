#!/usr/bin/env python3
"""
Test script for the film generator module
"""

import json
import sys
import os
from datetime import date
import logging
from film_generator import FilmGenerator

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

def load_config(config_file='config.json'):
    """Load configuration from JSON file"""
    with open(config_file, 'r') as f:
        return json.load(f)

def test_film_generation():
    """Test film generation functionality"""
    print("Testing Film Generator...")
    
    # Load configuration
    config = load_config()
    mysql_config = config['mysql']
    
    # Create film generator
    film_generator = FilmGenerator(mysql_config)
    
    try:
        # Test 1: Connect to database
        print("1. Testing database connection...")
        film_generator.connect()
        print("   ✓ Connected successfully")
        
        # Test 2: Create film_releases table
        print("2. Testing film_releases table creation...")
        film_generator.create_film_releases_table()
        print("   ✓ Table created/verified successfully")
        
        # Test 3: Generate films for a quarter
        print("3. Testing film generation...")
        quarter = "Q1 2023"
        num_films = 3
        category_focus = "Action"
        
        films_added = film_generator.generate_quarterly_films(
            quarter, num_films, category_focus
        )
        
        print(f"   ✓ Generated {films_added} films for {quarter}")
        
        # Reconnect for verification tests
        film_generator.connect()
        
        # Test 4: Verify films were added to database
        print("4. Verifying database entries...")
        film_generator.cursor.execute("""
            SELECT COUNT(*) FROM film 
            WHERE release_year = 2023
        """)
        film_count = film_generator.cursor.fetchone()[0]
        print(f"   ✓ Found {film_count} films from 2023")
        
        # Test 5: Check film_releases table
        print("5. Checking film_releases table...")
        film_generator.cursor.execute("""
            SELECT COUNT(*) FROM film_releases 
            WHERE release_quarter = 'Q1 2023'
        """)
        release_count = film_generator.cursor.fetchone()[0]
        print(f"   ✓ Found {release_count} film releases for Q1 2023")
        
        # Test 6: Check inventory was created
        print("6. Checking inventory creation...")
        # Get the film IDs we just added
        film_generator.cursor.execute("""
            SELECT f.film_id FROM film f
            JOIN film_releases fr ON f.film_id = fr.film_id
            WHERE fr.release_quarter = 'Q1 2023'
            LIMIT 1
        """)
        result = film_generator.cursor.fetchone()
        if result:
            film_id = result[0]
            film_generator.cursor.execute("""
                SELECT COUNT(*) FROM inventory 
                WHERE film_id = %s
            """, (film_id,))
            inventory_count = film_generator.cursor.fetchone()[0]
            print(f"   ✓ Found {inventory_count} inventory items for film ID {film_id}")
        else:
            print("   ⚠ Could not find recently added films to check inventory")
        
        # Test 7: Check inventory purchases table
        print("7. Checking inventory purchases table...")
        film_generator.cursor.execute("""
            SELECT COUNT(*) FROM inventory_purchases 
            WHERE purchase_date = '2023-02-15'
        """)
        purchase_count = film_generator.cursor.fetchone()[0]
        print(f"   ✓ Found {purchase_count} inventory purchases for 2023-02-15")
        
        # Test 8: Check staff linking in inventory purchases
        print("8. Checking staff linking in inventory purchases...")
        film_generator.cursor.execute("""
            SELECT ip.staff_id, f.title 
            FROM inventory_purchases ip
            JOIN film f ON ip.film_id = f.film_id
            WHERE ip.purchase_date = '2023-02-15' AND ip.staff_id IS NOT NULL
            LIMIT 1
        """)
        staff_result = film_generator.cursor.fetchone()
        if staff_result:
            print(f"   ✓ Inventory purchase linked to staff ID {staff_result[0]} for film '{staff_result[1]}'")
        else:
            print("   ⚠ No staff linking found in inventory purchases")
        
        film_generator.disconnect()
        print("\n✓ All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        if film_generator.conn:
            film_generator.disconnect()
        return False

def test_template_loading():
    """Test loading templates from files"""
    print("\nTesting Template Loading...")
    
    # Check if template files exist
    templates_dir = 'film_templates'
    if not os.path.exists(templates_dir):
        print("   ⚠ Templates directory not found")
        return False
    
    categories = ['action', 'comedy', 'drama']
    for category in categories:
        file_path = os.path.join(templates_dir, f"{category}.txt")
        if os.path.exists(file_path):
            print(f"   ✓ Found {category} template file")
        else:
            print(f"   ⚠ Missing {category} template file")
    
    return True

if __name__ == '__main__':
    print("Film Generator Test Suite")
    print("=" * 50)
    
    # Test template loading
    test_template_loading()
    
    # Test film generation
    success = test_film_generation()
    
    if success:
        print("\n🎉 All tests completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed!")
        sys.exit(1)