"""
Data analysis menu handler.
"""
from .base import BaseMenu
from core.config import EXPORT_DIR
from utils import print_section, wait_for_key


class AnalysisMenu(BaseMenu):
    """Handles data analysis and visualization."""
    
    def __init__(self, friend_repo, food_repo, analyzer):
        super().__init__(friend_repo, food_repo)
        self.analyzer = analyzer
    
    def display(self):
        print_section("DATA ANALYSIS")
        print("1. Text report\n2. Preference matrix\n3. Food popularity\n4. Visualizations\n0. Back")
    
    def handle_choice(self, choice: str) -> bool:
        actions = {'1': self.report, '2': self.matrix, '3': self.popularity, '4': self.visualize}
        if choice == '0':
            return False
        if choice in actions:
            actions[choice]()
        else:
            self.show_error("Invalid choice")
        return True
    
    def report(self):
        print_section("TEXT REPORT")
        report = self.analyzer.generate_text_report()
        print(report)
        
        if self.confirm("\nSave to file?"):
            filename = input("Filename [party_report.txt]: ").strip() or "party_report.txt"
            with open(EXPORT_DIR / filename, 'w') as f:
                f.write(report)
            print(f"✓ Saved to {EXPORT_DIR / filename}")
        wait_for_key()
    
    def matrix(self):
        print_section("PREFERENCE MATRIX")
        matrix = self.analyzer.get_preference_matrix()
        print(matrix.to_string() if not matrix.empty else "No data.")
        wait_for_key()
    
    def popularity(self):
        print_section("FOOD POPULARITY")
        df = self.analyzer.get_food_popularity()
        print(df.to_string(index=False) if not df.empty else "No data.")
        wait_for_key()
    
    def visualize(self):
        print_section("VISUALIZATIONS")
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            self.show_error("Install: pip install matplotlib seaborn")
            return
        
        print("1. Intimacy distribution\n2. Food analysis\n3. Preference heatmap\n4. All")
        choice = input("\nChoice: ").strip()
        save = self.confirm("Save to files?")
        
        try:
            if choice in ['1', '4']:
                path = str(EXPORT_DIR / "intimacy_distribution.png") if save else None
                self.analyzer.plot_intimacy_distribution(path)
            if choice in ['2', '4']:
                path = str(EXPORT_DIR / "food_analysis.png") if save else None
                self.analyzer.plot_food_analysis(path)
            if choice in ['3', '4']:
                path = str(EXPORT_DIR / "preference_heatmap.png") if save else None
                self.analyzer.plot_preference_heatmap(path)
            if not save:
                print("\n✓ Displayed")
        except Exception as e:
            self.show_error(str(e))
        wait_for_key()