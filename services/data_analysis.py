"""
Data analysis and visualization.
"""
import pandas as pd
import numpy as np
from typing import Optional
from core.repositories import FriendRepository, FoodRepository
from core.config import PLOT_DPI, HEATMAP_COLORMAP

try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    PLOTTING_AVAILABLE = True
except ImportError:
    PLOTTING_AVAILABLE = False


class PartyDataAnalyzer:
    """Data analysis using pandas."""
    
    def __init__(self, friend_repo: FriendRepository, food_repo: FoodRepository):
        self.friend_repo = friend_repo
        self.food_repo = food_repo
    
    def get_friend_summary_df(self) -> pd.DataFrame:
        """Get friend summary DataFrame."""
        friends = self.friend_repo.get_all()
        if not friends:
            return pd.DataFrame()
        
        data = []
        for f in friends:
            prefs = list(f.preferences.values())
            data.append({
                'Name': f.name,
                'Intimacy': f.intimacy,
                'Num_Foods_Rated': len(prefs),
                'Avg_Preference': np.mean(prefs) if prefs else 0,
                'Restrictions': ', '.join(f.dietary_restrictions) if f.dietary_restrictions else 'None'
            })
        
        return pd.DataFrame(data).sort_values('Intimacy', ascending=False)
    
    def get_food_analysis_df(self) -> pd.DataFrame:
        """Get food analysis DataFrame."""
        friends = self.friend_repo.get_all()
        foods = self.food_repo.get_all()
        
        if not friends or not foods:
            return pd.DataFrame()
        
        data = []
        for food in foods:
            ratings = [f.get_preference(food.name) for f in friends if f.get_preference(food.name) > 0]
            
            if ratings:
                weighted_sum = sum(f.get_preference(food.name) * f.intimacy for f in friends if f.get_preference(food.name) > 0)
                total_intimacy = sum(f.intimacy for f in friends if f.get_preference(food.name) > 0)
                weighted_avg = weighted_sum / total_intimacy if total_intimacy > 0 else 0
                
                data.append({
                    'Food': food.name,
                    'Cost': food.cost,
                    'Category': food.category,
                    'Avg_Rating': np.mean(ratings),
                    'Weighted_Avg': weighted_avg,
                    'Num_Ratings': len(ratings),
                    'Popularity_Score': len(ratings) * np.mean(ratings),
                    'Value_Score': weighted_avg / food.cost if food.cost > 0 else 0
                })
        
        return pd.DataFrame(data).sort_values('Popularity_Score', ascending=False)
    
    def get_preference_matrix(self) -> pd.DataFrame:
        """Create friend-food preference matrix."""
        friends = self.friend_repo.get_all()
        if not friends:
            return pd.DataFrame()
        
        all_foods = sorted(set(f for friend in friends for f in friend.preferences.keys()))
        
        data = []
        for friend in friends:
            row = {'Friend': friend.name, 'Intimacy': friend.intimacy}
            for food in all_foods:
                row[food] = friend.get_preference(food) or np.nan
            data.append(row)
        
        return pd.DataFrame(data).set_index('Friend')
    
    def get_food_popularity(self) -> pd.DataFrame:
        """Get food popularity statistics."""
        friends = self.friend_repo.get_all()
        if not friends:
            return pd.DataFrame()
        
        food_prefs = {}
        for friend in friends:
            for food, rating in friend.preferences.items():
                food_prefs.setdefault(food, []).append(rating)
        
        data = [{'Food': f, 'Avg_Rating': np.mean(r), 'Num_Ratings': len(r)} for f, r in food_prefs.items()]
        return pd.DataFrame(data).sort_values('Avg_Rating', ascending=False)
    
    def generate_text_report(self) -> str:
        """Generate text report."""
        lines = ["=" * 70, "PARTY PLANNING DATA ANALYSIS REPORT", "=" * 70]
        
        friend_df = self.get_friend_summary_df()
        if not friend_df.empty:
            lines.extend(["\n📊 FRIEND STATISTICS", "-" * 70])
            lines.append(f"Total Friends: {len(friend_df)}")
            lines.append(f"Average Intimacy: {friend_df['Intimacy'].mean():.2f}")
            lines.append("\nTop 5 Closest Friends:")
            for _, row in friend_df.head(5).iterrows():
                lines.append(f"  • {row['Name']} (Intimacy: {row['Intimacy']})")
        
        food_df = self.get_food_analysis_df()
        if not food_df.empty:
            lines.extend(["\n🍕 FOOD STATISTICS", "-" * 70])
            lines.append(f"Total Foods: {len(food_df)}")
            lines.append(f"Average Cost: ${food_df['Cost'].mean():.2f}")
            lines.append("\nMost Popular Foods:")
            for _, row in food_df.head(5).iterrows():
                lines.append(f"  • {row['Food']}: {row['Avg_Rating']:.2f}/5 (${row['Cost']:.2f})")
        
        lines.append("\n" + "=" * 70)
        return "\n".join(lines)
    
    def plot_intimacy_distribution(self, save_path: Optional[str] = None):
        """Plot intimacy distribution."""
        if not PLOTTING_AVAILABLE:
            print("⚠️ Matplotlib not available")
            return
        
        df = self.get_friend_summary_df()
        if df.empty:
            print("⚠️ No data")
            return
        
        plt.figure(figsize=(10, 6))
        sns.histplot(data=df, x='Intimacy', bins=10, kde=True)
        plt.title('Distribution of Friend Intimacy Levels')
        plt.xlabel('Intimacy Level')
        plt.ylabel('Count')
        
        if save_path:
            plt.savefig(save_path, dpi=PLOT_DPI, bbox_inches='tight')
            print(f"✓ Saved to {save_path}")
        else:
            plt.show()
        plt.close()
    
    def plot_food_analysis(self, save_path: Optional[str] = None):
        """Plot food analysis."""
        if not PLOTTING_AVAILABLE:
            print("⚠️ Matplotlib not available")
            return
        
        df = self.get_food_analysis_df()
        if df.empty:
            print("⚠️ No data")
            return
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        ax1.scatter(df['Cost'], df['Avg_Rating'], s=df['Num_Ratings'] * 20, alpha=0.6)
        for _, row in df.iterrows():
            ax1.annotate(row['Food'], (row['Cost'], row['Avg_Rating']), fontsize=8)
        ax1.set_xlabel('Cost ($)')
        ax1.set_ylabel('Rating')
        ax1.set_title('Rating vs Cost')
        
        df.groupby('Category')['Avg_Rating'].mean().plot(kind='bar', ax=ax2, color='skyblue')
        ax2.set_title('Rating by Category')
        ax2.set_ylabel('Avg Rating')
        
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=PLOT_DPI, bbox_inches='tight')
            print(f"✓ Saved to {save_path}")
        else:
            plt.show()
        plt.close()
    
    def plot_preference_heatmap(self, save_path: Optional[str] = None):
        """Plot preference heatmap."""
        if not PLOTTING_AVAILABLE:
            print("⚠️ Matplotlib not available")
            return
        
        matrix = self.get_preference_matrix()
        if matrix.empty:
            print("⚠️ No data")
            return
        
        plot_data = matrix.drop('Intimacy', axis=1, errors='ignore')
        
        plt.figure(figsize=(12, 8))
        sns.heatmap(plot_data, annot=True, fmt='.0f', cmap=HEATMAP_COLORMAP, linewidths=0.5)
        plt.title('Friend-Food Preference Matrix')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=PLOT_DPI, bbox_inches='tight')
            print(f"✓ Saved to {save_path}")
        else:
            plt.show()
        plt.close()