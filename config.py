"""
Centralized configuration for Party Optimizer.
All constants and settings in one place.
"""
import os
from pathlib import Path

# Application Info
APP_NAME = "House Party Optimizer"
APP_VERSION = "2.0.0"
AUTHORS = ["Chen-Yen Wu", "Jinghong Yang", "Yuting Wan"]

# Directories
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
EXPORT_DIR = BASE_DIR / "exports"

# Create directories
DATA_DIR.mkdir(exist_ok=True)
EXPORT_DIR.mkdir(exist_ok=True)

# File Names
FRIENDS_FILE = "friends.json"
FOODS_FILE = "foods.json"
RECOMMENDATIONS_FILE = "recommendations.json"

# Optimization Defaults
DEFAULT_SATISFACTION_WEIGHT = 0.5
DEFAULT_SAVINGS_WEIGHT = 0.3
DEFAULT_INTIMACY_WEIGHT = 0.2
DEFAULT_TOP_N_RECOMMENDATIONS = 10

# Menu Composition Constraints
REQUIRED_FOOD_ITEMS = 3  # Must select 3 food items (main/snack/dessert)
REQUIRED_DRINK_ITEMS = 2  # Must select 2 drink items

# Food category definitions
FOOD_CATEGORIES = ['main', 'snack', 'dessert']  # Count towards food items
DRINK_CATEGORY = 'drink'  # Count towards drink items

# Validation Constraints
MIN_INTIMACY = 1
MAX_INTIMACY = 10
MIN_PREFERENCE = 1
MAX_PREFERENCE = 5
MIN_BUDGET = 0.01
MAX_BUDGET = 10000.0
MIN_FRIENDS_GENERATE = 1
MAX_FRIENDS_GENERATE = 500

# Display Settings
DISPLAY_WIDTH = 70
TABLE_WIDTH = 90
MAX_NAME_DISPLAY_LENGTH = 25
PROGRESS_UPDATE_FREQUENCY = 50

# Sample Names for Random Generation
FIRST_NAMES = [
    "Alex", "Sam", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Avery",
    "Quinn", "Charlie", "Skylar", "Dakota", "Emma", "Liam", "Olivia", "Noah",
    "Ava", "Ethan", "Sophia", "Mason", "Isabella", "William", "Mia", "James",
    "Charlotte", "Benjamin", "Amelia", "Lucas", "Harper", "Henry", "Evelyn",
    "Alexander", "Abigail", "Jack", "Emily", "Sebastian", "Elizabeth", "Michael",
    "Sofia", "Daniel", "Ella", "Matthew", "Madison", "David", "Scarlett", "Joseph",
    "Victoria", "Carter", "Aria", "Owen", "Grace", "Wyatt", "Chloe", "John",
    "Camila", "Leo", "Penelope", "Jackson", "Riley", "Aiden", "Layla"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
    "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
    "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark",
    "Ramirez", "Lewis", "Robinson", "Walker", "Young", "Allen", "King",
    "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores", "Green",
    "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell"
]

# Dietary Restrictions (with probabilities, must sum to 1.0)
DIETARY_OPTIONS = [
    ('', 0.60),
    ('vegetarian', 0.15),
    ('vegan', 0.08),
    ('gluten-free', 0.07),
    ('dairy-free', 0.04),
    ('nut-free', 0.03),
    ('vegetarian;gluten-free', 0.02),
    ('vegan;gluten-free', 0.01),
]

# Default Foods
DEFAULT_FOODS = [
    "Fried Chicken", "Chips", "Sandwich", "Cookies",
    "Candy", "Soda", "Juice", "Tea"
]

DEFAULT_FOOD_PRICES = {
    "Fried Chicken": 5.70, "Chips": 2.99, "Sandwich": 4.00, "Cookies": 1.99,
    "Candy": 0.99, "Soda": 2.49, "Juice": 2.79, "Tea": 1.89
}

DEFAULT_FOOD_CATEGORIES = {
    "Fried Chicken": "main", "Chips": "snack", "Sandwich": "main",
    "Cookies": "dessert", "Candy": "dessert", "Soda": "drink",
    "Juice": "drink", "Tea": "drink"
}

# Generation Settings
DEFAULT_INTIMACY_MEAN = 6.0
DEFAULT_INTIMACY_STD = 2.0
DIVERSITY_LEVELS = ['low', 'medium', 'high', 'realistic']
INTIMACY_DISTRIBUTIONS = ['normal', 'uniform', 'bimodal']

# Performance Settings
NUMPY_DTYPE_DP = 'float32'
CSV_ENCODING = 'utf-8'

# Visualization Settings
PLOT_DPI = 300
HEATMAP_COLORMAP = 'YlOrRd'

# Error Messages
ERROR_MESSAGES = {
    'invalid_intimacy': f"Intimacy must be between {MIN_INTIMACY} and {MAX_INTIMACY}",
    'invalid_preference': f"Preference must be between {MIN_PREFERENCE} and {MAX_PREFERENCE}",
    'invalid_budget': f"Budget must be between ${MIN_BUDGET} and ${MAX_BUDGET}",
    'no_friends': "No friends available. Please add friends first.",
    'no_foods': "No food items available. Please add food items first.",
    'file_not_found': "File not found: {filename}",
    'invalid_csv': "Invalid CSV format: {message}",
    'duplicate_name': "A friend with name '{name}' already exists",
}

# Success Messages
SUCCESS_MESSAGES = {
    'friend_added': "✓ Friend '{name}' added successfully!",
    'friend_updated': "✓ Friend '{name}' updated successfully!",
    'friend_deleted': "✓ Friend '{name}' deleted successfully!",
    'food_added': "✓ Food item '{name}' added successfully!",
    'csv_imported': "✓ Successfully imported {count} friends",
    'csv_exported': "✓ Exported {count} friends to {filename}",
}

# Helper Functions
def get_error_message(key: str, **kwargs) -> str:
    """Get formatted error message."""
    return ERROR_MESSAGES.get(key, "An error occurred").format(**kwargs)

def get_success_message(key: str, **kwargs) -> str:
    """Get formatted success message."""
    return SUCCESS_MESSAGES.get(key, "Operation successful").format(**kwargs)

def validate_weights(satisfaction: float, savings: float, intimacy: float) -> bool:
    """Validate optimization weights sum to 1.0."""
    total = satisfaction + savings + intimacy
    return 0.99 <= total <= 1.01

# Configuration Validation
def validate_config():
    """Validate configuration on import."""
    if not validate_weights(DEFAULT_SATISFACTION_WEIGHT, DEFAULT_SAVINGS_WEIGHT, DEFAULT_INTIMACY_WEIGHT):
        raise ValueError("Default optimization weights must sum to 1.0")
    
    total_prob = sum(prob for _, prob in DIETARY_OPTIONS)
    if not 0.99 <= total_prob <= 1.01:
        raise ValueError("Dietary restriction probabilities must sum to 1.0")

validate_config()