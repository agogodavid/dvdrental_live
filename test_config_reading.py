#!/usr/bin/env python3
"""Test that generator reads films_count and stores_count from config"""

from generator import DVDRentalDataGenerator
import mysql.connector
import json

# Load config from shared/configs
with open('shared/configs/config.json', 'r') as f:
    config = json.load(f)

# Prepare config for generator
gen_config = {
    **config['mysql'],
    'simulation': config['simulation'],
    'generation': config['generation']
}

print('=== Config Check ===')
print(f'films_count from config: {gen_config["generation"]["films_count"]}')
print(f'stores_count from config: {gen_config["generation"]["stores_count"]}')
print()

# Create test database
conn = mysql.connector.connect(host='localhost', user='root', password='root')
cursor = conn.cursor()
cursor.execute('DROP DATABASE IF EXISTS dvdrental_config_test')
cursor.execute('CREATE DATABASE dvdrental_config_test')
cursor.close()
conn.close()

# Override database
gen_config['database'] = 'dvdrental_config_test'

# Test generator
print('=== Testing Generator Initialization ===')
gen = DVDRentalDataGenerator(gen_config)
gen.connect()
gen.initialize_and_seed()

# Check results
gen.cursor.execute('SELECT COUNT(*) FROM film')
film_count = gen.cursor.fetchone()[0]
gen.cursor.execute('SELECT COUNT(*) FROM store')
store_count = gen.cursor.fetchone()[0]

print(f'✓ Films created: {film_count}')
print(f'✓ Stores created: {store_count}')
print()

# The shared/configs/config.json has 500 films and 2 stores
expected_films = gen_config["generation"]["films_count"]
expected_stores = gen_config["generation"]["stores_count"]

if film_count == expected_films and store_count == expected_stores:
    print(f'✅ SUCCESS: Config values are being read correctly!')
    print(f'   Expected {expected_films} films and {expected_stores} stores')
    print(f'   Got {film_count} films and {store_count} stores')
else:
    print(f'❌ FAIL: Expected {expected_films} films and {expected_stores} stores')
    print(f'   Got {film_count} films and {store_count} stores')

gen.disconnect()

# Clean up test database
conn = mysql.connector.connect(host='localhost', user='root', password='root')
cursor = conn.cursor()
cursor.execute('DROP DATABASE IF EXISTS dvdrental_config_test')
cursor.close()
conn.close()
print('\nTest database cleaned up.')
