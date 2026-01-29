#!/usr/bin/env python3
"""Fix film release years in existing database to match simulation timeline"""

import mysql.connector
import random
import sys

def fix_film_years(database_name, sim_start_year=2001, dry_run=True):
    """
    Fix film release years to be logically consistent with simulation timeline
    
    Args:
        database_name: Name of the database to fix
        sim_start_year: Year the simulation starts (default 2001)
        dry_run: If True, only show what would be changed without making changes
    """
    print(f"{'DRY RUN - ' if dry_run else ''}Fixing film release years in {database_name}")
    print(f"Simulation start year: {sim_start_year}")
    print()
    
    # Connect to database
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='root',
        database=database_name
    )
    cursor = conn.cursor()
    
    # Get current state
    cursor.execute("""
        SELECT 
            MIN(release_year) as min_year,
            MAX(release_year) as max_year,
            COUNT(*) as total_films,
            COUNT(CASE WHEN release_year > %s THEN 1 END) as future_films
        FROM film
    """, (sim_start_year,))
    
    min_year, max_year, total_films, future_films = cursor.fetchone()
    
    print(f"Current state:")
    print(f"  Total films: {total_films}")
    print(f"  Release year range: {min_year} - {max_year}")
    print(f"  Films with year > {sim_start_year}: {future_films}")
    print()
    
    if future_films == 0:
        print("✅ No films need fixing - all release years are valid!")
        cursor.close()
        conn.close()
        return
    
    # Get films that need fixing
    cursor.execute("""
        SELECT film_id, title, release_year 
        FROM film 
        WHERE release_year > %s
        ORDER BY release_year DESC
    """, (sim_start_year,))
    
    films_to_fix = cursor.fetchall()
    
    print(f"Found {len(films_to_fix)} films to fix")
    
    if dry_run:
        print("\nSample of films that would be updated:")
        for film_id, title, old_year in films_to_fix[:10]:
            # Calculate what the new year would be
            year_min = max(1980, sim_start_year - 20)
            year_max = sim_start_year
            new_year = random.randint(year_min, year_max)
            print(f"  Film {film_id}: '{title}' - {old_year} → {new_year}")
        
        if len(films_to_fix) > 10:
            print(f"  ... and {len(films_to_fix) - 10} more")
        
        print(f"\nRun with --apply to actually update the database")
    else:
        # Fix the films
        year_min = max(1980, sim_start_year - 20)
        year_max = sim_start_year
        
        print(f"Updating films to have release years between {year_min} and {year_max}...")
        
        updates = []
        for film_id, title, old_year in films_to_fix:
            new_year = random.randint(year_min, year_max)
            updates.append((new_year, film_id))
        
        # Batch update
        cursor.executemany("""
            UPDATE film 
            SET release_year = %s 
            WHERE film_id = %s
        """, updates)
        
        conn.commit()
        
        # Verify changes
        cursor.execute("""
            SELECT 
                MIN(release_year) as min_year,
                MAX(release_year) as max_year,
                COUNT(CASE WHEN release_year > %s THEN 1 END) as future_films
            FROM film
        """, (sim_start_year,))
        
        new_min, new_max, remaining_future = cursor.fetchone()
        
        print(f"\n✅ Fixed {len(films_to_fix)} films!")
        print(f"  New release year range: {new_min} - {new_max}")
        print(f"  Remaining films with year > {sim_start_year}: {remaining_future}")
    
    cursor.close()
    conn.close()

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Fix film release years in database')
    parser.add_argument('--database', '-d', default='dvdrental_O', 
                       help='Database name (default: dvdrental_O)')
    parser.add_argument('--start-year', '-y', type=int, default=2001,
                       help='Simulation start year (default: 2001)')
    parser.add_argument('--apply', action='store_true',
                       help='Actually apply changes (default is dry-run)')
    
    args = parser.parse_args()
    
    try:
        fix_film_years(args.database, args.start_year, dry_run=not args.apply)
    except mysql.connector.Error as e:
        print(f"❌ Database error: {e}")
        sys.exit(1)
