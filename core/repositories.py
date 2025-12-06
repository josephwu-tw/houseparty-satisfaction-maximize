"""
Data persistence layer.
"""
import json
from typing import List, Optional
from pathlib import Path
from .models import Friend, Food
from .config import DATA_DIR, FRIENDS_FILE, FOODS_FILE, get_error_message


class BaseRepository:
    """Base repository for JSON file operations."""
    
    def __init__(self, data_dir: Path = None):
        self.data_dir = data_dir or DATA_DIR
        self.data_dir.mkdir(exist_ok=True)
    
    def _load_json(self, filename: str) -> dict:
        path = self.data_dir / filename
        if not path.exists():
            return {}
        with open(path, 'r') as f:
            return json.load(f)
    
    def _save_json(self, data: dict, filename: str):
        with open(self.data_dir / filename, 'w') as f:
            json.dump(data, f, indent=2)


class FriendRepository(BaseRepository):
    """Repository for friend data."""
    
    def __init__(self, data_dir: Path = None):
        super().__init__(data_dir)
        self.friends: List[Friend] = []
        self.load_all()
    
    def load_all(self) -> List[Friend]:
        data = self._load_json(FRIENDS_FILE)
        self.friends = [Friend.from_dict(f) for f in data.get('friends', [])]
        return self.friends
    
    def save_all(self):
        self._save_json({'friends': [f.to_dict() for f in self.friends]}, FRIENDS_FILE)
    
    def add(self, friend: Friend) -> Friend:
        if self.get_by_name(friend.name):
            raise ValueError(get_error_message('duplicate_name', name=friend.name))
        self.friends.append(friend)
        self.save_all()
        return friend
    
    def get_by_name(self, name: str) -> Optional[Friend]:
        return next((f for f in self.friends if f.name.lower() == name.lower()), None)
    
    def get_all(self) -> List[Friend]:
        return self.friends.copy()
    
    def update(self, friend: Friend) -> Friend:
        for i, f in enumerate(self.friends):
            if f.name.lower() == friend.name.lower():
                self.friends[i] = friend
                self.save_all()
                return friend
        raise ValueError(f"Friend '{friend.name}' not found")
    
    def delete(self, name: str) -> bool:
        for i, f in enumerate(self.friends):
            if f.name.lower() == name.lower():
                self.friends.pop(i)
                self.save_all()
                return True
        return False
    
    def count(self) -> int:
        return len(self.friends)
    
    def clear_all(self) -> int:
        count = len(self.friends)
        self.friends = []
        self.save_all()
        return count


class FoodRepository(BaseRepository):
    """Repository for food data."""
    
    def __init__(self, data_dir: Path = None):
        super().__init__(data_dir)
        self.foods: List[Food] = []
        self.load_all()
    
    def load_all(self) -> List[Food]:
        data = self._load_json(FOODS_FILE)
        self.foods = [Food.from_dict(f) for f in data.get('foods', [])]
        return self.foods
    
    def save_all(self):
        self._save_json({'foods': [f.to_dict() for f in self.foods]}, FOODS_FILE)
    
    def add(self, food: Food) -> Food:
        if self.get_by_name(food.name):
            raise ValueError(f"Food '{food.name}' already exists")
        self.foods.append(food)
        self.save_all()
        return food
    
    def get_by_name(self, name: str) -> Optional[Food]:
        return next((f for f in self.foods if f.name.lower() == name.lower()), None)
    
    def get_all(self) -> List[Food]:
        return self.foods.copy()
    
    def get_by_category(self, category: str) -> List[Food]:
        return [f for f in self.foods if f.category.lower() == category.lower()]
    
    def update(self, food: Food) -> Food:
        for i, f in enumerate(self.foods):
            if f.name.lower() == food.name.lower():
                self.foods[i] = food
                self.save_all()
                return food
        raise ValueError(f"Food '{food.name}' not found")
    
    def delete(self, name: str) -> bool:
        for i, f in enumerate(self.foods):
            if f.name.lower() == name.lower():
                self.foods.pop(i)
                self.save_all()
                return True
        return False
    
    def count(self) -> int:
        return len(self.foods)
    
    def clear_all(self) -> int:
        count = len(self.foods)
        self.foods = []
        self.save_all()
        return count