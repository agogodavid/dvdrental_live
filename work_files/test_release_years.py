#!/usr/bin/env python3
"""Test that films are generated with appropriate release years"""

from generator import DVDRentalDataGenerator
import mysql.connector
from datetime import datetime

# Load config from shared/configs
import json
with open('shared/configs/config.json', 'r') as f:
    config = json.load(f)

# Prepare config for generator
gen_config = {
    **config['mysql'],
    'simulation': config['simulation'],
    'generation': config['generation']
}

# Get start date
start_date_str = gen_config['simulation'].get('start_date', '2001-12-30')
start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
start_year = start_date.year

print(f'=== Film Release Year Test ===')
print(f'Simulation start date: {start_date} (year: {start_year})')
print()

# Create test database
conn = mysql.connector.connect(host='localhost', user='root', password='root')
cursor = conn.cursor()
cursor.execute('DROP DATABASE IF EXISTS dvdrental_year_test')
cursor.execute('CREATE DATABASE dvdrental_year_test')
cursor.close()
conn.close()

# Override database
gen_config['database'] = 'dvdrental_year_test'

# Test generator with 50 films
print('=== Testing Generator with 50 films ===')
gen = DVDRentalDataGenerator(gen_config)
gen.connect()

# Create minimal schema
gen.create_database()
gen.create_schema()
gen.seed_base_data()

# Seed films with start date
gen.seed_films(50, start_date=start_date)

# Check release years
gen.cursor.execute("""
    SELECT MIN(release_year) as min_year, 
           MAX(release_year) as max_year, 
           COUNT(*) as total_films,
           COUNT(CASE WHEN release_year > %s THEN 1 END) as future_films
    FROM film
""", (start_year,))

result = gen.cursor.fetchone()
min_year, max_year, total_films, future_films = result

print(f'✓ Total films: {total_films}')
print(f'✓ Release year range: {min_year} - {max_year}')
print(f'✓ Films with release year > {start_year}: {future_films}')
print()

# Check some sample films
gen.cursor.execute("""
    SELECT film_id, title, release_year 
    FROM film 
    ORDER BY release_year DESC 
    LIMIT 10
""")

print('Sample of most recent films:')
for film_id, title, release_year in gen.cursor.fetchall():
    print(f'  {film_id:<4} {title:<40} {release_year}')
print()

if future_films == 0 and max_year <= start_year:
    print('✅ SUCCESS: All films have release years at or before simulation start!')
    print(f'   Expected: release_year ≤ {start_year}')
    print(f'   Got: {min_year} ≤ release_year ≤ {max_year}')
else:
    print(f'❌ FAIL: Found {future_films} films with release years after {start_year}!')
    print(f'   Max release year: {max_year}')
    print(f'   Simulation start year: {start_year}')

gen.disconnect()

# Clean up test database
conn = mysql.connector.connect(host='localhost', user='root', password='root')
cursor = conn.cursor()
cursor.execute('DROP DATABASE IF EXISTS dvdrental_year_test')
cursor.close()
conn.close()
print('\nTest database cleaned up.')
