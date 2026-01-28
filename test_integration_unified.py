#!/usr/bin/env python3
"""
Integration test: Verify unified film generation works end-to-end
This simulates what happens during actual simulation runs
"""

import sys
import os
import json
from datetime import date

# Setup paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'level_3_master_simulation', 'film_system'))

def test_workflow():
    """Test the complete unified film generation workflow"""
    
    print("=" * 70)
    print("INTEGRATION TEST: Unified Film Generation Workflow")
    print("=" * 70)
    
    # Step 1: Load config
    print("\n[1/4] Loading configuration...")
    try:
        with open('shared/configs/config.json', 'r') as f:
            config = json.load(f)
        
        strategy = config['master_simulation']['film_release_strategy']
        market_weekly = strategy['market_weekly_releases']
        hot_cats = strategy['hot_categories']
        
        print(f"  ✓ Market weekly releases: {market_weekly}")
        print(f"  ✓ Hot categories: {len(hot_cats)} defined")
        print(f"  ✓ Annual market films: {market_weekly * 52}")
    except Exception as e:
        print(f"  ✗ Failed to load config: {e}")
        return False
    
    # Step 2: Load templates
    print("\n[2/4] Loading unified templates...")
    try:
        from unified_film_generator import load_templates_from_files, generate_film_title
        
        templates = load_templates_from_files()
        print(f"  ✓ Loaded templates for {len(templates)} categories")
        
        category_summary = {cat: len(templates[cat].get('titles', [])) for cat in templates}
        for cat in sorted(category_summary.keys())[:8]:
            print(f"    • {cat:12s}: {category_summary[cat]:2d} titles")
        print(f"    ... and {len(category_summary) - 8} more")
    except Exception as e:
        print(f"  ✗ Failed to load templates: {e}")
        return False
    
    # Step 3: Simulate film generation
    print("\n[3/4] Simulating film generation (52 weeks)...")
    try:
        films_generated = {}
        categories_used = list(templates.keys())
        
        # Simulate market releases
        total_market = market_weekly * 52
        for week in range(52):
            weekly_count = market_weekly
            for _ in range(weekly_count):
                cat = categories_used[week % len(categories_used)]
                title, desc, rating = generate_film_title(cat, templates)
                films_generated[title] = {'category': cat, 'rating': rating}
        
        print(f"  ✓ Generated {len(films_generated)} unique market releases")
        
        # Simulate hot category purchases
        purchases = {'Action': 0, 'Comedy': 0, 'Drama': 0}
        for hot_cat in hot_cats:
            cat_name = hot_cat['category']
            weeks = hot_cat['weeks']
            per_release = hot_cat['purchase_per_release']
            count = len(weeks) * per_release
            purchases[cat_name] = count
        
        print(f"  ✓ Purchases: Action={purchases['Action']}, Comedy={purchases['Comedy']}, Drama={purchases['Drama']}")
    except Exception as e:
        print(f"  ✗ Failed during generation: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 4: Verify consistency
    print("\n[4/4] Verifying consistency...")
    try:
        # Check that all generated films have valid structure
        invalid = 0
        for title, info in films_generated.items():
            if not info.get('category') or not info.get('rating'):
                invalid += 1
        
        if invalid > 0:
            print(f"  ✗ Found {invalid} invalid films")
            return False
        
        print(f"  ✓ All {len(films_generated)} films have valid structure")
        
        # Check rating distribution
        ratings = {}
        for title, info in films_generated.items():
            rating = info['rating']
            ratings[rating] = ratings.get(rating, 0) + 1
        
        print(f"  ✓ Rating distribution: {ratings}")
        
        # Check that we have films from multiple categories
        categories_found = set(info['category'] for info in films_generated.values())
        print(f"  ✓ Used {len(categories_found)} different categories")
        
        if len(categories_found) < 10:
            print(f"  ⚠ Warning: Only {len(categories_found)} categories used (expected 16)")
        
    except Exception as e:
        print(f"  ✗ Verification failed: {e}")
        return False
    
    return True


def main():
    """Run integration test"""
    try:
        success = test_workflow()
        
        print("\n" + "=" * 70)
        if success:
            print("✓ INTEGRATION TEST PASSED")
            print("\nThe unified film generation system is working correctly!")
            print(f"Expected simulation flow:")
            print(f"  • Week 0-51: Generate {20} market films/week = 1,040 total")
            print(f"  • Select weeks: Purchase hot category films to inventory")
            print(f"  • Result: Realistic market dynamics with selective purchasing")
            return 0
        else:
            print("✗ INTEGRATION TEST FAILED")
            print("\nPlease check the errors above.")
            return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
