"""
Food items management menu handler.
"""
from .base import BaseMenu
from core.models import Food
from core.config import FOOD_CATEGORIES, DRINK_CATEGORY, MIN_FOOD_ITEMS, MIN_DRINK_ITEMS, get_success_message
from utils import print_section, wait_for_key


class FoodsMenu(BaseMenu):
    """Handles food item management."""
    
    def __init__(self, friend_repo, food_repo, analyzer):
        super().__init__(friend_repo, food_repo)
        self.analyzer = analyzer
    
    def display(self):
        print_section("MANAGE FOOD ITEMS")
        print("1. View all\n2. Add\n3. Analytics\n4. By category\n5. Clear all\n0. Back")
    
    def handle_choice(self, choice: str) -> bool:
        actions = {'1': self.view_all, '2': self.add, '3': self.analytics, '4': self.by_category, '5': self.clear_all}
        if choice == '0':
            return False
        if choice in actions:
            actions[choice]()
        else:
            self.show_error("Invalid choice")
        return True
    
    def view_all(self):
        print_section("ALL FOOD ITEMS")
        df = self.analyzer.get_food_analysis_df()
        if df.empty:
            print("No foods.")
        else:
            print(df[['Food', 'Cost', 'Category', 'Avg_Rating']].to_string(index=False))
            print(f"\nTotal: {len(df)}, Total Cost: ${df['Cost'].sum():.2f}")
        wait_for_key()
    
    def add(self):
        print_section("ADD FOOD")
        name = input("Name: ").strip()
        if not name:
            self.show_error("Name required")
            return
        
        try:
            cost = float(input("Cost ($): ").strip())
            if cost < 0:
                self.show_error("Cost must be >= 0")
                return
        except ValueError:
            self.show_error("Invalid cost")
            return
        
        category = input("Category (main/snack/dessert/drink) [snack]: ").strip() or "snack"
        
        try:
            self.food_repo.add(Food(name, cost, category))
            print(f"\n{get_success_message('food_added', name=name)}")
        except ValueError as e:
            self.show_error(str(e))
        wait_for_key()
    
    def analytics(self):
        print_section("FOOD ANALYTICS")
        df = self.analyzer.get_food_analysis_df()
        if df.empty:
            print("No data.")
        else:
            print("\n🏆 Top 5 Popular:")
            print(df[['Food', 'Avg_Rating', 'Popularity_Score']].head().to_string(index=False))
            print("\n💰 Top 5 Value:")
            print(df.nlargest(5, 'Value_Score')[['Food', 'Cost', 'Value_Score']].to_string(index=False))
        wait_for_key()
    
    def by_category(self):
        print_section("FOOD ITEMS BY CATEGORY")
        foods = self.food_repo.get_all()
        if not foods:
            print("No items.")
            wait_for_key()
            return
        
        food_items = [f for f in foods if f.category in FOOD_CATEGORIES]
        drink_items = [f for f in foods if f.category == DRINK_CATEGORY]
        
        print(f"\n🍴 FOODS ({len(food_items)}, need {MIN_FOOD_ITEMS}):")
        for cat in FOOD_CATEGORIES:
            items = [f for f in food_items if f.category == cat]
            if items:
                print(f"\n  {cat.upper()}:")
                for f in items:
                    print(f"    • {f.name}: ${f.cost:.2f}")
        
        print(f"\n🥤 DRINKS ({len(drink_items)}, need {MIN_DRINK_ITEMS}):")
        for f in drink_items:
            print(f"    • {f.name}: ${f.cost:.2f}")
        
        if food_items and drink_items:
            min_cost = min(f.cost for f in food_items) + min(d.cost for d in drink_items)
            print(f"\n💰 Min cost/guest: ${min_cost:.2f}")
        wait_for_key()
    
    def clear_all(self):
        print_section("⚠️ CLEAR ALL FOODS")
        count = self.food_repo.count()
        if count == 0:
            print("Nothing to clear.")
            wait_for_key()
            return
        
        print(f"\n⚠️ This will delete ALL {count} food items!")
        if input("Type 'yes' to confirm: ").strip().lower() == 'yes':
            if input("Type 'DELETE ALL': ").strip() == 'DELETE ALL':
                self.food_repo.clear_all()
                print(f"\n✓ Deleted {count} items.")
            else:
                print("\n✓ Cancelled.")
        else:
            print("\n✓ Cancelled.")
        wait_for_key()