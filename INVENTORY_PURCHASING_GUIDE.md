# Inventory Purchasing Guide

## Overview

This document explains the inventory purchasing logic in the DVD rental simulation system, including the configurable purchasing strategies and how they relate to film releases.

## Current Inventory Purchase Logic

### Basic Flow

1. **Film Releases**: New films are added to the catalog via the film generator
2. **Inventory Purchasing**: The inventory manager purchases copies of films to add to store inventory
3. **Staff Linking**: Each purchase is linked to a staff member for tracking purchasing decisions
4. **Seasonal Considerations**: Different strategies consider seasonal demand patterns

### Key Tables

- `film_releases`: Tracks when films are released to the market
- `inventory`: Stores physical copies in stores
- `inventory_purchases`: Links inventory items to purchasing decisions and staff

## Configurable Purchase Strategies

### 1. Aggressive Strategy

**Configuration:**
```json
{
  "strategy": "aggressive",
  "inventory_per_film": [8, 12],
  "diversification_factor": 1.0
}
```

**Characteristics:**
- **High Growth**: Purchases 8-12 copies per film
- **Broad Diversification**: Spreads purchases across many different genres
- **Recent Release Focus**: 70% chance to purchase recently released films
- **More Films**: Buys more different films (quantity ÷ 6)

**Use Case:** Rapid expansion, capturing market share across all genres

### 2. Stable Strategy

**Configuration:**
```json
{
  "strategy": "stable", 
  "inventory_per_film": [5, 8],
  "diversification_factor": 0.8
}
```

**Characteristics:**
- **Moderate Growth**: Purchases 5-8 copies per film
- **Balanced Approach**: Moderate genre diversification
- **Conservative Film Count**: Buys moderate number of different films (quantity ÷ 8)
- **Steady Growth**: Predictable, sustainable inventory growth

**Use Case:** Steady business growth with controlled risk

### 3. Seasonal Strategy

**Configuration:**
```json
{
  "strategy": "seasonal",
  "inventory_per_film": [4, 7], 
  "diversification_factor": 0.3,
  "seasonal_preferences": {
    "Q1": ["Drama", "Romance", "Comedy"],
    "Q2": ["Action", "Sci-Fi", "Adventure"],
    "Q3": ["Horror", "Thriller", "Action"],
    "Q4": ["Family", "Animation", "Comedy"]
  }
}
```

**Characteristics:**
- **Seasonal Focus**: Prioritizes genres appropriate for the current season
- **Targeted Purchasing**: 70% chance to buy recent releases, genre-weighted selection
- **Lower Per-Film Quantity**: 4-7 copies per film
- **Fewer Film Types**: Buys fewer different films (quantity ÷ 10)

**Seasonal Genre Preferences:**
- **Q1 (Jan-Mar)**: Drama, Romance, Comedy - Post-holiday introspective content
- **Q2 (Apr-Jun)**: Action, Sci-Fi, Adventure - Summer blockbuster season
- **Q3 (Jul-Sep)**: Horror, Thriller, Action - Late summer scares and action
- **Q4 (Oct-Dec)**: Family, Animation, Comedy - Holiday family entertainment

**Use Case:** Aligning inventory with seasonal customer demand patterns

## Film Release and Inventory Purchase Relationship

### Current Logic

1. **Film Release**: Films are released with a specific date (e.g., 2023-02-15)
2. **Inventory Purchase**: Inventory is purchased on the same date or shortly after
3. **Recent Release Priority**: 70% chance to purchase films released within the last 30 days
4. **Genre Weighting**: Strategy determines which genres get priority

### Matching Logic

The system creates a logical connection between film releases and inventory purchases:

- **Recent Release Matching**: Films released within 30 days get 70% purchase priority
- **Seasonal Matching**: Seasonal strategy matches purchases to appropriate genres for the time of year
- **Strategy-Based Matching**: Each strategy has different criteria for selecting which films to purchase

### Example Flow

```
Week 10: Action films released (Q1 2023)
├── Aggressive Strategy: Buys 10 copies of 5 different action films
├── Stable Strategy: Buys 6 copies of 3 different action films  
└── Seasonal Strategy: Buys 5 copies of 2 action films (less Q1 focus)

Week 20: Comedy films released (Q2 2023)  
├── Aggressive Strategy: Diversifies to include comedies
├── Stable Strategy: Maintains balanced approach
└── Seasonal Strategy: Prioritizes comedies (Q2 preference)
```

## Configuration Examples

### Aggressive Expansion
```json
{
  "inventory_purchasing": {
    "strategy": "aggressive",
    "aggressive": {
      "description": "Rapid market expansion across all genres",
      "inventory_per_film": [10, 15],
      "diversification_factor": 1.2
    }
  }
}
```

### Conservative Growth
```json
{
  "inventory_purchasing": {
    "strategy": "stable",
    "stable": {
      "description": "Conservative, steady growth",
      "inventory_per_film": [3, 6],
      "diversification_factor": 0.5
    }
  }
}
```

### Holiday Focus
```json
{
  "inventory_purchasing": {
    "strategy": "seasonal",
    "seasonal": {
      "description": "Holiday-focused inventory",
      "inventory_per_film": [6, 10],
      "diversification_factor": 0.1,
      "seasonal_preferences": {
        "Q4": ["Family", "Animation", "Comedy", "Romance"]
      }
    }
  }
}
```

## Benefits of Configurable Strategies

1. **Business Flexibility**: Adapt purchasing to business goals
2. **Seasonal Optimization**: Align inventory with customer demand
3. **Risk Management**: Control exposure through diversification
4. **Data-Driven Decisions**: Track which strategies work best
5. **Staff Accountability**: Link purchases to specific staff members

## Implementation Notes

- All strategies maintain the same database schema
- Strategies can be changed dynamically without data migration
- Staff assignments are randomized but trackable
- Film selection considers both recent releases and genre preferences
- Inventory quantities are distributed across all available stores