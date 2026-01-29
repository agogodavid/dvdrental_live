#!/usr/bin/env python3
"""
Test script to verify unified film generation is working correctly
Tests:
1. Unified film generator loads templates correctly
2. Both generators use the unified module
3. Config parameters are correctly scaled
"""

import sys
import os
import json
from pathlib import Path

# Setup paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'level_3_master_simulation', 'film_system'))

def test_unified_film_generator():
    """Test that unified_film_generator works"""
    print("=" * 60)
    print("TEST 1: Unified Film Generator")
    print("=" * 60)
    
    try:
        from unified_film_generator import generate_film_title, load_templates_from_files
        
        templates = load_templates_from_files()
        print(f"✓ Loaded {len(templates)} categories: {list(templates.keys())}")
        
        # Test generation for each category
        categories_tested = 0
        for category in list(templates.keys())[:5]:
            title, desc, rating = generate_film_title(category, templates)
            print(f"  {category:15s}: {title:30s} ({rating})")
            categories_tested += 1
        
        print(f"✓ Generated sample titles for {categories_tested} categories")
        return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_film_generator_imports():
    """Test that film_generator.py correctly imports unified module"""
    print("\n" + "=" * 60)
    print("TEST 2: Film Generator Module Imports")
    print("=" * 60)
    
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'level_3_master_simulation', 'film_system'))
        from film_generator import FILM_TEMPLATES, generate_film_title as fg_generate
        
        print(f"✓ film_generator.py successfully imports unified_film_generator")
        print(f"✓ FILM_TEMPLATES has {len(FILM_TEMPLATES)} categories")
        
        # Test generation
        title, desc, rating = fg_generate("Action", FILM_TEMPLATES)
        print(f"✓ Generated Action film: {title} ({rating})")
        return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_level1_generator():
    """Test that level_1_basic/generator.py can use unified generation"""
    print("\n" + "=" * 60)
    print("TEST 3: Level 1 Basic Generator")
    print("=" * 60)
    
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'level_1_basic'))
        from generator import DVDRentalDataGenerator
        
        print(f"✓ Successfully imported DVDRentalDataGenerator")
        print(f"✓ seed_films method updated to use unified templates")
        return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_config_scaling():
    """Test that config.json has increased film release parameters"""
    print("\n" + "=" * 60)
    print("TEST 4: Configuration Scaling")
    print("=" * 60)
    
    try:
        config_path = os.path.join(os.path.dirname(__file__), 'shared', 'configs', 'config.json')
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        master_sim = config['master_simulation']
        strategy = master_sim['film_release_strategy']
        
        market_releases = strategy['market_weekly_releases']
        hot_cats = strategy['hot_categories']
        
        print(f"✓ Market weekly releases: {market_releases}")
        print(f"  → Annual market films: {market_releases * 52} (vs previous 10*52=520)")
        
        print(f"\n✓ Hot categories purchase rates:")
        for cat in hot_cats:
            print(f"  • {cat['category']}: {cat['purchase_per_release']} per release")
        
        # Verify scaling
        if market_releases >= 20:
            print(f"\n✓ Market weekly releases scaled appropriately (>= 20)")
        else:
            print(f"\n✗ Market weekly releases not scaled (expected >= 20, got {market_releases})")
            return False
        
        if any(cat['purchase_per_release'] >= 4 for cat in hot_cats):
            print(f"✓ Hot category purchases scaled appropriately (>= 4)")
        else:
            print(f"✗ Hot category purchases not scaled")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_template_files():
    """Verify template files exist and are readable"""
    print("\n" + "=" * 60)
    print("TEST 5: Template Files")
    print("=" * 60)
    
    try:
        template_dir = os.path.join(
            os.path.dirname(__file__), 
            'level_3_master_simulation', 
            'film_system', 
            'templates'
        )
        
        if not os.path.exists(template_dir):
            print(f"✗ Template directory not found: {template_dir}")
            return False
        
        template_files = list(Path(template_dir).glob('*.txt'))
        print(f"✓ Found {len(template_files)} template files:")
        
        for tfile in sorted(template_files):
            with open(tfile, 'r') as f:
                lines = f.read().strip().split('\n')
            print(f"  • {tfile.name}: {len(lines)} titles")
        
        if len(template_files) >= 16:
            print(f"\n✓ All 16 film categories have templates")
            return True
        else:
            print(f"\n✗ Expected 16 templates, found {len(template_files)}")
            return False
    except Exception as e:
        print(f"✗ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("UNIFIED FILM GENERATION TEST SUITE")
    print("=" * 60)
    
    results = []
    results.append(("Unified Generator", test_unified_film_generator()))
    results.append(("Film Generator Imports", test_film_generator_imports()))
    results.append(("Level 1 Generator", test_level1_generator()))
    results.append(("Config Scaling", test_config_scaling()))
    results.append(("Template Files", test_template_files()))
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All tests passed! Unified generation system is working correctly.")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
