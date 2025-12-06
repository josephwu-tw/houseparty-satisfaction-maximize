"""
Data models for Party Optimizer.
"""
from dataclasses import dataclass, field, asdict
from typing import Dict, List
from .config import (
    MIN_INTIMACY, MAX_INTIMACY, MIN_PREFERENCE, MAX_PREFERENCE,
    DEFAULT_MAX_GUESTS, DRINK_CATEGORY, validate_weights
)


@dataclass
class Friend:
    """Friend with food preferences and intimacy level."""
    name: str
    preferences: Dict[str, int]
    intimacy: int
    dietary_restrictions: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if not MIN_INTIMACY <= self.intimacy <= MAX_INTIMACY:
            raise ValueError(f"Intimacy must be {MIN_INTIMACY}-{MAX_INTIMACY}, got {self.intimacy}")
        for food, rating in self.preferences.items():
            if not MIN_PREFERENCE <= rating <= MAX_PREFERENCE:
                raise ValueError(f"Preference must be {MIN_PREFERENCE}-{MAX_PREFERENCE}, got {rating} for {food}")
    
    def get_preference(self, food_name: str) -> int:
        return self.preferences.get(food_name, 0)
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Friend':
        return cls(**data)


@dataclass
class Food:
    """Food item with cost and category."""
    name: str
    cost: float
    category: str = "snack"
    tags: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if self.cost < 0:
            raise ValueError(f"Cost cannot be negative, got {self.cost}")
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Food':
        return cls(**data)


@dataclass
class PartyRecommendation:
    """Party planning recommendation."""
    guest_list: List[str]
    recommended_foods: List[str]
    food_costs: Dict[str, float]
    total_cost: float
    max_satisfaction: float
    total_intimacy: int
    cost_savings: float
    efficiency_score: float
    host_happiness: float
    num_guests: int = 0
    food_categories: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    def print_summary(self, rank: int = None):
        header = f"--- Recommendation #{rank} ---" if rank else "--- Recommendation ---"
        print(f"\n{header}")
        print(f"Guests: {', '.join(self.guest_list)}")
        print(f"Number of Guests: {len(self.guest_list)}")
        print(f"Total Intimacy: {self.total_intimacy}")
        print(f"Average Intimacy: {self.total_intimacy / len(self.guest_list):.1f}")
        print(f"Satisfaction: {self.max_satisfaction:.1f}")
        
        foods = [f for f in self.recommended_foods if self.food_categories.get(f) != DRINK_CATEGORY]
        drinks = [f for f in self.recommended_foods if self.food_categories.get(f) == DRINK_CATEGORY]
        
        print(f"\n📋 Menu Composition:")
        print(f"  Foods ({len(foods)}): {', '.join(foods) if foods else 'None'}")
        print(f"  Drinks ({len(drinks)}): {', '.join(drinks) if drinks else 'None'}")
        print(f"  Total Items: {len(self.recommended_foods)}")
        
        print(f"\nCost Breakdown (× {len(self.guest_list)} guests):")
        for food, unit_cost in self.food_costs.items():
            total = unit_cost * len(self.guest_list)
            cat = self.food_categories.get(food, '')
            print(f"  • {food} [{cat}]: ${unit_cost:.2f} × {len(self.guest_list)} = ${total:.2f}")
        
        print(f"\nTotal Cost: ${self.total_cost:.2f}")
        print(f"Cost Per Guest: ${self.total_cost / len(self.guest_list):.2f}")
        print(f"Savings: ${self.cost_savings:.2f}")
        print(f"Efficiency: {self.efficiency_score:.2f}")
        print(f"Host Happiness: {self.host_happiness:.2f}")
        print("-" * 50)


@dataclass
class OptimizationConfig:
    """Configuration for optimization."""
    budget: float
    min_guests: int = 1
    max_guests: int = None
    satisfaction_weight: float = 0.4
    savings_weight: float = 0.2
    intimacy_weight: float = 0.4
    
    def __post_init__(self):
        if self.max_guests is None:
            self.max_guests = DEFAULT_MAX_GUESTS
        if not validate_weights(self.satisfaction_weight, self.savings_weight, self.intimacy_weight):
            total = self.satisfaction_weight + self.savings_weight + self.intimacy_weight
            raise ValueError(f"Weights must sum to 1.0, got {total}")