"""
Data models for Party Optimizer.
"""
from dataclasses import dataclass, field, asdict
from typing import Dict, List
from config import MIN_INTIMACY, MAX_INTIMACY, MIN_PREFERENCE, MAX_PREFERENCE


@dataclass
class Friend:
    """Friend with food preferences and intimacy level."""
    name: str
    preferences: Dict[str, int]  # {food_name: rating 1-5}
    intimacy: int  # 1-10
    dietary_restrictions: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate data."""
        if not MIN_INTIMACY <= self.intimacy <= MAX_INTIMACY:
            raise ValueError(f"Intimacy must be {MIN_INTIMACY}-{MAX_INTIMACY}, got {self.intimacy}")
        
        for food, rating in self.preferences.items():
            if not MIN_PREFERENCE <= rating <= MAX_PREFERENCE:
                raise ValueError(f"Preference must be {MIN_PREFERENCE}-{MAX_PREFERENCE}, got {rating} for {food}")
    
    def get_preference(self, food_name: str) -> int:
        """Get preference rating for a food."""
        return self.preferences.get(food_name, 0)
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Friend':
        """Create Friend from dictionary."""
        return cls(**data)


@dataclass
class Food:
    """Food item with cost and category."""
    name: str
    cost: float
    category: str = "snack"
    tags: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate data."""
        if self.cost < 0:
            raise ValueError(f"Cost cannot be negative, got {self.cost}")
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Food':
        """Create Food from dictionary."""
        return cls(**data)


@dataclass
class PartyRecommendation:
    """Party planning recommendation with menu composition."""
    guest_list: List[str]
    recommended_foods: List[str]
    food_costs: Dict[str, float]  # Unit cost per food
    total_cost: float  # Total cost (includes per-person multiplication)
    max_satisfaction: float
    total_intimacy: int
    cost_savings: float
    efficiency_score: float
    host_happiness: float
    num_guests: int = 0  # Number of guests
    food_categories: Dict[str, str] = field(default_factory=dict)  # Food -> category
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)
    
    def print_summary(self, rank: int = None):
        """Print formatted summary with menu composition and cost breakdown."""
        from config import DRINK_CATEGORY
        
        header = f"--- Recommendation #{rank} ---" if rank else "--- Recommendation ---"
        print(f"\n{header}")
        print(f"Guests: {', '.join(self.guest_list)}")
        print(f"Number of Guests: {len(self.guest_list)}")
        print(f"Total Intimacy: {self.total_intimacy}")
        print(f"Satisfaction: {self.max_satisfaction:.1f}")
        
        # Separate foods and drinks based on category
        foods = []
        drinks = []
        
        for food_name in self.recommended_foods:
            category = self.food_categories.get(food_name, 'unknown')
            if category == DRINK_CATEGORY:
                drinks.append(food_name)
            else:
                foods.append(food_name)
        
        print(f"\n📋 Menu Composition:")
        print(f"  Foods ({len(foods)}): {', '.join(foods) if foods else 'None'}")
        print(f"  Drinks ({len(drinks)}): {', '.join(drinks) if drinks else 'None'}")
        
        print(f"\nCost Breakdown (× {len(self.guest_list)} guests):")
        for food, unit_cost in self.food_costs.items():
            total_food_cost = unit_cost * len(self.guest_list)
            category = self.food_categories.get(food, '')
            category_tag = f"[{category}]" if category else ""
            print(f"  • {food} {category_tag}: ${unit_cost:.2f} × {len(self.guest_list)} = ${total_food_cost:.2f}")
        
        print(f"\nTotal Cost: ${self.total_cost:.2f}")
        print(f"Cost Per Guest: ${self.total_cost / len(self.guest_list):.2f}")
        print(f"Savings: ${self.cost_savings:.2f}")
        print(f"Efficiency: {self.efficiency_score:.2f} (satisfaction per $)")
        print(f"Host Happiness: {self.host_happiness:.2f}")
        print("-" * 50)


@dataclass
class OptimizationConfig:
    """Configuration for optimization algorithm."""
    budget: float
    min_guests: int = 1
    max_guests: int = None
    satisfaction_weight: float = 0.5
    savings_weight: float = 0.3
    intimacy_weight: float = 0.2
    
    def __post_init__(self):
        """Validate weights sum to 1."""
        from config import validate_weights
        total = self.satisfaction_weight + self.savings_weight + self.intimacy_weight
        if not validate_weights(self.satisfaction_weight, self.savings_weight, self.intimacy_weight):
            raise ValueError(f"Weights must sum to 1.0, got {total}")