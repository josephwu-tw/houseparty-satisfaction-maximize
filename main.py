"""
House Party Optimizer - Main Application
Dynamic programming solution with pandas/numpy optimization.

Authors: Chen-Yen Wu, Jinghong Yang, Yuting Wan
"""
import sys
import os
import numpy as np
from models import Friend, Food, OptimizationConfig
from repositories import FriendRepository, FoodRepository
from optimizer import PartyOptimizer
from csv_tools import CSVImporter
from data_analysis import PartyDataAnalyzer
from generate_sample_csv import FriendDataGenerator, DEFAULT_FOODS
from utils import (
    initialize_sample_data, print_header, print_section,
    validate_budget, get_user_input, display_summary_table,
    export_recommendations_to_json, validate_intimacy, wait_for_key
)
from config import get_success_message, get_error_message, EXPORT_DIR


class PartyPlannerApp:
    """Main application with integrated generator."""
    
    def __init__(self):
        self.friend_repo = FriendRepository()
        self.food_repo = FoodRepository()
        self.csv_importer = CSVImporter(self.friend_repo, self.food_repo)
        self.analyzer = PartyDataAnalyzer(self.friend_repo, self.food_repo)
        
        if self.friend_repo.count() == 0 or self.food_repo.count() == 0:
            self._initialize_with_sample_data()
    
    def _initialize_with_sample_data(self):
        print_section("Initializing with sample data...")
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
        
        print(f"✓ Loaded {self.friend_repo.count()} friends")
        print(f"✓ Loaded {self.food_repo.count()} food items")
    
    def display_main_menu(self):
        print_header("🎉 HOUSE PARTY OPTIMIZER 🎉")
        print("What would you like to do?\n")
        print("1. Optimize party planning")
        print("2. Manage friends")
        print("3. Manage food items")
        print("4. Data analysis & reports")
        print("5. Export recommendations")
        print("6. Exit")
        print()
    
    def run_optimization(self):
        print_header("PARTY OPTIMIZATION")
        
        print("Menu Requirements: 3 Food Items + 2 Beverages")
        print("Food categories: main, snack, dessert")
        print("Beverage category: drink")
        print()
        
        budget = get_user_input("Enter your budget ($): ", float, validate_budget)
        if budget is None:
            return
        
        print("\nOptimization Preferences (Press Enter for defaults):")
        satisfaction_weight = input("Satisfaction weight (default 0.5): ").strip()
        satisfaction_weight = float(satisfaction_weight) if satisfaction_weight else 0.5
        
        savings_weight = input("Savings weight (default 0.3): ").strip()
        savings_weight = float(savings_weight) if savings_weight else 0.3
        
        intimacy_weight = input("Intimacy weight (default 0.2): ").strip()
        intimacy_weight = float(intimacy_weight) if intimacy_weight else 0.2
        
        try:
            config = OptimizationConfig(budget=budget, satisfaction_weight=satisfaction_weight,
                                      savings_weight=savings_weight, intimacy_weight=intimacy_weight)
        except ValueError as e:
            print(f"\n❌ Error: {e}")
            return
        
        print_section("Running optimization...")
        
        friends = self.friend_repo.get_all()
        foods = self.food_repo.get_all()
        
        if not friends or not foods:
            print(get_error_message('no_friends'))
            wait_for_key()
            return
        
        # Check if we have enough items for menu constraints
        from config import REQUIRED_FOOD_ITEMS, REQUIRED_DRINK_ITEMS, FOOD_CATEGORIES, DRINK_CATEGORY
        
        food_items = [f for f in foods if f.category in FOOD_CATEGORIES]
        drink_items = [f for f in foods if f.category == DRINK_CATEGORY]
        
        if len(food_items) < REQUIRED_FOOD_ITEMS:
            print(f"❌ Need at least {REQUIRED_FOOD_ITEMS} food items (main/snack/dessert).")
            print(f"   Currently have: {len(food_items)}")
            print(f"   Add more food items in 'Manage food items' menu.")
            wait_for_key()
            return
        
        if len(drink_items) < REQUIRED_DRINK_ITEMS:
            print(f"❌ Need at least {REQUIRED_DRINK_ITEMS} drink items.")
            print(f"   Currently have: {len(drink_items)}")
            print(f"   Add more drinks in 'Manage food items' menu.")
            wait_for_key()
            return
        
        optimizer = PartyOptimizer(friends, foods)
        recommendations = optimizer.get_top_recommendations(config, top_n=10)
        
        if not recommendations:
            print("\n❌ No valid recommendations found with the given budget.")
            print(f"\nTo satisfy menu requirements (3 foods + 2 drinks):")
            
            # Calculate minimum cost
            cheapest_foods = sorted(food_items, key=lambda f: f.cost)[:REQUIRED_FOOD_ITEMS]
            cheapest_drinks = sorted(drink_items, key=lambda f: f.cost)[:REQUIRED_DRINK_ITEMS]
            min_per_person = sum(f.cost for f in cheapest_foods) + sum(f.cost for f in cheapest_drinks)
            
            print(f"  Minimum cost for 1 guest: ${min_per_person:.2f}")
            print(f"  Minimum cost for 2 guests: ${min_per_person * 2:.2f}")
            print(f"  Minimum cost for 3 guests: ${min_per_person * 3:.2f}")
            print(f"\n  Suggested: Increase budget or reduce guest count.")
            wait_for_key()
            return
        
        print_section(f"Top Recommendations (Budget: ${budget:.2f})")
        
        for i, rec in enumerate(recommendations[:3], 1):
            rec.print_summary(rank=i)
        
        if len(recommendations) > 3:
            print_section(f"Summary of All {len(recommendations)} Recommendations")
            display_summary_table(recommendations)
        
        stats = optimizer.get_statistics(recommendations)
        if stats:
            print_section("Statistics")
            print(f"Average Cost: ${stats['cost']['mean']:.2f} (±${stats['cost']['std']:.2f})")
            print(f"Average Satisfaction: {stats['satisfaction']['mean']:.1f}")
        
        self.last_recommendations = recommendations
        
        export = input("\nExport recommendations? (y/n): ").strip().lower()
        if export == 'y':
            self.export_recommendations()
        
        wait_for_key()
    
    def manage_friends(self):
        while True:
            print_section("MANAGE FRIENDS")
            print("1. View all friends")
            print("2. Add new friend")
            print("3. Update friend")
            print("4. Delete friend")
            print("5. Generate random friends")
            print("6. Export friends to CSV")
            print("7. Import friends from CSV")
            print("8. Generate CSV template")
            print("9. View friend statistics")
            print("10. Clear all friends")
            print("11. Back to main menu")
            
            choice = input("\nChoice: ").strip()
            
            if choice == '1':
                self.view_all_friends()
            elif choice == '2':
                self.add_friend()
            elif choice == '3':
                self.update_friend()
            elif choice == '4':
                self.delete_friend()
            elif choice == '5':
                self.generate_random_friends()
            elif choice == '6':
                self.export_friends_csv()
            elif choice == '7':
                self.import_friends_csv()
            elif choice == '8':
                self.generate_csv_template()
            elif choice == '9':
                self.view_friend_statistics()
            elif choice == '10':
                self.clear_all_friends()
            elif choice == '11':
                break
            else:
                print("❌ Invalid choice")
                wait_for_key()
    
    def generate_random_friends(self):
        print_header("🎲 RANDOM FRIEND GENERATOR")
        
        try:
            num_friends = int(input("How many friends? (1-500): ").strip())
            if not 1 <= num_friends <= 500:
                print("❌ Enter 1-500")
                return
        except ValueError:
            print("❌ Invalid number")
            return
        
        print("\nDiversity: 1=Low 2=Medium 3=High 4=Realistic")
        diversity_choice = input("Choose (1-4) [default: 4]: ").strip() or "4"
        diversity_map = {"1": "low", "2": "medium", "3": "high", "4": "realistic"}
        diversity = diversity_map.get(diversity_choice, "realistic")
        
        print("\nDistribution: 1=Normal 2=Uniform 3=Bimodal")
        intimacy_choice = input("Choose (1-3) [default: 1]: ").strip() or "1"
        intimacy_map = {"1": "normal", "2": "uniform", "3": "bimodal"}
        intimacy_dist = intimacy_map.get(intimacy_choice, "normal")
        
        foods = [food.name for food in self.food_repo.get_all()]
        if not foods:
            foods = DEFAULT_FOODS
        
        use_seed = input("\nUse random seed? (y/n) [default: n]: ").strip().lower()
        seed = None
        if use_seed == 'y':
            try:
                seed = int(input("Enter seed: ").strip())
            except ValueError:
                print("⚠️  Invalid seed")
        
        print("\n" + "="*70)
        generator = FriendDataGenerator(seed=seed)
        df = generator.generate_batch(num_friends, foods, diversity, intimacy_dist)
        
        print("\n📋 Preview (first 5):")
        preview_cols = ['Name', 'Intimacy'] + foods[:3]
        print(df[preview_cols].head().to_string(index=False))
        
        print("\n" + "="*70)
        confirm = input(f"\nAdd {num_friends} friends to database? (y/n): ").strip().lower()
        
        if confirm == 'y':
            added, updated, errors = 0, 0, 0
            
            for _, row in df.iterrows():
                try:
                    name = row['Name']
                    intimacy = int(row['Intimacy'])
                    dietary_restrictions = []
                    
                    if 'Dietary_Restrictions' in row and row['Dietary_Restrictions']:
                        dietary_restrictions = [r.strip() for r in str(row['Dietary_Restrictions']).split(';')]
                    
                    preferences = {}
                    for food in foods:
                        if food in row and not np.isnan(row[food]):
                            preferences[food] = int(row[food])
                    
                    friend = Friend(name, preferences, intimacy, dietary_restrictions)
                    
                    existing = self.friend_repo.get_by_name(name)
                    if existing:
                        self.friend_repo.update(friend)
                        updated += 1
                    else:
                        self.friend_repo.add(friend)
                        added += 1
                        
                except Exception as e:
                    errors += 1
            
            print("\n" + "="*70)
            print("✓ Complete!")
            print(f"  Added: {added}")
            print(f"  Updated: {updated}")
            if errors > 0:
                print(f"  Errors: {errors}")
            print("="*70)
            
            save_csv = input("\nSave to CSV? (y/n) [default: n]: ").strip().lower()
            if save_csv == 'y':
                filename = input("Filename [default: generated_friends.csv]: ").strip() or "generated_friends.csv"
                filepath = EXPORT_DIR / filename
                df.to_csv(filepath, index=False)
                print(f"✓ Saved to {filepath}")
        else:
            save_csv = input("\nSave to CSV without adding? (y/n): ").strip().lower()
            if save_csv == 'y':
                filename = input("Filename [default: generated_friends.csv]: ").strip() or "generated_friends.csv"
                filepath = EXPORT_DIR / filename
                df.to_csv(filepath, index=False)
                print(f"✓ Saved to {filepath}")
        
        wait_for_key()
    
    def view_all_friends(self):
        print_section("ALL FRIENDS")
        df = self.analyzer.get_friend_summary_df()
        
        if df.empty:
            print("No friends found.")
            wait_for_key()
            return
        
        print(df[['Name', 'Intimacy', 'Avg_Preference', 'Num_Foods_Rated', 'Restrictions']].to_string(index=False))
        print(f"\nTotal: {len(df)} friends")
        wait_for_key()
    
    def view_friend_statistics(self):
        print_section("FRIEND STATISTICS")
        df = self.analyzer.get_friend_summary_df()
        
        if df.empty:
            print("No friends.")
            wait_for_key()
            return
        
        print("\n📊 Overview:")
        print(f"  Total: {len(df)}")
        print(f"  Avg Intimacy: {df['Intimacy'].mean():.2f}")
        print(f"  Avg Preference: {df['Avg_Preference'].mean():.2f}")
        
        print("\n🏆 Top 5:")
        print(df[['Name', 'Intimacy', 'Avg_Preference']].head().to_string(index=False))
        wait_for_key()
    
    def add_friend(self):
        print_section("ADD FRIEND")
        
        name = input("Name: ").strip()
        if not name:
            print("❌ Name required")
            wait_for_key()
            return
        
        try:
            intimacy = int(input("Intimacy (1-10): ").strip())
            if not validate_intimacy(intimacy):
                print(get_error_message('invalid_intimacy'))
                wait_for_key()
                return
        except ValueError:
            print("❌ Invalid")
            wait_for_key()
            return
        
        print("\nRate each food (1-5):")
        preferences = {}
        for food in self.food_repo.get_all():
            while True:
                try:
                    rating = int(input(f"  {food.name}: ").strip())
                    if 1 <= rating <= 5:
                        preferences[food.name] = rating
                        break
                    print("    Must be 1-5")
                except ValueError:
                    print("    Invalid")
        
        restrictions_input = input("\nDietary restrictions (comma-separated, or Enter): ").strip()
        restrictions = [r.strip() for r in restrictions_input.split(',')] if restrictions_input else []
        
        try:
            friend = Friend(name, preferences, intimacy, restrictions)
            self.friend_repo.add(friend)
            print(f"\n{get_success_message('friend_added', name=name)}")
        except ValueError as e:
            print(f"\n❌ Error: {e}")
        
        wait_for_key()
    
    def update_friend(self):
        print_section("UPDATE FRIEND")
        
        name = input("Enter friend's name: ").strip()
        friend = self.friend_repo.get_by_name(name)
        
        if not friend:
            print(f"❌ Friend '{name}' not found")
            wait_for_key()
            return
        
        print(f"\nUpdating {friend.name} (Press Enter to keep current):")
        
        intimacy_input = input(f"Intimacy (current: {friend.intimacy}): ").strip()
        if intimacy_input:
            try:
                friend.intimacy = int(intimacy_input)
            except ValueError:
                print("❌ Invalid, keeping current")
        
        print(f"\n{get_success_message('friend_updated', name=friend.name)}")
        self.friend_repo.update(friend)
        wait_for_key()
    
    def delete_friend(self):
        print_section("DELETE FRIEND")
        
        name = input("Enter friend's name: ").strip()
        confirm = input(f"Delete '{name}'? (y/n): ").strip().lower()
        
        if confirm == 'y':
            if self.friend_repo.delete(name):
                print(f"\n{get_success_message('friend_deleted', name=name)}")
            else:
                print(f"❌ Not found")
        
        wait_for_key()
    
    def clear_all_friends(self):
        """Clear all friend data with double confirmation."""
        print_section("⚠️  CLEAR ALL FRIENDS")
        
        current_count = self.friend_repo.count()
        
        if current_count == 0:
            print("No friends to clear.")
            wait_for_key()
            return
        
        print(f"\n⚠️  WARNING: This will permanently delete ALL {current_count} friends!")
        print("This action CANNOT be undone.")
        print("\nRecommendation: Export to CSV first (Menu option 6)")
        
        # First confirmation
        confirm1 = input(f"\nAre you sure you want to delete ALL {current_count} friends? (yes/no): ").strip().lower()
        
        if confirm1 != 'yes':
            print("\n✓ Operation cancelled. No friends were deleted.")
            wait_for_key()
            return
        
        # Second confirmation with exact count
        print(f"\n⚠️  FINAL WARNING: You are about to delete {current_count} friends permanently!")
        confirm2 = input(f"Type 'DELETE ALL' to confirm: ").strip()
        
        if confirm2 == 'DELETE ALL':
            # Clear all friends
            deleted_count = self.friend_repo.clear_all()
            
            print("\n" + "="*60)
            print(f"✓ All {deleted_count} friends have been deleted.")
            print("  The friend database has been cleared.")
            print("="*60)
        else:
            print("\n✓ Operation cancelled. No friends were deleted.")
        
        wait_for_key()
    
    def export_friends_csv(self):
        print_section("EXPORT TO CSV")
        
        filename = input("Filename [default: friends_export.csv]: ").strip() or "friends_export.csv"
        filepath = EXPORT_DIR / filename
        include_stats = input("Include statistics? (y/n) [default: n]: ").strip().lower() == 'y'
        
        try:
            count = self.csv_importer.export_friends_to_csv(str(filepath), include_stats)
            print(f"\n{get_success_message('csv_exported', count=count, filename=str(filepath))}")
        except Exception as e:
            print(f"\n❌ Error: {e}")
        
        wait_for_key()
    
    def import_friends_csv(self):
        print_section("IMPORT FROM CSV")
        
        print("Required: Name, Intimacy columns")
        print("Optional: Dietary_Restrictions, Food preferences\n")
        
        filename = input("CSV filename: ").strip()
        
        if not filename:
            print("❌ Filename required")
            return
        
        # Check if file exists in current dir or exports dir
        if os.path.exists(filename):
            filepath = filename
        elif os.path.exists(EXPORT_DIR / filename):
            filepath = str(EXPORT_DIR / filename)
        else:
            print(get_error_message('file_not_found', filename=filename))
            print(f"  Checked: ./{filename}")
            print(f"  Checked: {EXPORT_DIR / filename}")
            return
        
        is_valid, message = self.csv_importer.validate_csv_format(filepath)
        if not is_valid:
            print(f"❌ {message}")
            return
        
        print(f"\n✓ {message}")
        print(f"  Importing from: {filepath}")
        
        update_existing = input("Update existing? (y/n) [default: y]: ").strip().lower()
        update_existing = update_existing != 'n'
        
        print("Importing...")
        
        try:
            stats = self.csv_importer.import_friends_from_csv(filepath, update_existing)
            
            print(f"\n{'='*60}")
            print(f"Import Summary:")
            print(f"  Total: {stats['total_rows']}")
            print(f"  ✓ Added: {stats['successful']}")
            print(f"  ✓ Updated: {stats['updated']}")
            print(f"  ✗ Failed: {stats['failed']}")
            
            if stats['errors']:
                print(f"\nErrors (first 10):")
                for error in stats['errors'][:10]:
                    print(f"  • {error}")
                if len(stats['errors']) > 10:
                    print(f"  ... {len(stats['errors']) - 10} more")
            
            print(f"{'='*60}")
            
        except Exception as e:
            print(f"\n❌ Import failed: {e}")
        
        wait_for_key()
    
    def generate_csv_template(self):
        print_section("GENERATE TEMPLATE")
        
        filename = input("Filename [default: friends_template.csv]: ").strip() or "friends_template.csv"
        filepath = EXPORT_DIR / filename
        
        try:
            self.csv_importer.get_csv_template(str(filepath))
            print(f"\n✓ Template: {filepath}")
            print("  • All food items as columns")
            print("  • Example data included")
        except Exception as e:
            print(f"\n❌ Error: {e}")
        
        wait_for_key()
    
    def manage_food_items(self):
        while True:
            print_section("MANAGE FOOD ITEMS")
            print("1. View all food items")
            print("2. Add new food item")
            print("3. View food analytics")
            print("4. Clear all food items")
            print("5. Back to main menu")
            
            choice = input("\nChoice: ").strip()
            
            if choice == '1':
                self.view_all_foods()
            elif choice == '2':
                self.add_food()
            elif choice == '3':
                self.view_food_analytics()
            elif choice == '4':
                self.clear_all_foods()
            elif choice == '5':
                break
            else:
                print("❌ Invalid choice")
                wait_for_key()
    
    def view_all_foods(self):
        print_section("ALL FOOD ITEMS")
        df = self.analyzer.get_food_analysis_df()
        
        if df.empty:
            print("No foods.")
            wait_for_key()
            return
        
        print(df[['Food', 'Cost', 'Category', 'Avg_Rating', 'Num_Ratings']].to_string(index=False))
        print(f"\nTotal: {len(df)}, Cost: ${df['Cost'].sum():.2f}")
        wait_for_key()
    
    def view_food_analytics(self):
        print_section("FOOD ANALYTICS")
        df = self.analyzer.get_food_analysis_df()
        
        if df.empty:
            print("No data.")
            wait_for_key()
            return
        
        print("\n🏆 Top 5 Popular:")
        print(df[['Food', 'Avg_Rating', 'Popularity_Score']].head().to_string(index=False))
        
        print("\n💰 Top 5 Value:")
        best_value = df.nlargest(5, 'Value_Score')
        print(best_value[['Food', 'Cost', 'Weighted_Avg', 'Value_Score']].to_string(index=False))
        wait_for_key()
    
    def add_food(self):
        print_section("ADD FOOD")
        
        name = input("Name: ").strip()
        if not name:
            print("❌ Name required")
            wait_for_key()
            return
        
        try:
            cost = float(input("Cost ($): ").strip())
            if cost < 0:
                print("❌ Cost >= 0")
                wait_for_key()
                return
        except ValueError:
            print("❌ Invalid")
            wait_for_key()
            return
        
        category = input("Category (snack/drink/main/dessert) [default: snack]: ").strip() or "snack"
        
        try:
            food = Food(name, cost, category)
            self.food_repo.add(food)
            print(f"\n{get_success_message('food_added', name=name)}")
        except ValueError as e:
            print(f"\n❌ Error: {e}")
        
        wait_for_key()
    
    def clear_all_foods(self):
        """Clear all food data with double confirmation."""
        print_section("⚠️  CLEAR ALL FOOD ITEMS")
        
        current_count = self.food_repo.count()
        
        if current_count == 0:
            print("No food items to clear.")
            wait_for_key()
            return
        
        print(f"\n⚠️  WARNING: This will permanently delete ALL {current_count} food items!")
        print("This action CANNOT be undone.")
        print("\n⚠️  Note: Deleting foods will affect friend preferences and optimization!")
        
        # First confirmation
        confirm1 = input(f"\nAre you sure you want to delete ALL {current_count} food items? (yes/no): ").strip().lower()
        
        if confirm1 != 'yes':
            print("\n✓ Operation cancelled. No food items were deleted.")
            wait_for_key()
            return
        
        # Second confirmation
        print(f"\n⚠️  FINAL WARNING: Deleting {current_count} food items!")
        confirm2 = input(f"Type 'DELETE ALL' to confirm: ").strip()
        
        if confirm2 == 'DELETE ALL':
            deleted_count = self.food_repo.clear_all()
            
            print("\n" + "="*60)
            print(f"✓ All {deleted_count} food items have been deleted.")
            print("  The food database has been cleared.")
            print("  You may want to reinitialize with sample data.")
            print("="*60)
        else:
            print("\n✓ Operation cancelled. No food items were deleted.")
        
        wait_for_key()
    
    def data_analysis_menu(self):
        while True:
            print_section("DATA ANALYSIS")
            print("1. Generate text report")
            print("2. View preference matrix")
            print("3. View food popularity")
            print("4. Generate visualizations")
            print("5. Back")
            
            choice = input("\nChoice: ").strip()
            
            if choice == '1':
                self.generate_text_report()
            elif choice == '2':
                self.view_preference_matrix()
            elif choice == '3':
                self.view_food_popularity()
            elif choice == '4':
                self.generate_visualizations()
            elif choice == '5':
                break
            else:
                print("❌ Invalid choice")
                wait_for_key()
    
    def generate_text_report(self):
        print_section("TEXT REPORT")
        
        report = self.analyzer.generate_text_report()
        print(report)
        
        save = input("\nSave to file? (y/n): ").strip().lower()
        if save == 'y':
            filename = input("Filename [default: party_report.txt]: ").strip() or "party_report.txt"
            filepath = EXPORT_DIR / filename
            with open(filepath, 'w') as f:
                f.write(report)
            print(f"✓ Saved to {filepath}")
        
        wait_for_key()
    
    def view_preference_matrix(self):
        print_section("PREFERENCE MATRIX")
        
        matrix = self.analyzer.get_preference_matrix()
        if matrix.empty:
            print("No data.")
            wait_for_key()
            return
        
        print(matrix.to_string())
        wait_for_key()
    
    def view_food_popularity(self):
        print_section("FOOD POPULARITY")
        
        df = self.analyzer.get_food_popularity()
        if df.empty:
            print("No data.")
            wait_for_key()
            return
        
        print(df.to_string(index=False))
        wait_for_key()
    
    def generate_visualizations(self):
        print_section("VISUALIZATIONS")
        
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            print("❌ Install: pip install matplotlib seaborn")
            wait_for_key()
            return
        
        print("1. Intimacy distribution")
        print("2. Food analysis")
        print("3. Preference heatmap")
        print("4. All")
        
        choice = input("\nChoice: ").strip()
        save_plots = input("Save to files? (y/n) [default: n]: ").strip().lower() == 'y'
        
        try:
            if choice in ['1', '4']:
                path = str(EXPORT_DIR / "intimacy_distribution.png") if save_plots else None
                self.analyzer.plot_intimacy_distribution(path)
            
            if choice in ['2', '4']:
                path = str(EXPORT_DIR / "food_analysis.png") if save_plots else None
                self.analyzer.plot_food_analysis(path)
            
            if choice in ['3', '4']:
                path = str(EXPORT_DIR / "preference_heatmap.png") if save_plots else None
                self.analyzer.plot_preference_heatmap(path)
            
            if not save_plots:
                print("\n✓ Displayed")
        except Exception as e:
            print(f"\n❌ Error: {e}")
        
        wait_for_key()
    
    def export_recommendations(self):
        if not hasattr(self, 'last_recommendations') or not self.last_recommendations:
            print("❌ No recommendations. Run optimization first.")
            wait_for_key()
            return
        
        filename = input("\nFilename [default: recommendations.json]: ").strip() or "recommendations.json"
        filepath = EXPORT_DIR / filename
        export_recommendations_to_json(self.last_recommendations, str(filepath))
        wait_for_key()
    
    def run(self):
        while True:
            self.display_main_menu()
            choice = input("Choice (1-6): ").strip()
            
            if choice == '1':
                self.run_optimization()
            elif choice == '2':
                self.manage_friends()
            elif choice == '3':
                self.manage_food_items()
            elif choice == '4':
                self.data_analysis_menu()
            elif choice == '5':
                self.export_recommendations()
            elif choice == '6':
                print_header("Thank you! 🎉")
                sys.exit(0)
            else:
                print("❌ Invalid choice")
                wait_for_key()


def main():
    try:
        app = PartyPlannerApp()
        app.run()
    except KeyboardInterrupt:
        print("\n\nTerminated by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()