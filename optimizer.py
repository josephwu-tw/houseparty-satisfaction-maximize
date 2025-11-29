"""
Optimization service using dynamic programming with numpy.
Enforces menu constraints: 3 food items + 2 beverages.
"""
import numpy as np
from typing import List, Tuple, Dict
from itertools import combinations
from models import Friend, Food, PartyRecommendation, OptimizationConfig
from config import NUMPY_DTYPE_DP, REQUIRED_FOOD_ITEMS, REQUIRED_DRINK_ITEMS, FOOD_CATEGORIES, DRINK_CATEGORY


class PartyOptimizer:
    """Party optimizer with menu composition constraints."""
    
    def __init__(self, friends: List[Friend], foods: List[Food]):
        self.friends = friends
        self.foods = foods
        
        # Separate foods into categories
        self.food_items = [f for f in foods if f.category in FOOD_CATEGORIES]
        self.drink_items = [f for f in foods if f.category == DRINK_CATEGORY]
        
        self.food_costs = np.array([food.cost for food in foods])
        self.food_names = [food.name for food in foods]
    
    def calculate_food_values_vectorized(self, guest_list: List[Friend]) -> np.ndarray:
        """Calculate food values: Σ(preference × intimacy) for all guests."""
        n_foods = len(self.foods)
        values = np.zeros(n_foods)
        
        for i, food in enumerate(self.foods):
            for friend in guest_list:
                values[i] += friend.get_preference(food.name) * friend.intimacy
        
        return values
    
    def calculate_menu_satisfaction(self, selected_foods: List[Food], guest_list: List[Friend]) -> float:
        """Calculate total satisfaction for a specific menu selection."""
        total_satisfaction = 0.0
        for food in selected_foods:
            for friend in guest_list:
                total_satisfaction += friend.get_preference(food.name) * friend.intimacy
        return total_satisfaction
    
    def find_best_menu(self, guest_list: List[Friend], budget: float) -> Tuple[float, List[Food], float]:
        """
        Find best menu satisfying constraints:
        - Exactly 3 food items (from main/snack/dessert)
        - Exactly 2 drink items
        - Within budget (cost per person × num_guests)
        
        Args:
            guest_list: List of invited guests
            budget: Total budget in dollars
            
        Returns:
            Tuple of (max_satisfaction, selected_foods, total_cost)
        """
        if not self.food_items or not self.drink_items or not guest_list or budget <= 0:
            return 0.0, [], 0.0
        
        # Check if we have enough items
        if len(self.food_items) < REQUIRED_FOOD_ITEMS:
            return 0.0, [], 0.0
        if len(self.drink_items) < REQUIRED_DRINK_ITEMS:
            return 0.0, [], 0.0
        
        num_guests = len(guest_list)
        best_satisfaction = 0.0
        best_menu = []
        best_cost = 0.0
        
        # Try all combinations of 3 food items
        for food_combo in combinations(self.food_items, REQUIRED_FOOD_ITEMS):
            # Try all combinations of 2 drink items
            for drink_combo in combinations(self.drink_items, REQUIRED_DRINK_ITEMS):
                # Combine into full menu
                menu = list(food_combo) + list(drink_combo)
                
                # Calculate total cost (per person × num guests)
                total_cost = sum(item.cost for item in menu) * num_guests
                
                # Check if within budget
                if total_cost <= budget:
                    # Calculate satisfaction
                    satisfaction = self.calculate_menu_satisfaction(menu, guest_list)
                    
                    # Update best if better
                    if satisfaction > best_satisfaction:
                        best_satisfaction = satisfaction
                        best_menu = menu
                        best_cost = total_cost
        
        return best_satisfaction, best_menu, best_cost
    
    def knapsack_dp_numpy(self, guest_list: List[Friend], budget: float) -> Tuple[float, List[Food], float]:
        """
        Wrapper method that uses constrained menu selection.
        Maintains backward compatibility with existing code.
        """
        return self.find_best_menu(guest_list, budget)
    
    def calculate_host_happiness(self, satisfaction: float, cost_savings: float, 
                                total_intimacy: int, config: OptimizationConfig) -> float:
        """Calculate weighted happiness score."""
        normalized_values = np.array([
            satisfaction / 100,
            cost_savings / 10,
            total_intimacy / 10
        ])
        
        weights = np.array([
            config.satisfaction_weight,
            config.savings_weight,
            config.intimacy_weight
        ])
        
        return float(np.dot(normalized_values, weights))
    
    def optimize(self, config: OptimizationConfig) -> List[PartyRecommendation]:
        """Generate and evaluate all guest combinations."""
        max_guests = config.max_guests or len(self.friends)
        recommendations = []
        
        # Try different guest list sizes
        for size in range(config.min_guests, max_guests + 1):
            for guest_combo in combinations(self.friends, size):
                guest_list = list(guest_combo)
                
                # Run DP optimization
                satisfaction, foods, cost = self.knapsack_dp_numpy(guest_list, config.budget)
                
                # Calculate metrics
                total_intimacy = sum(f.intimacy for f in guest_list)
                cost_savings = config.budget - cost
                efficiency = satisfaction / cost if cost > 0 else 0
                host_happiness = self.calculate_host_happiness(
                    satisfaction, cost_savings, total_intimacy, config
                )
                
                # Create recommendation with category info
                food_categories_map = {f.name: f.category for f in foods}
                
                recommendation = PartyRecommendation(
                    guest_list=[f.name for f in guest_list],
                    recommended_foods=[f.name for f in foods],
                    food_costs={f.name: f.cost for f in foods},  # Unit costs
                    total_cost=round(cost, 2),  # Total cost (already includes × num_guests)
                    max_satisfaction=round(satisfaction, 2),
                    total_intimacy=total_intimacy,
                    cost_savings=round(cost_savings, 2),
                    efficiency_score=round(efficiency, 2),
                    host_happiness=round(host_happiness, 2),
                    num_guests=len(guest_list),  # Store for display
                    food_categories=food_categories_map  # Store categories
                )
                
                recommendations.append(recommendation)
        
        # Sort by happiness (primary) and satisfaction (secondary)
        happiness_scores = np.array([r.host_happiness for r in recommendations])
        satisfaction_scores = np.array([r.max_satisfaction for r in recommendations])
        sort_indices = np.lexsort((satisfaction_scores, happiness_scores))[::-1]
        
        return [recommendations[i] for i in sort_indices]
    
    def get_top_recommendations(self, config: OptimizationConfig, 
                               top_n: int = 5) -> List[PartyRecommendation]:
        """Get top N recommendations."""
        all_recommendations = self.optimize(config)
        return all_recommendations[:top_n]
    
    def get_statistics(self, recommendations: List[PartyRecommendation]) -> Dict:
        """Calculate statistics using numpy."""
        if not recommendations:
            return {}
        
        costs = np.array([r.total_cost for r in recommendations])
        satisfactions = np.array([r.max_satisfaction for r in recommendations])
        intimacies = np.array([r.total_intimacy for r in recommendations])
        num_guests = np.array([len(r.guest_list) for r in recommendations])
        
        return {
            'total_recommendations': len(recommendations),
            'cost': {
                'mean': float(np.mean(costs)),
                'median': float(np.median(costs)),
                'std': float(np.std(costs)),
                'min': float(np.min(costs)),
                'max': float(np.max(costs))
            },
            'satisfaction': {
                'mean': float(np.mean(satisfactions)),
                'median': float(np.median(satisfactions)),
                'std': float(np.std(satisfactions)),
                'min': float(np.min(satisfactions)),
                'max': float(np.max(satisfactions))
            },
            'intimacy': {
                'mean': float(np.mean(intimacies)),
                'median': float(np.median(intimacies)),
            },
            'guests': {
                'mean': float(np.mean(num_guests)),
                'median': float(np.median(num_guests)),
                'mode': int(np.bincount(num_guests).argmax()),
            }
        }