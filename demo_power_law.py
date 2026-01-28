#!/usr/bin/env python3
"""
Test script to demonstrate power law (Zipfian) distribution for film rentals.
Shows how the distribution changes based on alpha parameter.
"""

import math
from typing import List

def calculate_zipfian_weights_demo(rental_counts: List[int], alpha: float = 1.0) -> List[float]:
    """Calculate Zipfian weights for demonstration"""
    if not rental_counts:
        return [1.0]
    
    sorted_counts = sorted(set(rental_counts), reverse=True)
    count_to_rank = {count: rank + 1 for rank, count in enumerate(sorted_counts)}
    
    weights = []
    for count in rental_counts:
        rank = count_to_rank[count]
        weight = 1.0 / ((rank + 1) ** alpha)
        weights.append(weight)
    
    total_weight = sum(weights)
    if total_weight > 0:
        normalized_weights = [w / total_weight for w in weights]
    else:
        normalized_weights = [1.0 / len(weights) for _ in weights]
    
    return normalized_weights


def demonstrate_power_law():
    """Demonstrate power law distribution with different alpha values"""
    
    print("=" * 70)
    print("POWER LAW (ZIPFIAN) DISTRIBUTION DEMONSTRATION")
    print("=" * 70)
    print()
    
    # Simulate 100 films with initial rental counts
    # New films: 0 rentals, Popular films: up to 50 rentals
    rental_counts = [0] * 70 + [i for i in range(1, 31)]
    rental_counts.sort(reverse=True)
    
    # Test different alpha values
    alphas = [0.5, 1.0, 1.5]
    
    for alpha in alphas:
        print(f"\nAlpha = {alpha}")
        print("-" * 70)
        
        weights = calculate_zipfian_weights_demo(rental_counts, alpha)
        
        # Convert to percentages
        percentages = [w * 100 for w in weights]
        
        # Group by popularity tiers
        top_1_pct = sum(percentages[:1])
        top_10_pct = sum(percentages[:10])
        top_20_pct = sum(percentages[:20])
        top_50_pct = sum(percentages[:50])
        
        print(f"  Top 1 film:     {top_1_pct:5.1f}% of rentals")
        print(f"  Top 10 films:   {top_10_pct:5.1f}% of rentals")
        print(f"  Top 20 films:   {top_20_pct:5.1f}% of rentals")
        print(f"  Top 50 films:   {top_50_pct:5.1f}% of rentals")
        print(f"  Bottom 50 films: {100 - top_50_pct:5.1f}% of rentals")
        
        # Detailed breakdown
        print(f"\n  Detailed rank distribution (top 15 films):")
        print(f"  {'Rank':<6} {'Rentals':<10} {'Weight':<8} {'%':<8}")
        print(f"  {'-'*6} {'-'*10} {'-'*8} {'-'*8}")
        
        for rank, (count, weight) in enumerate(zip(rental_counts[:15], weights[:15]), 1):
            pct = weight * 100
            print(f"  {rank:<6} {count:<10} {weight:<8.4f} {pct:<8.2f}%")
    
    print("\n" + "=" * 70)
    print("INTERPRETATION")
    print("=" * 70)
    print("""
α = 0.5 (Gentle Distribution):
  - All films get rented regularly
  - Less extreme concentration
  - Good for: Academic/teaching environments

α = 1.0 (Moderate Distribution - RECOMMENDED):
  - Classic 80/20 pattern
  - Top 20% of films get ~80% of rentals
  - Realistic for typical DVD rental business
  - Good for: Production simulations

α = 1.5 (Extreme Distribution):
  - Very few films dominate rentals
  - Most films rarely rented
  - Realistic for Netflix/streaming era
  - Good for: Advanced analytics scenarios
    """)
    
    print("\n" + "=" * 70)
    print("IMPLEMENTATION IN GENERATOR")
    print("=" * 70)
    print("""
The power law distribution is implemented in the rental selection process:

1. When a customer rents a film:
   - System looks up available inventory
   - Counts how many times each film has been rented
   - Ranks films by popularity

2. Calculates weights using Zipf's Law:
   - weight = 1 / (rank ^ alpha)
   - Popular films (low rank) get higher weights
   - Niche films (high rank) get lower weights

3. Uses weighted random selection:
   - More popular films selected more often
   - Still possible to rent any film
   - Reflects realistic rental patterns

Configuration in config.json:
  "generation": {
    "rental_distribution": {
      "enabled": true,
      "type": "power_law",
      "alpha": 1.0
    }
  }
    """)


if __name__ == '__main__':
    demonstrate_power_law()
