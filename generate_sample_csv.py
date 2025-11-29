"""
Random friend data generator using pandas and numpy.
"""
import pandas as pd
import numpy as np
import argparse
from pathlib import Path
from typing import List, Optional
from config import (
    FIRST_NAMES, LAST_NAMES, DIETARY_OPTIONS, DEFAULT_FOODS,
    DEFAULT_INTIMACY_MEAN, DEFAULT_INTIMACY_STD,
    INTIMACY_DISTRIBUTIONS, DIVERSITY_LEVELS,
    MIN_INTIMACY, MAX_INTIMACY, MIN_PREFERENCE, MAX_PREFERENCE,
    MIN_FRIENDS_GENERATE, MAX_FRIENDS_GENERATE, CSV_ENCODING, DISPLAY_WIDTH,
    EXPORT_DIR
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
            first = np.random.choice(FIRST_NAMES)
            last = np.random.choice(LAST_NAMES)
            name = f"{first} {last}"
            if name not in self.used_names:
                self.used_names.add(name)
                return name
        return f"{np.random.choice(FIRST_NAMES)} {np.random.choice(LAST_NAMES)} {np.random.randint(1, 9999)}"
    
    def generate_intimacy(self, mean: float = DEFAULT_INTIMACY_MEAN, 
                         std: float = DEFAULT_INTIMACY_STD) -> int:
        """Generate intimacy level using normal distribution."""
        intimacy = int(np.round(np.random.normal(mean, std)))
        return max(MIN_INTIMACY, min(MAX_INTIMACY, intimacy))
    
    def generate_dietary_restriction(self) -> str:
        """Generate dietary restriction based on probabilities."""
        restrictions, probs = zip(*DIETARY_OPTIONS)
        return np.random.choice(restrictions, p=probs)
    
    def generate_preferences(self, foods: List[str], diversity: str = "medium",
                           personality: Optional[str] = None) -> dict:
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
        elif diversity == "medium":
            for food in foods:
                preferences[food] = np.random.randint(MIN_PREFERENCE, MAX_PREFERENCE + 1)
        else:  # high
            for food in foods:
                preferences[food] = np.random.randint(MIN_PREFERENCE, MAX_PREFERENCE + 1)
        
        # Apply personality
        if personality == "picky":
            for food in foods:
                if preferences[food] >= 4:
                    preferences[food] = MAX_PREFERENCE
                elif preferences[food] <= 2:
                    preferences[food] = MIN_PREFERENCE
        elif personality == "adventurous":
            for food in foods:
                preferences[food] = min(MAX_PREFERENCE, preferences[food] + 1)
        
        return preferences
    
    def generate_batch(self, num_friends: int, foods: List[str],
                      diversity: str = "realistic",
                      intimacy_dist: str = "normal") -> pd.DataFrame:
        """Generate batch of friends efficiently."""
        print(f"\n🎲 Generating {num_friends} random friends...")
        
        names = [self.generate_name() for _ in range(num_friends)]
        
        # Generate intimacy levels
        if intimacy_dist == "uniform":
            intimacies = np.random.randint(MIN_INTIMACY, MAX_INTIMACY + 1, size=num_friends)
        elif intimacy_dist == "bimodal":
            intimacies = np.concatenate([
                np.random.randint(7, MAX_INTIMACY + 1, size=num_friends//2),
                np.random.randint(MIN_INTIMACY, 5, size=num_friends - num_friends//2)
            ])
            np.random.shuffle(intimacies)
        else:  # normal
            intimacies = [self.generate_intimacy() for _ in range(num_friends)]
        
        dietary_restrictions = [self.generate_dietary_restriction() for _ in range(num_friends)]
        
        # Generate preferences
        all_preferences = []
        for i in range(num_friends):
            personality = "picky" if i % 10 == 0 else "adventurous" if i % 7 == 0 else None
            prefs = self.generate_preferences(foods, diversity, personality)
            all_preferences.append(prefs)
        
        # Build DataFrame
        data = {
            'Name': names,
            'Intimacy': intimacies,
            'Dietary_Restrictions': dietary_restrictions
        }
        
        for food in foods:
            data[food] = [prefs[food] for prefs in all_preferences]
        
        df = pd.DataFrame(data)
        
        # Display summary
        print(f"✓ Generated {len(df)} friends")
        print(f"\n📊 Quick Statistics:")
        print(f"  Average Intimacy: {df['Intimacy'].mean():.1f}")
        print(f"  Intimacy Range: {df['Intimacy'].min()}-{df['Intimacy'].max()}")
        
        food_cols = [col for col in df.columns if col not in ['Name', 'Intimacy', 'Dietary_Restrictions']]
        avg_prefs = df[food_cols].mean().mean()
        print(f"  Average Food Preference: {avg_prefs:.2f}")
        
        return df


def interactive_mode():
    """Interactive CLI for generating friend data."""
    print("="*DISPLAY_WIDTH)
    print("🎉 INTERACTIVE FRIEND DATA GENERATOR 🎉".center(DISPLAY_WIDTH))
    print("="*DISPLAY_WIDTH)
    print("\nGenerate random friend data for Party Optimizer\n")
    
    # Get inputs
    try:
        num_friends = int(input(f"How many friends? ({MIN_FRIENDS_GENERATE}-{MAX_FRIENDS_GENERATE}): ").strip())
        if not MIN_FRIENDS_GENERATE <= num_friends <= MAX_FRIENDS_GENERATE:
            print(f"❌ Enter a number between {MIN_FRIENDS_GENERATE}-{MAX_FRIENDS_GENERATE}")
            return
    except ValueError:
        print("❌ Invalid number")
        return
    
    # Diversity
    print("\nPreference Diversity:")
    for i, level in enumerate(DIVERSITY_LEVELS, 1):
        print(f"  {i}. {level.capitalize()}")
    diversity_choice = input(f"Choose (1-{len(DIVERSITY_LEVELS)}) [default: 4]: ").strip() or "4"
    diversity_map = {str(i+1): level for i, level in enumerate(DIVERSITY_LEVELS)}
    diversity = diversity_map.get(diversity_choice, "realistic")
    
    # Intimacy distribution
    print("\nIntimacy Distribution:")
    for i, dist in enumerate(INTIMACY_DISTRIBUTIONS, 1):
        print(f"  {i}. {dist.capitalize()}")
    intimacy_choice = input(f"Choose (1-{len(INTIMACY_DISTRIBUTIONS)}) [default: 1]: ").strip() or "1"
    intimacy_map = {str(i+1): dist for i, dist in enumerate(INTIMACY_DISTRIBUTIONS)}
    intimacy_dist = intimacy_map.get(intimacy_choice, "normal")
    
    # Custom foods
    use_custom = input("\nUse custom food items? (y/n) [default: n]: ").strip().lower()
    if use_custom == 'y':
        foods_input = input("Enter food names (comma-separated): ").strip()
        foods = [f.strip() for f in foods_input.split(',') if f.strip()]
        if not foods:
            print("⚠️  Using defaults")
            foods = DEFAULT_FOODS.copy()
    else:
        foods = DEFAULT_FOODS.copy()
    
    # Random seed
    use_seed = input("\nUse random seed? (y/n) [default: n]: ").strip().lower()
    seed = None
    if use_seed == 'y':
        try:
            seed = int(input("Enter seed: ").strip())
        except ValueError:
            print("⚠️  Invalid seed, using random")
    
    # Filename
    default_filename = f"friends_{num_friends}.csv"
    filename = input(f"\nOutput filename [default: {default_filename}]: ").strip()
    filename = filename if filename else default_filename
    
    # Generate
    print("\n" + "="*DISPLAY_WIDTH)
    generator = FriendDataGenerator(seed=seed)
    df = generator.generate_batch(num_friends, foods, diversity, intimacy_dist)
    
    # Save to exports directory
    filepath = EXPORT_DIR / filename
    df.to_csv(filepath, index=False, encoding=CSV_ENCODING)
    print(f"\n✓ Saved to: {filepath}")
    print(f"  File size: {filepath.stat().st_size / 1024:.1f} KB")
    
    # Preview
    show_preview = input("\nShow preview? (y/n) [default: y]: ").strip().lower()
    if show_preview != 'n':
        print("\n📋 Preview:")
        print(df.head().to_string(index=False))
    
    print("\n" + "="*DISPLAY_WIDTH)
    print(f"✨ Import in main app: Manage Friends → Import from CSV → {filepath}")
    print("="*DISPLAY_WIDTH)


def main():
    """Command line interface."""
    parser = argparse.ArgumentParser(description="Generate sample friend CSV files")
    parser.add_argument('-i', '--interactive', action='store_true', help='Interactive mode')
    parser.add_argument('-n', '--num-friends', type=int, help='Number of friends')
    parser.add_argument('-o', '--output', default='sample_friends.csv', help='Output file')
    parser.add_argument('-d', '--diversity', choices=DIVERSITY_LEVELS, default='realistic')
    parser.add_argument('--intimacy', choices=INTIMACY_DISTRIBUTIONS, default='normal')
    parser.add_argument('-s', '--seed', type=int, help='Random seed')
    parser.add_argument('--foods', nargs='+', help='Custom food items')
    
    args = parser.parse_args()
    
    if args.interactive or args.num_friends is None:
        interactive_mode()
    else:
        foods = args.foods if args.foods else DEFAULT_FOODS
        
        print("="*DISPLAY_WIDTH)
        print("Friend Data Generator".center(DISPLAY_WIDTH))
        print("="*DISPLAY_WIDTH)
        
        generator = FriendDataGenerator(seed=args.seed)
        df = generator.generate_batch(args.num_friends, foods, args.diversity, args.intimacy)
        
        filepath = EXPORT_DIR / args.output
        df.to_csv(filepath, index=False, encoding=CSV_ENCODING)
        print(f"\n✓ Saved to: {filepath}")
        print("\nPreview:")
        print(df.head().to_string(index=False))
        print("="*DISPLAY_WIDTH)


if __name__ == "__main__":
    main()