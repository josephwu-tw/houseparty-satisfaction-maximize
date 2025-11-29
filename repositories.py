"""
Data access layer for persistent storage.
"""
import json
from typing import List, Optional
from pathlib import Path
from models import Friend, Food
from config import DATA_DIR, FRIENDS_FILE, FOODS_FILE


class BaseRepository:
    """Base repository for file operations."""
    
    def __init__(self, data_dir: str = None):
        self.data_dir = Path(data_dir) if data_dir else DATA_DIR
        self.data_dir.mkdir(exist_ok=True)
    
    def _get_file_path(self, filename: str) -> Path:
        """Get full file path."""
        return self.data_dir / filename
    
    def _load_json(self, filename: str) -> dict:
        """Load JSON file."""
        file_path = self._get_file_path(filename)
        if not file_path.exists():
            return {}
        with open(file_path, 'r') as f:
            return json.load(f)
    
    def _save_json(self, data: dict, filename: str):
        """Save JSON file."""
        file_path = self._get_file_path(filename)
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)


class FriendRepository(BaseRepository):
    """Repository for friend data."""
    
    def __init__(self, data_dir: str = None):
        super().__init__(data_dir)
        self.friends: List[Friend] = []
        self.load_all()
    
    def load_all(self) -> List[Friend]:
        """Load all friends."""
        data = self._load_json(FRIENDS_FILE)
        self.friends = [Friend.from_dict(f) for f in data.get('friends', [])]
        return self.friends
    
    def save_all(self):
        """Save all friends."""
        data = {'friends': [f.to_dict() for f in self.friends]}
        self._save_json(data, FRIENDS_FILE)
    
    def add(self, friend: Friend) -> Friend:
        """Add new friend."""
        if self.get_by_name(friend.name):
            from config import get_error_message
            raise ValueError(get_error_message('duplicate_name', name=friend.name))
        self.friends.append(friend)
        self.save_all()
        return friend
    
    def get_by_name(self, name: str) -> Optional[Friend]:
        """Get friend by name."""
        for friend in self.friends:
            if friend.name.lower() == name.lower():
                return friend
        return None
    
    def get_all(self) -> List[Friend]:
        """Get all friends."""
        return self.friends.copy()
    
    def update(self, friend: Friend) -> Friend:
        """Update existing friend."""
        for i, existing in enumerate(self.friends):
            if existing.name.lower() == friend.name.lower():
                self.friends[i] = friend
                self.save_all()
                return friend
        raise ValueError(f"Friend '{friend.name}' not found")
    
    def delete(self, name: str) -> bool:
        """Delete friend."""
        for i, friend in enumerate(self.friends):
            if friend.name.lower() == name.lower():
                self.friends.pop(i)
                self.save_all()
                return True
        return False
    
    def count(self) -> int:
        """Count friends."""
        return len(self.friends)
    
    def clear_all(self) -> int:
        """Clear all friends. Returns count of deleted friends."""
        count = len(self.friends)
        self.friends = []
        self.save_all()
        return count


class FoodRepository(BaseRepository):
    """Repository for food data."""
    
    def __init__(self, data_dir: str = None):
        super().__init__(data_dir)
        self.foods: List[Food] = []
        self.load_all()
    
    def load_all(self) -> List[Food]:
        """Load all foods."""
        data = self._load_json(FOODS_FILE)
        self.foods = [Food.from_dict(f) for f in data.get('foods', [])]
        return self.foods
    
    def save_all(self):
        """Save all foods."""
        data = {'foods': [f.to_dict() for f in self.foods]}
        self._save_json(data, FOODS_FILE)
    
    def add(self, food: Food) -> Food:
        """Add new food."""
        if self.get_by_name(food.name):
            raise ValueError(f"Food '{food.name}' already exists")
        self.foods.append(food)
        self.save_all()
        return food
    
    def get_by_name(self, name: str) -> Optional[Food]:
        """Get food by name."""
        for food in self.foods:
            if food.name.lower() == name.lower():
                return food
        return None
    
    def get_all(self) -> List[Food]:
        """Get all foods."""
        return self.foods.copy()
    
    def get_by_category(self, category: str) -> List[Food]:
        """Get foods by category."""
        return [f for f in self.foods if f.category.lower() == category.lower()]
    
    def update(self, food: Food) -> Food:
        """Update existing food."""
        for i, existing in enumerate(self.foods):
            if existing.name.lower() == food.name.lower():
                self.foods[i] = food
                self.save_all()
                return food
        raise ValueError(f"Food '{food.name}' not found")
    
    def delete(self, name: str) -> bool:
        """Delete food."""
        for i, food in enumerate(self.foods):
            if food.name.lower() == name.lower():
                self.foods.pop(i)
                self.save_all()
                return True
        return False
    
    def count(self) -> int:
        """Count foods."""
        return len(self.foods)
    
    def clear_all(self) -> int:
        """Clear all foods. Returns count of deleted foods."""
        count = len(self.foods)
        self.foods = []
        self.save_all()
        return count