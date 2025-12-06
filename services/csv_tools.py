"""
CSV import/export operations.
"""
import pandas as pd
import numpy as np
from typing import Dict, Tuple
from pathlib import Path
from core.models import Friend
from core.repositories import FriendRepository, FoodRepository
from core.config import CSV_ENCODING


class CSVImporter:
    """CSV import/export with pandas."""
    
    def __init__(self, friend_repo: FriendRepository, food_repo: FoodRepository):
        self.friend_repo = friend_repo
        self.food_repo = food_repo
        self.available_foods = [f.name for f in food_repo.get_all()]
    
    def import_friends_from_csv(self, filename: str, update_existing: bool = True) -> Dict:
        """Import friends from CSV file."""
        if not Path(filename).exists():
            raise FileNotFoundError(f"CSV file not found: {filename}")
        
        df = pd.read_csv(filename, encoding=CSV_ENCODING)
        
        required = ['Name', 'Intimacy']
        missing = [c for c in required if c not in df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
        
        stats = {'total_rows': len(df), 'successful': 0, 'updated': 0, 'failed': 0, 'errors': []}
        food_cols = [c for c in df.columns if c not in ['Name', 'Intimacy', 'Dietary_Restrictions']]
        
        for idx, row in df.iterrows():
            try:
                name = str(row['Name']).strip()
                if not name or pd.isna(row['Name']):
                    stats['errors'].append(f"Row {idx+2}: Missing name")
                    stats['failed'] += 1
                    continue
                
                intimacy = int(row['Intimacy'])
                if not 1 <= intimacy <= 10:
                    stats['errors'].append(f"Row {idx+2} ({name}): Invalid intimacy")
                    stats['failed'] += 1
                    continue
                
                dietary = []
                if 'Dietary_Restrictions' in df.columns and not pd.isna(row['Dietary_Restrictions']):
                    dietary = [r.strip() for r in str(row['Dietary_Restrictions']).split(';') if r.strip()]
                
                preferences = {}
                for col in food_cols:
                    if col in row and not pd.isna(row[col]):
                        try:
                            val = int(row[col])
                            if 1 <= val <= 5:
                                preferences[col] = val
                        except (ValueError, TypeError):
                            pass
                
                friend = Friend(name, preferences, intimacy, dietary)
                existing = self.friend_repo.get_by_name(name)
                
                if existing:
                    if update_existing:
                        self.friend_repo.update(friend)
                        stats['updated'] += 1
                    else:
                        stats['failed'] += 1
                else:
                    self.friend_repo.add(friend)
                    stats['successful'] += 1
                    
            except Exception as e:
                stats['errors'].append(f"Row {idx+2}: {e}")
                stats['failed'] += 1
        
        return stats
    
    def export_friends_to_csv(self, filename: str, include_stats: bool = False) -> int:
        """Export friends to CSV file."""
        friends = self.friend_repo.get_all()
        if not friends:
            return 0
        
        all_foods = set(self.available_foods)
        for f in friends:
            all_foods.update(f.preferences.keys())
        food_cols = sorted(all_foods)
        
        data = []
        for friend in friends:
            row = {
                'Name': friend.name,
                'Intimacy': friend.intimacy,
                'Dietary_Restrictions': ';'.join(friend.dietary_restrictions) if friend.dietary_restrictions else ''
            }
            for food in food_cols:
                row[food] = friend.preferences.get(food, '')
            
            if include_stats:
                prefs = list(friend.preferences.values())
                row['Avg_Preference'] = np.mean(prefs) if prefs else 0
            
            data.append(row)
        
        pd.DataFrame(data).to_csv(filename, index=False, encoding=CSV_ENCODING)
        return len(friends)
    
    def get_csv_template(self, filename: str) -> str:
        """Generate CSV template file."""
        food_cols = sorted(self.available_foods)
        
        data = {
            'Name': ['Alice Johnson', 'Bob Smith', 'Carol Davis'],
            'Intimacy': [8, 7, 9],
            'Dietary_Restrictions': ['vegetarian', '', 'vegan;gluten-free']
        }
        for i, food in enumerate(food_cols):
            data[food] = [5, 4, 3] if i < 3 else ['', '', '']
        
        pd.DataFrame(data).to_csv(filename, index=False, encoding=CSV_ENCODING)
        return filename
    
    def validate_csv_format(self, filename: str) -> Tuple[bool, str]:
        """Validate CSV file format."""
        try:
            df = pd.read_csv(filename, nrows=5, encoding=CSV_ENCODING)
            
            required = ['Name', 'Intimacy']
            missing = [c for c in required if c not in df.columns]
            if missing:
                return False, f"Missing required columns: {missing}"
            
            if not pd.api.types.is_numeric_dtype(df['Intimacy']):
                return False, "Intimacy column must be numeric"
            
            if df.empty:
                return False, "CSV file contains no data"
            
            return True, f"Valid CSV ({len(df)} rows checked)"
            
        except FileNotFoundError:
            return False, f"File not found: {filename}"
        except pd.errors.EmptyDataError:
            return False, "CSV file is empty"
        except Exception as e:
            return False, f"Error: {e}"