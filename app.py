"""
House Party Optimizer - Application Core
"""
from core import FriendRepository, FoodRepository, EXPORT_DIR
from services import CSVImporter, PartyDataAnalyzer, FriendDataGenerator
from menus import OptimizationMenu, FriendsMenu, FoodsMenu, AnalysisMenu
from utils import initialize_sample_data, print_header, print_section, wait_for_key, export_recommendations_to_json


class PartyPlannerApp:
    """Main application coordinator."""
    
    def __init__(self):
        # Repositories
        self.friend_repo = FriendRepository()
        self.food_repo = FoodRepository()
        
        # Services
        self.csv_importer = CSVImporter(self.friend_repo, self.food_repo)
        self.analyzer = PartyDataAnalyzer(self.friend_repo, self.food_repo)
        
        # Menus
        self.optimization_menu = OptimizationMenu(self.friend_repo, self.food_repo)
        self.friends_menu = FriendsMenu(
            self.friend_repo, self.food_repo,
            self.csv_importer, self.analyzer, FriendDataGenerator
        )
        self.foods_menu = FoodsMenu(self.friend_repo, self.food_repo, self.analyzer)
        self.analysis_menu = AnalysisMenu(self.friend_repo, self.food_repo, self.analyzer)
        
        # Initialize sample data if empty
        if self.friend_repo.count() == 0 or self.food_repo.count() == 0:
            self._init_sample_data()
    
    def _init_sample_data(self):
        print_section("Initializing sample data...")
        friends, foods = initialize_sample_data()
        
        for friend in friends:
            try:
                self.friend_repo.add(friend)
            except ValueError:
                pass
        
        for food in foods:
            try:
                self.food_repo.add(food)
            except ValueError:
                pass
        
        print(f"✓ Loaded {self.friend_repo.count()} friends, {self.food_repo.count()} foods")
    
    def display_menu(self):
        print_header("🎉 HOUSE PARTY OPTIMIZER 🎉")
        print("1. Optimize party\n2. Manage friends\n3. Manage foods\n4. Data analysis\n5. Export recommendations\n0. Exit\n")
    
    def export_recommendations(self):
        recs = self.optimization_menu.get_last_recommendations()
        if not recs:
            print("❌ No recommendations. Run optimization first.")
            wait_for_key()
            return
        
        filename = input("Filename [recommendations.json]: ").strip() or "recommendations.json"
        export_recommendations_to_json(recs, str(EXPORT_DIR / filename))
        wait_for_key()
    
    def run(self):
        while True:
            self.display_menu()
            choice = input("Choice (0-5): ").strip()
            
            if choice == '1':
                self.optimization_menu.run()
            elif choice == '2':
                self.friends_menu.run()
            elif choice == '3':
                self.foods_menu.run()
            elif choice == '4':
                self.analysis_menu.run()
            elif choice == '5':
                self.export_recommendations()
            elif choice == '0':
                print_header("Thank you! 🎉")
                break
            else:
                print("❌ Invalid choice")
                wait_for_key()