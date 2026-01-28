"""
Inventory Scheduler Module - Generates seasonal inventory purchase schedules
"""

from datetime import datetime, date, timedelta
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)


def generate_seasonal_trends(total_weeks: int, start_date: date) -> List[Tuple[int, int, str]]:
    """Generate seasonal inventory purchase schedule based on business lifecycle
    
    Returns list of (week_number, quantity, description) tuples
    """
    schedule = []
    
    # Business lifecycle phases
    # Growth phase (first 2 years): Aggressive inventory growth
    if total_weeks > 0:
        for week in range(13, min(104, total_weeks + 1), 13):  # Every quarter
            quarter = (week // 13) % 4 + 1
            year = start_date.year + (week // 52)
            schedule.append((week, 50, f"Q{quarter} {year} - Aggressive growth"))
    
    # Plateau phase (years 3-6): Moderate growth  
    if total_weeks > 104:
        for week in range(104 + 16, min(312, total_weeks + 1), 16):  # Every 4 months
            quarter = ((week - 104) // 16) % 4 + 1
            year = start_date.year + (week // 52)
            schedule.append((week, 30, f"Q{quarter} {year} - Moderate growth"))
    
    # Decline phase (years 7-8): Minimal growth
    if total_weeks > 312:
        for week in range(312 + 20, min(416, total_weeks + 1), 20):  # Every 5 months
            quarter = ((week - 312) // 20) % 4 + 1
            year = start_date.year + (week // 52)
            schedule.append((week, 15, f"Q{quarter} {year} - Minimal growth"))
    
    # Reactivation phase (years 9-10): Strategic growth
    if total_weeks > 416:
        for week in range(416 + 12, min(total_weeks + 1, 521), 12):  # Every quarter
            quarter = ((week - 416) // 12) % 4 + 1
            year = start_date.year + (week // 52)
            schedule.append((week, 25, f"Q{quarter} {year} - Strategic growth"))
    
    # Initial inventory at week 0 (already handled by generator)
    if len(schedule) == 0 or schedule[0][0] != 0:
        schedule.insert(0, (0, 0, "Initial inventory created by generator"))
    
    return sorted(schedule, key=lambda x: x[0])


def get_inventory_additions_for_week(week_num: int, total_weeks: int, start_date: date) -> Tuple[bool, int, str]:
    """Get inventory additions for a specific week
    
    Returns: (should_add, quantity, description)
    """
    schedule = generate_seasonal_trends(total_weeks, start_date)
    
    for week, qty, desc in schedule:
        if week == week_num:
            return qty > 0, qty, desc
    
    return False, 0, ""
