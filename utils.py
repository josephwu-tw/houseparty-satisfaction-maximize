"""
Utility functions for Party Optimizer.
"""
from typing import List, Tuple
from models import Friend, Food
from config import (
    DEFAULT_FOODS, DEFAULT_FOOD_PRICES, DEFAULT_FOOD_CATEGORIES,
    MIN_INTIMACY, MAX_INTIMACY, MIN_PREFERENCE, MAX_PREFERENCE,
    MIN_BUDGET, DISPLAY_WIDTH, MAX_NAME_DISPLAY_LENGTH, TABLE_WIDTH,
    get_error_message, get_success_message
)


def initialize_sample_data() -> Tuple[List[Friend], List[Food]]:
    """Create sample data using config defaults."""
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
    print(f"\n{'='*width}")
    print(f"{text.center(width)}")
    print(f"{'='*width}\n")


def print_section(text: str):
    """Print section divider."""
    print(f"\n{text}")
    print("-" * len(text))


def validate_budget(budget: float) -> bool:
    """Validate budget."""
    return budget >= MIN_BUDGET


def validate_intimacy(intimacy: int) -> bool:
    """Validate intimacy level."""
    return MIN_INTIMACY <= intimacy <= MAX_INTIMACY


def validate_preference(preference: int) -> bool:
    """Validate food preference."""
    return MIN_PREFERENCE <= preference <= MAX_PREFERENCE


def get_user_input(prompt: str, input_type=str, validator=None):
    """Get validated user input."""
    while True:
        try:
            value = input(prompt)
            converted_value = input_type(value)
            
            if validator and not validator(converted_value):
                print("Invalid input. Please try again.")
                continue
                
            return converted_value
        except ValueError:
            print(f"Invalid input type. Expected {input_type.__name__}.")
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
            return None


def display_summary_table(recommendations: List, max_rows: int = 10):
    """Display recommendations table."""
    if not recommendations:
        print("No recommendations available.")
        return
    
    print(f"\n{'#':<4} {'Guests':<25} {'Foods':<15} {'Cost':<10} {'Satisfaction':<15} {'Happiness':<12}")
    print("-" * TABLE_WIDTH)
    
    for i, rec in enumerate(recommendations[:max_rows], 1):
        guests = ', '.join(rec.guest_list)
        if len(guests) > MAX_NAME_DISPLAY_LENGTH:
            guests = guests[:MAX_NAME_DISPLAY_LENGTH-3] + "..."
        
        foods_count = f"{len(rec.recommended_foods)} items"
        print(f"{i:<4} {guests:<25} {foods_count:<15} "
              f"${rec.total_cost:<9.2f} {rec.max_satisfaction:<15.1f} {rec.host_happiness:<12.2f}")


def export_recommendations_to_json(recommendations: List, filename: str = "recommendations.json"):
    """Export recommendations to JSON."""
    import json
    
    data = {
        'total_recommendations': len(recommendations),
        'recommendations': [rec.to_dict() for rec in recommendations]
    }
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\n✓ Recommendations exported to {filename}")

def wait_for_key(message: str = "\n(press Enter to continue...)"):
    """Wait for user to press Enter."""
    input(message)