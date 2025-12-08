"""
Optimization engine for party planning.
"""
import numpy as np
from typing import List, Tuple, Dict
from itertools import combinations
from .models import Friend, Food, PartyRecommendation, OptimizationConfig
from .config import (
    MIN_FOOD_ITEMS, MAX_FOOD_ITEMS, MIN_DRINK_ITEMS, MAX_DRINK_ITEMS,
    FOOD_CATEGORIES, DRINK_CATEGORY
)


class PartyOptimizer:
    """Party optimizer with menu constraints (1-3 foods + 1-2 drinks)."""
    
    def __init__(self, friends: List[Friend], foods: List[Food]):
        self.friends = friends
        self.foods = foods
        self.food_items = [f for f in foods if f.category in FOOD_CATEGORIES]
        self.drink_items = [f for f in foods if f.category == DRINK_CATEGORY]
    
    def calculate_menu_satisfaction(self, menu: List[Food], guests: List[Friend]) -> float:
        """Calculate total guest satisfaction (sum of preferences)."""
        return sum(guest.get_preference(item.name) for item in menu for guest in guests)
    
    def find_best_menu(self, guests: List[Friend], budget: float) -> Tuple[float, List[Food], float]:
        """Find best menu within budget satisfying constraints."""
        if not self.food_items or not self.drink_items or not guests or budget <= 0:
            return 0.0, [], 0.0
        
        if len(self.food_items) < MIN_FOOD_ITEMS or len(self.drink_items) < MIN_DRINK_ITEMS:
            return 0.0, [], 0.0
        
        num_guests = len(guests)
        best_satisfaction, best_menu, best_cost = 0.0, [], 0.0
        
        for num_foods in range(MIN_FOOD_ITEMS, min(MAX_FOOD_ITEMS, len(self.food_items)) + 1):
            for food_combo in combinations(self.food_items, num_foods):
                for num_drinks in range(MIN_DRINK_ITEMS, min(MAX_DRINK_ITEMS, len(self.drink_items)) + 1):
                    for drink_combo in combinations(self.drink_items, num_drinks):
                        menu = list(food_combo) + list(drink_combo)
                        total_cost = sum(item.cost for item in menu) * num_guests
                        
                        if total_cost <= budget:
                            satisfaction = self.calculate_menu_satisfaction(menu, guests)
                            if satisfaction > best_satisfaction:
                                best_satisfaction, best_menu, best_cost = satisfaction, menu, total_cost
        
        return best_satisfaction, best_menu, best_cost
    
    def calculate_happiness(self, satisfaction: float, savings: float, intimacy: int,
                           num_guests: int, num_items: int, budget: float, config: OptimizationConfig) -> float:
        """Calculate host happiness score."""
        avg_satisfaction = satisfaction / (num_guests * num_items) if (num_guests * num_items) > 0 else 0
        avg_intimacy = intimacy / num_guests if num_guests > 0 else 0
        savings_ratio = savings / budget if budget > 0 else 0
        
        return (config.satisfaction_weight * avg_satisfaction +
                config.savings_weight * savings_ratio +
                config.intimacy_weight * avg_intimacy)
    
    def optimize(self, config: OptimizationConfig) -> List[PartyRecommendation]:
        """Generate and evaluate all guest combinations."""
        max_guests = min(config.max_guests or len(self.friends), len(self.friends))
        min_guests = max(1, config.min_guests)
        
        print(f"  [Optimizer] Searching guest counts: {min_guests} to {max_guests}")
        
        recommendations = []
        
        for size in range(min_guests, max_guests + 1):
            for guest_combo in combinations(self.friends, size):
                guests = list(guest_combo)
                satisfaction, menu, cost = self.find_best_menu(guests, config.budget)
                
                if not menu:
                    continue
                
                intimacy = sum(g.intimacy for g in guests)
                savings = config.budget - cost
                efficiency = satisfaction / cost if cost > 0 else 0
                happiness = self.calculate_happiness(satisfaction, savings, intimacy, len(guests), len(menu), config.budget, config)
                
                recommendations.append(PartyRecommendation(
                    guest_list=[g.name for g in guests],
                    recommended_foods=[f.name for f in menu],
                    food_costs={f.name: f.cost for f in menu},
                    total_cost=round(cost, 2),
                    max_satisfaction=round(satisfaction, 2),
                    total_intimacy=intimacy,
                    cost_savings=round(savings, 2),
                    efficiency_score=round(efficiency, 2),
                    host_happiness=round(happiness, 2),
                    num_guests=len(guests),
                    food_categories={f.name: f.category for f in menu}
                ))
        
        print(f"  [Optimizer] Generated {len(recommendations)} valid recommendations")
        
        if recommendations:
            happiness = np.array([r.host_happiness for r in recommendations])
            satisfaction = np.array([r.max_satisfaction for r in recommendations])
            indices = np.lexsort((satisfaction, happiness))[::-1]
            return [recommendations[i] for i in indices]
        
        return []
    
    def get_top_recommendations(self, config: OptimizationConfig, top_n: int = 5) -> List[PartyRecommendation]:
        return self.optimize(config)[:top_n]
    
    def get_statistics(self, recommendations: List[PartyRecommendation]) -> Dict:
        if not recommendations:
            return {}
        
        costs = np.array([r.total_cost for r in recommendations])
        satisfactions = np.array([r.max_satisfaction for r in recommendations])
        intimacies = np.array([r.total_intimacy for r in recommendations])
        guests = np.array([r.num_guests for r in recommendations])
        
        return {
            'total': len(recommendations),
            'cost': {'mean': float(np.mean(costs)), 'std': float(np.std(costs))},
            'satisfaction': {'mean': float(np.mean(satisfactions)), 'std': float(np.std(satisfactions))},
            'intimacy': {'mean': float(np.mean(intimacies))},
            'guests': {'mean': float(np.mean(guests)), 'min': int(np.min(guests)), 'max': int(np.max(guests))}
        }