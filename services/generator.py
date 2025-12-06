"""
Random friend data generator.
"""
import pandas as pd
import numpy as np
from typing import List, Optional
from core.config import (
    FIRST_NAMES, LAST_NAMES, DIETARY_OPTIONS, DEFAULT_FOODS,
    DEFAULT_INTIMACY_MEAN, DEFAULT_INTIMACY_STD,
    MIN_INTIMACY, MAX_INTIMACY, MIN_PREFERENCE, MAX_PREFERENCE
)


class FriendDataGenerator:
    """Generate random friend data using numpy."""
    
    def __init__(self, seed: Optional[int] = None):
        if seed is not None:
            np.random.seed(seed)
        self.used_names = set()
    
    def generate_name(self) -> str:
        """Generate unique random name."""
        for _ in range(1000):
            name = f"{np.random.choice(FIRST_NAMES)} {np.random.choice(LAST_NAMES)}"
            if name not in self.used_names:
                self.used_names.add(name)
                return name
        return f"{np.random.choice(FIRST_NAMES)} {np.random.choice(LAST_NAMES)} {np.random.randint(1, 9999)}"
    
    def generate_intimacy(self, mean: float = DEFAULT_INTIMACY_MEAN, std: float = DEFAULT_INTIMACY_STD) -> int:
        """Generate intimacy using normal distribution."""
        val = int(np.round(np.random.normal(mean, std)))
        return max(MIN_INTIMACY, min(MAX_INTIMACY, val))
    
    def generate_dietary_restriction(self) -> str:
        """Generate dietary restriction based on probabilities."""
        restrictions, probs = zip(*DIETARY_OPTIONS)
        return np.random.choice(restrictions, p=probs)
    
    def generate_preferences(self, foods: List[str], diversity: str = "realistic") -> dict:
        """Generate food preferences."""
        preferences = {}
        
        if diversity == "realistic":
            base = np.random.choice([3, 4], p=[0.6, 0.4])
            for food in foods:
                pref = base + np.random.randint(-2, 3)
                preferences[food] = max(MIN_PREFERENCE, min(MAX_PREFERENCE, pref))
        elif diversity == "low":
            base = np.random.randint(2, 5)
            for food in foods:
                preferences[food] = max(MIN_PREFERENCE, min(MAX_PREFERENCE, base + np.random.randint(-1, 2)))
        else:  # medium or high
            for food in foods:
                preferences[food] = np.random.randint(MIN_PREFERENCE, MAX_PREFERENCE + 1)
        
        return preferences
    
    def generate_batch(self, num_friends: int, foods: List[str],
                      diversity: str = "realistic", intimacy_dist: str = "normal") -> pd.DataFrame:
        """Generate batch of friends."""
        print(f"\n🎲 Generating {num_friends} random friends...")
        
        names = [self.generate_name() for _ in range(num_friends)]
        
        if intimacy_dist == "uniform":
            intimacies = np.random.randint(MIN_INTIMACY, MAX_INTIMACY + 1, size=num_friends)
        elif intimacy_dist == "bimodal":
            half = num_friends // 2
            intimacies = np.concatenate([
                np.random.randint(7, MAX_INTIMACY + 1, size=half),
                np.random.randint(MIN_INTIMACY, 5, size=num_friends - half)
            ])
            np.random.shuffle(intimacies)
        else:
            intimacies = [self.generate_intimacy() for _ in range(num_friends)]
        
        dietary = [self.generate_dietary_restriction() for _ in range(num_friends)]
        all_prefs = [self.generate_preferences(foods, diversity) for _ in range(num_friends)]
        
        data = {'Name': names, 'Intimacy': intimacies, 'Dietary_Restrictions': dietary}
        for food in foods:
            data[food] = [p[food] for p in all_prefs]
        
        df = pd.DataFrame(data)
        
        print(f"✓ Generated {len(df)} friends")
        print(f"\n📊 Statistics:")
        print(f"  Average Intimacy: {df['Intimacy'].mean():.1f}")
        print(f"  Intimacy Range: {df['Intimacy'].min()}-{df['Intimacy'].max()}")
        
        food_cols = [c for c in df.columns if c not in ['Name', 'Intimacy', 'Dietary_Restrictions']]
        print(f"  Average Preference: {df[food_cols].mean().mean():.2f}")
        
        return df