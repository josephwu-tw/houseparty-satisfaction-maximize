"""
CSV import/export using pandas.
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from pathlib import Path
from models import Friend, Food
from repositories import FriendRepository, FoodRepository
from config import CSV_ENCODING


class CSVImporter:
    """CSV operations with pandas."""
    
    def __init__(self, friend_repo: FriendRepository, food_repo: FoodRepository):
        self.friend_repo = friend_repo
        self.food_repo = food_repo
        self.available_foods = [food.name for food in food_repo.get_all()]
    
    def import_friends_from_csv(self, filename: str, update_existing: bool = True) -> Dict:
        """Import friends from CSV."""
        if not Path(filename).exists():
            raise FileNotFoundError(f"CSV file not found: {filename}")
        
        df = pd.read_csv(filename, encoding=CSV_ENCODING)
        
        # Validate required columns
        required_cols = ['Name', 'Intimacy']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        stats = {'total_rows': len(df), 'successful': 0, 'updated': 0, 'failed': 0, 'errors': []}
        
        food_columns = [col for col in df.columns 
                       if col not in ['Name', 'Intimacy', 'Dietary_Restrictions']]
        
        for idx, row in df.iterrows():
            try:
                name = str(row['Name']).strip()
                if not name or pd.isna(row['Name']):
                    stats['errors'].append(f"Row {idx+2}: Missing name")
                    stats['failed'] += 1
                    continue
                
                intimacy = int(row['Intimacy'])
                if not 1 <= intimacy <= 10:
                    stats['errors'].append(f"Row {idx+2} ({name}): Intimacy must be 1-10")
                    stats['failed'] += 1
                    continue
                
                # Parse dietary restrictions
                dietary_restrictions = []
                if 'Dietary_Restrictions' in df.columns and not pd.isna(row['Dietary_Restrictions']):
                    restrictions_str = str(row['Dietary_Restrictions']).strip()
                    if restrictions_str:
                        dietary_restrictions = [r.strip() for r in restrictions_str.split(';')]
                
                # Parse food preferences
                preferences = {}
                for food_col in food_columns:
                    if food_col in row and not pd.isna(row[food_col]):
                        try:
                            pref_value = int(row[food_col])
                            if 1 <= pref_value <= 5:
                                preferences[food_col] = pref_value
                        except (ValueError, TypeError):
                            pass
                
                friend = Friend(name, preferences, intimacy, dietary_restrictions)
                
                existing = self.friend_repo.get_by_name(name)
                if existing:
                    if update_existing:
                        self.friend_repo.update(friend)
                        stats['updated'] += 1
                    else:
                        stats['errors'].append(f"Row {idx+2}: '{name}' already exists (skipped)")
                        stats['failed'] += 1
                else:
                    self.friend_repo.add(friend)
                    stats['successful'] += 1
                
            except Exception as e:
                stats['errors'].append(f"Row {idx+2}: {str(e)}")
                stats['failed'] += 1
        
        return stats
    
    def export_friends_to_csv(self, filename: str, include_stats: bool = False) -> int:
        """Export friends to CSV."""
        friends = self.friend_repo.get_all()
        if not friends:
            return 0
        
        all_foods = set()
        for friend in friends:
            all_foods.update(friend.preferences.keys())
        all_foods.update(self.available_foods)
        food_columns = sorted(all_foods)
        
        data = []
        for friend in friends:
            row = {
                'Name': friend.name,
                'Intimacy': friend.intimacy,
                'Dietary_Restrictions': ';'.join(friend.dietary_restrictions) if friend.dietary_restrictions else ''
            }
            
            for food in food_columns:
                row[food] = friend.preferences.get(food, '')
            
            if include_stats:
                row['Total_Preferences'] = len(friend.preferences)
                row['Avg_Preference'] = np.mean(list(friend.preferences.values())) if friend.preferences else 0
            
            data.append(row)
        
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False, encoding=CSV_ENCODING)
        return len(friends)
    
    def get_csv_template(self, filename: str = "friends_template.csv") -> str:
        """Generate CSV template."""
        food_columns = sorted(self.available_foods)
        
        template_data = {
            'Name': ['Alice Johnson', 'Bob Smith', 'Carol Davis'],
            'Intimacy': [8, 7, 9],
            'Dietary_Restrictions': ['vegetarian', '', 'vegan;gluten-free']
        }
        
        for i, food in enumerate(food_columns):
            template_data[food] = [5, 4, 3] if i < 3 else ['', '', '']
        
        df = pd.DataFrame(template_data)
        df.to_csv(filename, index=False, encoding=CSV_ENCODING)
        return filename
    
    def validate_csv_format(self, filename: str) -> Tuple[bool, str]:
        """Validate CSV format."""
        try:
            df = pd.read_csv(filename, nrows=5, encoding=CSV_ENCODING)
            
            required_cols = ['Name', 'Intimacy']
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if missing_cols:
                return False, f"Missing required columns: {missing_cols}"
            
            if not pd.api.types.is_numeric_dtype(df['Intimacy']):
                return False, "Intimacy column must contain numeric values"
            
            if df.empty:
                return False, "CSV file contains no data rows"
            
            return True, f"CSV format is valid ({len(df)} sample rows checked)"
            
        except FileNotFoundError:
            return False, f"File not found: {filename}"
        except pd.errors.EmptyDataError:
            return False, "CSV file is empty"
        except Exception as e:
            return False, f"Error validating CSV: {str(e)}"
    
    def analyze_friend_data(self) -> pd.DataFrame:
        """Get friend statistics DataFrame."""
        friends = self.friend_repo.get_all()
        if not friends:
            return pd.DataFrame()
        
        data = []
        for friend in friends:
            prefs = list(friend.preferences.values())
            data.append({
                'Name': friend.name,
                'Intimacy': friend.intimacy,
                'Num_Preferences': len(prefs),
                'Avg_Preference': np.mean(prefs) if prefs else 0,
                'Max_Preference': max(prefs) if prefs else 0,
                'Min_Preference': min(prefs) if prefs else 0,
            })
        
        df = pd.DataFrame(data)
        return df.sort_values('Intimacy', ascending=False)
    
    def get_food_popularity(self) -> pd.DataFrame:
        """Get food popularity statistics."""
        friends = self.friend_repo.get_all()
        if not friends:
            return pd.DataFrame()
        
        food_prefs = {}
        for friend in friends:
            for food, rating in friend.preferences.items():
                if food not in food_prefs:
                    food_prefs[food] = []
                food_prefs[food].append(rating)
        
        data = []
        for food, ratings in food_prefs.items():
            data.append({
                'Food': food,
                'Avg_Rating': np.mean(ratings),
                'Median_Rating': np.median(ratings),
                'Num_Ratings': len(ratings)
            })
        
        df = pd.DataFrame(data)
        return df.sort_values('Avg_Rating', ascending=False)