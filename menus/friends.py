"""
Friends management menu handler.
"""
import os
import numpy as np
from .base import BaseMenu
from core.models import Friend
from core.config import EXPORT_DIR, DEFAULT_FOODS, get_success_message, get_error_message
from utils import print_header, print_section, wait_for_key, validate_intimacy


class FriendsMenu(BaseMenu):
    """Handles friend management."""
    
    def __init__(self, friend_repo, food_repo, csv_importer, analyzer, generator_class):
        super().__init__(friend_repo, food_repo)
        self.csv_importer = csv_importer
        self.analyzer = analyzer
        self.generator_class = generator_class
    
    def display(self):
        print_section("MANAGE FRIENDS")
        options = [
            "1. View all", "2. Add", "3. Update", "4. Delete",
            "5. Generate random", "6. Export CSV", "7. Import CSV",
            "8. Generate template", "9. Statistics", "10. Clear all", "0. Back"
        ]
        print("\n".join(options))
    
    def handle_choice(self, choice: str) -> bool:
        actions = {
            '1': self.view_all, '2': self.add, '3': self.update, '4': self.delete,
            '5': self.generate_random, '6': self.export_csv, '7': self.import_csv,
            '8': self.generate_template, '9': self.statistics, '10': self.clear_all
        }
        if choice == '0':
            return False
        if choice in actions:
            actions[choice]()
        else:
            self.show_error("Invalid choice")
        return True
    
    def view_all(self):
        print_section("ALL FRIENDS")
        df = self.analyzer.get_friend_summary_df()
        if df.empty:
            print("No friends.")
        else:
            print(df[['Name', 'Intimacy', 'Avg_Preference', 'Restrictions']].to_string(index=False))
            print(f"\nTotal: {len(df)}")
        wait_for_key()
    
    def add(self):
        print_section("ADD FRIEND")
        name = input("Name: ").strip()
        if not name:
            self.show_error("Name required")
            return
        
        try:
            intimacy = int(input("Intimacy (1-10): ").strip())
            if not validate_intimacy(intimacy):
                self.show_error("Intimacy must be 1-10")
                return
        except ValueError:
            self.show_error("Invalid number")
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
        
        restrictions = input("\nDietary restrictions (comma-separated): ").strip()
        restrictions = [r.strip() for r in restrictions.split(',')] if restrictions else []
        
        try:
            self.friend_repo.add(Friend(name, preferences, intimacy, restrictions))
            print(f"\n{get_success_message('friend_added', name=name)}")
        except ValueError as e:
            self.show_error(str(e))
        wait_for_key()
    
    def update(self):
        print_section("UPDATE FRIEND")
        name = input("Friend name: ").strip()
        friend = self.friend_repo.get_by_name(name)
        if not friend:
            self.show_error(f"'{name}' not found")
            return
        
        print(f"\nUpdating {friend.name} (Enter to keep current):")
        intimacy_input = input(f"Intimacy ({friend.intimacy}): ").strip()
        if intimacy_input:
            try:
                friend.intimacy = int(intimacy_input)
            except ValueError:
                print("⚠️ Keeping current")
        
        self.friend_repo.update(friend)
        print(f"\n{get_success_message('friend_updated', name=friend.name)}")
        wait_for_key()
    
    def delete(self):
        print_section("DELETE FRIEND")
        name = input("Friend name: ").strip()
        if self.confirm(f"Delete '{name}'?"):
            if self.friend_repo.delete(name):
                print(f"\n{get_success_message('friend_deleted', name=name)}")
            else:
                self.show_error("Not found")
        wait_for_key()
    
    def generate_random(self):
        print_header("🎲 RANDOM FRIEND GENERATOR")
        try:
            num = int(input("How many? (1-500): ").strip())
            if not 1 <= num <= 500:
                self.show_error("Enter 1-500")
                return
        except ValueError:
            self.show_error("Invalid number")
            return
        
        diversity = {"1": "low", "2": "medium", "3": "high", "4": "realistic"}.get(
            input("\nDiversity (1=Low 2=Med 3=High 4=Realistic) [4]: ").strip() or "4", "realistic")
        intimacy_dist = {"1": "normal", "2": "uniform", "3": "bimodal"}.get(
            input("Distribution (1=Normal 2=Uniform 3=Bimodal) [1]: ").strip() or "1", "normal")
        
        seed = None
        if input("\nUse seed? (y/n) [n]: ").strip().lower() == 'y':
            try:
                seed = int(input("Seed: ").strip())
            except ValueError:
                pass
        
        foods = [f.name for f in self.food_repo.get_all()] or DEFAULT_FOODS
        generator = self.generator_class(seed=seed)
        df = generator.generate_batch(num, foods, diversity, intimacy_dist)
        
        print(f"\n📋 Preview:\n{df.head().to_string(index=False)}")
        
        if self.confirm(f"\nAdd {num} friends to database?"):
            added, updated = 0, 0
            for _, row in df.iterrows():
                try:
                    prefs = {f: int(row[f]) for f in foods if f in row and not np.isnan(row[f])}
                    dietary = [r.strip() for r in str(row.get('Dietary_Restrictions', '')).split(';') if r.strip()]
                    friend = Friend(row['Name'], prefs, int(row['Intimacy']), dietary)
                    
                    if self.friend_repo.get_by_name(row['Name']):
                        self.friend_repo.update(friend)
                        updated += 1
                    else:
                        self.friend_repo.add(friend)
                        added += 1
                except Exception:
                    pass
            print(f"\n✓ Added: {added}, Updated: {updated}")
        
        if self.confirm("Save to CSV?"):
            filename = input("Filename [generated_friends.csv]: ").strip() or "generated_friends.csv"
            df.to_csv(EXPORT_DIR / filename, index=False)
            print(f"✓ Saved to {EXPORT_DIR / filename}")
        wait_for_key()
    
    def export_csv(self):
        print_section("EXPORT CSV")
        filename = input("Filename [friends_export.csv]: ").strip() or "friends_export.csv"
        try:
            count = self.csv_importer.export_friends_to_csv(str(EXPORT_DIR / filename))
            print(f"\n{get_success_message('csv_exported', count=count, filename=str(EXPORT_DIR / filename))}")
        except Exception as e:
            self.show_error(str(e))
        wait_for_key()
    
    def import_csv(self):
        print_section("IMPORT CSV")
        filename = input("CSV filename: ").strip()
        if not filename:
            self.show_error("Filename required")
            return
        
        filepath = filename if os.path.exists(filename) else str(EXPORT_DIR / filename)
        if not os.path.exists(filepath):
            self.show_error(f"File not found: {filename}")
            return
        
        valid, msg = self.csv_importer.validate_csv_format(filepath)
        if not valid:
            self.show_error(msg)
            return
        
        print(f"\n✓ {msg}")
        update = input("Update existing? (y/n) [y]: ").strip().lower() != 'n'
        
        try:
            stats = self.csv_importer.import_friends_from_csv(filepath, update)
            print(f"\n✓ Added: {stats['successful']}, Updated: {stats['updated']}, Failed: {stats['failed']}")
        except Exception as e:
            self.show_error(str(e))
        wait_for_key()
    
    def generate_template(self):
        print_section("GENERATE TEMPLATE")
        filename = input("Filename [friends_template.csv]: ").strip() or "friends_template.csv"
        self.csv_importer.get_csv_template(str(EXPORT_DIR / filename))
        print(f"\n✓ Template: {EXPORT_DIR / filename}")
        wait_for_key()
    
    def statistics(self):
        print_section("STATISTICS")
        df = self.analyzer.get_friend_summary_df()
        if df.empty:
            print("No data.")
        else:
            print(f"\nTotal: {len(df)}")
            print(f"Avg Intimacy: {df['Intimacy'].mean():.2f}")
            print(f"\n🏆 Top 5:\n{df[['Name', 'Intimacy', 'Avg_Preference']].head().to_string(index=False)}")
        wait_for_key()
    
    def clear_all(self):
        print_section("⚠️ CLEAR ALL FRIENDS")
        count = self.friend_repo.count()
        if count == 0:
            print("Nothing to clear.")
            wait_for_key()
            return
        
        print(f"\n⚠️ This will delete ALL {count} friends!")
        if input("Type 'yes' to confirm: ").strip().lower() == 'yes':
            if input("Type 'DELETE ALL': ").strip() == 'DELETE ALL':
                self.friend_repo.clear_all()
                print(f"\n✓ Deleted {count} friends.")
            else:
                print("\n✓ Cancelled.")
        else:
            print("\n✓ Cancelled.")
        wait_for_key()