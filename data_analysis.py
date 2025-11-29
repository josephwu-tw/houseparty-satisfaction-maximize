"""
Data analysis and visualization using pandas/matplotlib.
"""
import pandas as pd
import numpy as np
from typing import Optional
from models import Friend, Food
from repositories import FriendRepository, FoodRepository
from config import PLOT_DPI, HEATMAP_COLORMAP

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
        for friend in friends:
            prefs = list(friend.preferences.values())
            data.append({
                'Name': friend.name,
                'Intimacy': friend.intimacy,
                'Num_Foods_Rated': len(prefs),
                'Avg_Preference': np.mean(prefs) if prefs else 0,
                'Max_Preference': max(prefs) if prefs else 0,
                'Min_Preference': min(prefs) if prefs else 0,
                'Restrictions': ', '.join(friend.dietary_restrictions) if friend.dietary_restrictions else 'None'
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
            ratings = [f.get_preference(food.name) for f in friends 
                      if f.get_preference(food.name) > 0]
            
            if ratings:
                weighted_sum = sum(f.get_preference(food.name) * f.intimacy 
                                 for f in friends if f.get_preference(food.name) > 0)
                total_intimacy = sum(f.intimacy for f in friends 
                                   if f.get_preference(food.name) > 0)
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
        
        all_foods = set()
        for friend in friends:
            all_foods.update(friend.preferences.keys())
        food_columns = sorted(all_foods)
        
        data = []
        for friend in friends:
            row = {'Friend': friend.name, 'Intimacy': friend.intimacy}
            for food in food_columns:
                row[food] = friend.get_preference(food) if friend.get_preference(food) > 0 else np.nan
            data.append(row)
        
        return pd.DataFrame(data).set_index('Friend')
    
    def get_food_popularity(self) -> pd.DataFrame:
        """Get food popularity analysis."""
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
                'Std_Rating': np.std(ratings),
                'Num_Ratings': len(ratings)
            })
        
        return pd.DataFrame(data).sort_values('Avg_Rating', ascending=False)
    
    def generate_text_report(self) -> str:
        """Generate comprehensive text report."""
        report = []
        report.append("="*70)
        report.append("PARTY PLANNING DATA ANALYSIS REPORT")
        report.append("="*70)
        
        # Friend summary
        friend_df = self.get_friend_summary_df()
        if not friend_df.empty:
            report.append("\n📊 FRIEND STATISTICS")
            report.append("-"*70)
            report.append(f"Total Friends: {len(friend_df)}")
            report.append(f"Average Intimacy: {friend_df['Intimacy'].mean():.2f}")
            report.append(f"Intimacy Range: {friend_df['Intimacy'].min()}-{friend_df['Intimacy'].max()}")
            
            report.append("\nTop 5 Closest Friends:")
            for _, row in friend_df.head(5).iterrows():
                report.append(f"  • {row['Name']} (Intimacy: {row['Intimacy']}, "
                            f"Avg Preference: {row['Avg_Preference']:.2f})")
        
        # Food analysis
        food_df = self.get_food_analysis_df()
        if not food_df.empty:
            report.append("\n🍕 FOOD STATISTICS")
            report.append("-"*70)
            report.append(f"Total Foods: {len(food_df)}")
            report.append(f"Average Cost: ${food_df['Cost'].mean():.2f}")
            
            report.append("\nMost Popular Foods:")
            for _, row in food_df.head(5).iterrows():
                report.append(f"  • {row['Food']}: {row['Avg_Rating']:.2f}/5 "
                            f"(${row['Cost']:.2f}, {row['Num_Ratings']} ratings)")
        
        report.append("\n" + "="*70)
        return "\n".join(report)
    
    def plot_intimacy_distribution(self, save_path: Optional[str] = None):
        """Plot intimacy distribution."""
        if not PLOTTING_AVAILABLE:
            print("⚠️  Matplotlib not available. Install: pip install matplotlib seaborn")
            return
        
        friend_df = self.get_friend_summary_df()
        if friend_df.empty:
            print("⚠️  No friend data available")
            return
        
        plt.figure(figsize=(10, 6))
        sns.histplot(data=friend_df, x='Intimacy', bins=10, kde=True)
        plt.title('Distribution of Friend Intimacy Levels', fontsize=14, fontweight='bold')
        plt.xlabel('Intimacy Level')
        plt.ylabel('Number of Friends')
        plt.grid(True, alpha=0.3)
        
        if save_path:
            plt.savefig(save_path, dpi=PLOT_DPI, bbox_inches='tight')
            print(f"✓ Saved plot to {save_path}")
        else:
            plt.show()
        plt.close()
    
    def plot_food_analysis(self, save_path: Optional[str] = None):
        """Plot food rating vs cost."""
        if not PLOTTING_AVAILABLE:
            print("⚠️  Matplotlib not available")
            return
        
        food_df = self.get_food_analysis_df()
        if food_df.empty:
            print("⚠️  No food data available")
            return
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Scatter plot
        scatter = ax1.scatter(food_df['Cost'], food_df['Avg_Rating'], 
                            s=food_df['Num_Ratings']*20, alpha=0.6, 
                            c=food_df['Popularity_Score'], cmap='viridis')
        ax1.set_xlabel('Cost ($)')
        ax1.set_ylabel('Average Rating')
        ax1.set_title('Food Rating vs Cost')
        ax1.grid(True, alpha=0.3)
        
        for _, row in food_df.iterrows():
            ax1.annotate(row['Food'], (row['Cost'], row['Avg_Rating']), 
                        fontsize=8, alpha=0.7)
        
        plt.colorbar(scatter, ax=ax1, label='Popularity Score')
        
        # Bar plot
        category_avg = food_df.groupby('Category')['Avg_Rating'].mean().sort_values(ascending=False)
        category_avg.plot(kind='bar', ax=ax2, color='skyblue')
        ax2.set_xlabel('Category')
        ax2.set_ylabel('Average Rating')
        ax2.set_title('Average Rating by Category')
        ax2.grid(True, alpha=0.3, axis='y')
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=PLOT_DPI, bbox_inches='tight')
            print(f"✓ Saved plot to {save_path}")
        else:
            plt.show()
        plt.close()
    
    def plot_preference_heatmap(self, save_path: Optional[str] = None):
        """Plot preference heatmap."""
        if not PLOTTING_AVAILABLE:
            print("⚠️  Matplotlib not available")
            return
        
        matrix = self.get_preference_matrix()
        if matrix.empty:
            print("⚠️  No preference data available")
            return
        
        plot_data = matrix.drop('Intimacy', axis=1, errors='ignore')
        
        plt.figure(figsize=(12, 8))
        sns.heatmap(plot_data, annot=True, fmt='.0f', cmap=HEATMAP_COLORMAP, 
                   cbar_kws={'label': 'Preference Rating'}, 
                   linewidths=0.5, linecolor='gray')
        plt.title('Friend-Food Preference Matrix', fontsize=14, fontweight='bold')
        plt.xlabel('Food Items')
        plt.ylabel('Friends')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=PLOT_DPI, bbox_inches='tight')
            print(f"✓ Saved heatmap to {save_path}")
        else:
            plt.show()
        plt.close()