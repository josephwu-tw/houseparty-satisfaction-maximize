"""
Optimization menu handler.
"""
import json
from .base import BaseMenu
from core.models import OptimizationConfig
from core.optimizer import PartyOptimizer
from core.config import (
    DEFAULT_MAX_GUESTS, EXPORT_DIR, MIN_FOOD_ITEMS, MIN_DRINK_ITEMS,
    FOOD_CATEGORIES, DRINK_CATEGORY, validate_weights
)
from utils import print_header, print_section, wait_for_key, get_user_input, validate_budget, display_summary_table


class OptimizationMenu(BaseMenu):
    """Handles party optimization workflow."""
    
    def __init__(self, friend_repo, food_repo):
        super().__init__(friend_repo, food_repo)
        self.last_recommendations = None
    
    def display(self):
        pass
    
    def handle_choice(self, choice: str) -> bool:
        return False
    
    def run(self):
        print_header("PARTY OPTIMIZATION")
        print("Menu Requirements:")
        print("  • At least 1 food + 1 drink, Maximum 3 foods + 2 drinks\n")
        
        config = self._get_config()
        if not config:
            return
        
        friends, foods = self._validate_data()
        if not friends:
            return
        
        recs = self._run_optimization(friends, foods, config)
        if not recs:
            return
        
        self.last_recommendations = recs
        self._display_results(recs, config.budget)
        self._interactive_review(recs)
    
    def _get_config(self):
        budget = get_user_input("Enter your budget ($): ", float, validate_budget)
        if budget is None:
            return None
        
        print(f"\nGuest Selection:")
        max_input = input(f"  Maximum guests [default: {DEFAULT_MAX_GUESTS}]: ").strip()
        try:
            max_guests = int(max_input) if max_input else DEFAULT_MAX_GUESTS
        except ValueError:
            max_guests = DEFAULT_MAX_GUESTS
        
        if max_guests < 1:
            self.show_error("Must invite at least 1 guest")
            return None
        
        total = self.friend_repo.count()
        if max_guests > total:
            print(f"  Note: Only {total} friends available")
            max_guests = total
        print(f"  → Will consider 1-{max_guests} guests")
        
        print("\nWeights (Press Enter for defaults):")
        try:
            sat = float(input("Satisfaction (0.4): ").strip() or 0.4)
            sav = float(input("Savings (0.2): ").strip() or 0.2)
            intim = float(input("Intimacy (0.4): ").strip() or 0.4)
        except ValueError:
            self.show_error("Invalid weight")
            return None
        
        if not validate_weights(sat, sav, intim):
            self.show_error(f"Weights must sum to 1.0, got {sat+sav+intim:.2f}")
            return None
        
        return OptimizationConfig(budget=budget, max_guests=max_guests,
                                  satisfaction_weight=sat, savings_weight=sav, intimacy_weight=intim)
    
    def _validate_data(self):
        friends = self.friend_repo.get_all()
        foods = self.food_repo.get_all()
        
        if not friends or not foods:
            self.show_error("No friends or foods available")
            return None, None
        
        food_items = [f for f in foods if f.category in FOOD_CATEGORIES]
        drink_items = [f for f in foods if f.category == DRINK_CATEGORY]
        
        if len(food_items) < MIN_FOOD_ITEMS:
            self.show_error(f"Need at least {MIN_FOOD_ITEMS} food item")
            return None, None
        if len(drink_items) < MIN_DRINK_ITEMS:
            self.show_error(f"Need at least {MIN_DRINK_ITEMS} drink item")
            return None, None
        
        return friends, foods
    
    def _run_optimization(self, friends, foods, config):
        print_section("Running optimization...")
        
        optimizer = PartyOptimizer(friends, foods)
        print(f"\n✓ Available: {len(optimizer.food_items)} foods, {len(optimizer.drink_items)} drinks")
        
        if optimizer.food_items and optimizer.drink_items:
            min_cost = min(f.cost for f in optimizer.food_items) + min(d.cost for d in optimizer.drink_items)
            print(f"  Min cost/guest: ${min_cost:.2f}")
        
        recs = optimizer.get_top_recommendations(config, top_n=5)
        
        if not recs or all(len(r.recommended_foods) == 0 for r in recs):
            self.show_error("No valid recommendations. Try increasing budget.")
            return None
        return recs
    
    def _display_results(self, recs, budget):
        print_section(f"Top 5 Recommendations (Budget: ${budget:.2f})")
        display_summary_table(recs, max_rows=5)
    
    def _interactive_review(self, recs):
        while True:
            print("\n" + "=" * 60)
            print("Enter 1-5 to view details, 0 to return")
            choice = input("\nChoice: ").strip()
            
            if choice == '0':
                break
            elif choice.isdigit() and 1 <= int(choice) <= len(recs):
                rec = recs[int(choice) - 1]
                rec.print_summary(rank=int(choice))
                
                if self.confirm("\nExport this recommendation?"):
                    self._export(rec, int(choice))
                    break
            else:
                print("❌ Invalid choice")
    
    def _export(self, rec, rank):
        foods = [f for f in rec.recommended_foods if rec.food_categories.get(f) != DRINK_CATEGORY]
        drinks = [f for f in rec.recommended_foods if rec.food_categories.get(f) == DRINK_CATEGORY]
        
        data = {
            'rank': rank,
            'guests': rec.guest_list,
            'menu': {'foods': foods, 'drinks': drinks},
            'cost': {'total': rec.total_cost, 'savings': rec.cost_savings},
            'metrics': {'satisfaction': rec.max_satisfaction, 'intimacy': rec.total_intimacy, 'happiness': rec.host_happiness}
        }
        
        filename = input(f"\nFilename [recommendation_{rank}.json]: ").strip() or f"recommendation_{rank}.json"
        with open(EXPORT_DIR / filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"\n✓ Exported to {EXPORT_DIR / filename}")
        wait_for_key()
    
    def get_last_recommendations(self):
        return self.last_recommendations