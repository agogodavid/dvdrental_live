#!/usr/bin/env python3
"""
Inventory Scheduler - Generate periodic inventory additions with seasonal trends

This script generates inventory addition schedules based on seasonal trends
and the duration specified in config.json. It can be called periodically
to add new inventory to the DVD rental database.
"""

import json
import logging
import random
from datetime import datetime, timedelta
from typing import List, Tuple

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config(config_file='config.json') -> dict:
    """Load configuration from JSON file"""
    with open(config_file, 'r') as f:
        return json.load(f)


def get_quarter_for_date(date: datetime.date, start_date: datetime.date) -> int:
    """Get quarter number (1-4) for a given date relative to start date"""
    # Calculate the number of quarters since start date
    days_diff = (date - start_date).days
    weeks_diff = days_diff // 7
    quarters_diff = weeks_diff // 13  # Approximately 13 weeks per quarter
    
    # Return quarter 1-4, cycling every 4 quarters
    return (quarters_diff % 4) + 1


def generate_seasonal_trends(total_weeks: int, start_date: datetime.date) -> List[Tuple[int, int, str]]:
    """
    Generate inventory additions schedule with random seasonal trends
    
    Args:
        total_weeks: Total number of weeks for the simulation
        start_date: Start date of the simulation
        
    Returns:
        List of tuples: (week_number, quantity, description)
    """
    inventory_schedule = []
    
    # Add initial inventory creation at week 0
    inventory_schedule.append((0, 0, "Initial inventory created by generator"))
    
    # Generate quarterly inventory additions
    weeks_per_quarter = 13  # Approximately 13 weeks per quarter
    current_week = weeks_per_quarter
    
    while current_week < total_weeks:
        # Determine quarter and seasonal trend
        current_date = start_date + timedelta(weeks=current_week)
        quarter = get_quarter_for_date(current_date, start_date)
        
        # Define seasonal trends for each quarter
        seasonal_trends = {
            1: {  # Q1 - Winter (January-March)
                "base_quantity": 40,
                "variance": 15,
                "description_prefix": "Q1 Winter"
            },
            2: {  # Q2 - Spring (April-June)
                "base_quantity": 35,
                "variance": 12,
                "description_prefix": "Q2 Spring"
            },
            3: {  # Q3 - Summer (July-September)
                "base_quantity": 55,
                "variance": 20,
                "description_prefix": "Q3 Summer"
            },
            4: {  # Q4 - Fall/Winter (October-December)
                "base_quantity": 50,
                "variance": 18,
                "description_prefix": "Q4 Fall/Winter"
            }
        }
        
        trend = seasonal_trends[quarter]
        
        # Generate random quantity within seasonal variance
        quantity = max(10, trend["base_quantity"] + random.randint(-trend["variance"], trend["variance"]))
        
        # Add seasonal-specific description
        seasonal_descriptions = {
            1: ["refresh", "restock", "expansion", "collection update"],
            2: ["refresh", "new arrivals", "spring collection", "seasonal update"],
            3: ["blockbuster prep", "summer expansion", "high-demand restock", "peak season prep"],
            4: ["holiday prep", "winter restock", "seasonal expansion", "year-end update"]
        }
        
        description_suffix = random.choice(seasonal_descriptions[quarter])
        description = f"{trend['description_prefix']} - {description_suffix}"
        
        inventory_schedule.append((current_week, quantity, description))
        
        # Move to next quarter
        current_week += weeks_per_quarter
    
    # Sort by week number
    inventory_schedule.sort(key=lambda x: x[0])
    
    return inventory_schedule


def get_inventory_additions_for_week(week_num: int, total_weeks: int, start_date: datetime.date) -> Tuple[bool, int, str]:
    """
    Check if inventory should be added for a specific week
    
    Args:
        week_num: Week number to check
        total_weeks: Total weeks in simulation
        start_date: Start date of simulation
        
    Returns:
        Tuple: (should_add, quantity, description)
    """
    schedule = generate_seasonal_trends(total_weeks, start_date)
    
    for week, qty, desc in schedule:
        if week == week_num:
            return True, qty, desc
    
    return False, 0, ""


def display_inventory_schedule(total_weeks: int, start_date: datetime.date):
    """Display the generated inventory schedule"""
    schedule = generate_seasonal_trends(total_weeks, start_date)
    
    logger.info("Generated Inventory Addition Schedule:")
    logger.info("=" * 60)
    
    for week, qty, desc in schedule:
        date = start_date + timedelta(weeks=week)
        logger.info(f"  Week {week:3d} ({date}): +{qty:3d} items - {desc}")
    
    logger.info("=" * 60)


def main():
    """Main function to generate and display inventory schedule"""
    print("\n")
    logger.info("╔" + "═" * 58 + "╗")
    logger.info("║" + " INVENTORY SCHEDULER - Seasonal Trends Generator ".center(58) + "║")
    logger.info("╚" + "═" * 58 + "╝")
    
    try:
        # Load configuration
        config = load_config()
        master_config = config.get('master_simulation', {})
        total_weeks = master_config.get('total_weeks', 156)
        start_date_str = master_config.get('start_date', '2001-10-01')
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        
        logger.info(f"Simulation Duration: {total_weeks} weeks")
        logger.info(f"Start Date: {start_date}")
        end_date = start_date + timedelta(weeks=total_weeks)
        logger.info(f"End Date: {end_date}")
        
        # Generate and display schedule
        display_inventory_schedule(total_weeks, start_date)
        
        logger.info("\nSchedule generated successfully!")
        logger.info("This schedule can be used by master_simulation.py or called independently.")
        
    except Exception as e:
        logger.error(f"Failed to generate inventory schedule: {e}")
        raise


if __name__ == '__main__':
    main()