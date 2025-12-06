"""
Utility helper functions.
"""
import json
from typing import List, Tuple
from core.models import Friend, Food
from core.config import (
    DEFAULT_FOODS, DEFAULT_FOOD_PRICES, DEFAULT_FOOD_CATEGORIES,
    MIN_INTIMACY, MAX_INTIMACY, MIN_BUDGET, DISPLAY_WIDTH
)


def initialize_sample_data() -> Tuple[List[Friend], List[Food]]:
    """Create sample data."""
    friends = [
        Friend("Tom", {"Fried Chicken": 5, "Chips": 3, "Sandwich": 4, "Cookies": 2, 
                      "Candy": 1, "Soda": 5, "Juice": 3, "Tea": 1}, 7),
        Friend("Ariel", {"Fried Chicken": 3, "Chips": 2, "Sandwich": 5, "Cookies": 3, 
                        "Candy": 4, "Soda": 2, "Juice": 3, "Tea": 4}, 6),
        Friend("Bob", {"Fried Chicken": 4, "Chips": 5, "Sandwich": 3, "Cookies": 4, 
                      "Candy": 3, "Soda": 4, "Juice": 2, "Tea": 2}, 8),
        Friend("Lisa", {"Fried Chicken": 2, "Chips": 4, "Sandwich": 4, "Cookies": 5, 
                       "Candy": 5, "Soda": 3, "Juice": 4, "Tea": 3}, 5, ["vegetarian"]),
        Friend("Mike", {"Fried Chicken": 5, "Chips": 5, "Sandwich": 4, "Cookies": 3, 
                       "Candy": 2, "Soda": 5, "Juice": 4, "Tea": 2}, 9)
    ]
    
    foods = [
        Food(name, DEFAULT_FOOD_PRICES[name], DEFAULT_FOOD_CATEGORIES[name],
             [] if name in ["Fried Chicken", "Sandwich"] else ["vegetarian"])
        for name in DEFAULT_FOODS
    ]
    
    return friends, foods


def print_header(text: str, width: int = DISPLAY_WIDTH):
    """Print formatted header."""
    print(f"\n{'=' * width}")
    print(f"{text.center(width)}")
    print(f"{'=' * width}\n")


def print_section(text: str):
    """Print section divider."""
    print(f"\n{text}")
    print("-" * len(text))


def wait_for_key(message: str = "\n(press Enter to continue...)"):
    """Wait for user input."""
    input(message)


def validate_budget(budget: float) -> bool:
    """Validate budget value."""
    return budget >= MIN_BUDGET


def validate_intimacy(intimacy: int) -> bool:
    """Validate intimacy level."""
    return MIN_INTIMACY <= intimacy <= MAX_INTIMACY


def get_user_input(prompt: str, input_type=str, validator=None):
    """Get validated user input."""
    while True:
        try:
            value = input(prompt)
            converted = input_type(value)
            if validator and not validator(converted):
                print("Invalid input. Please try again.")
                continue
            return converted
        except ValueError:
            print(f"Invalid input. Expected {input_type.__name__}.")
        except KeyboardInterrupt:
            print("\nCancelled.")
            return None


def display_summary_table(recommendations: List, max_rows: int = 10):
    """Display recommendations summary table."""
    if not recommendations:
        print("No recommendations available.")
        return
    
    print(f"\n{'#':<4} {'Guests':<30} {'Items':<8} {'Savings':<10} {'Satisfaction':<15} {'Avg Intimacy':<15} {'Happiness':<12}")
    print("-" * 100)
    
    for i, rec in enumerate(recommendations[:max_rows], 1):
        # Shorten guest names
        guests = []
        for name in rec.guest_list:
            parts = name.split()
            short = f"{parts[0]} {parts[1][0]}." if len(parts) >= 2 else parts[0]
            guests.append(short)
        
        guests_str = ', '.join(guests)
        if len(guests_str) > 28:
            guests_str = guests_str[:25] + "..."
        
        items_str = f"{len(rec.recommended_foods)} items"
        avg_intimacy = rec.total_intimacy / len(rec.guest_list) if rec.guest_list else 0
        
        print(f"{i:<4} {guests_str:<30} {items_str:<8} "
              f"${rec.cost_savings:<9.2f} {rec.max_satisfaction:<15.1f} "
              f"{avg_intimacy:<15.1f} {rec.host_happiness:<12.2f}")


def export_recommendations_to_json(recommendations: List, filename: str):
    """Export recommendations to JSON file."""
    data = {
        'total': len(recommendations),
        'recommendations': [r.to_dict() for r in recommendations]
    }
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\n✓ Exported to {filename}")