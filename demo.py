"""
Automated demo for Party Optimizer.
"""
from models import OptimizationConfig
from optimizer import PartyOptimizer
from utils import initialize_sample_data, print_header, print_section


def run_demo():
    """Run automated demonstration."""
    
    print_header("🎉 PARTY OPTIMIZER - DEMO 🎉")
    
    print_section("Step 1: Load Data")
    friends, foods = initialize_sample_data()
    
    print(f"✓ {len(friends)} friends:")
    for friend in friends:
        print(f"   • {friend.name} (intimacy: {friend.intimacy})")
    
    print(f"\n✓ {len(foods)} foods:")
    for food in foods:
        print(f"   • {food.name}: ${food.cost:.2f}")
    
    print_section("Step 2: Create Optimizer")
    optimizer = PartyOptimizer(friends, foods)
    print("✓ Optimizer ready")
    
    # Test different budgets
    budgets = [15.0, 30.0, 50.0]
    
    for budget in budgets:
        print_section(f"Step 3: Optimize for ${budget:.2f}")
        
        config = OptimizationConfig(budget=budget)
        recommendations = optimizer.get_top_recommendations(config, top_n=3)
        
        print(f"✓ Found {len(recommendations)} recommendations\n")
        
        for i, rec in enumerate(recommendations, 1):
            rec.print_summary(rank=i)
        
        if recommendations:
            best = recommendations[0]
            efficiency = best.max_satisfaction / best.total_cost if best.total_cost > 0 else 0
            utilization = (best.total_cost / budget) * 100
            
            print_section(f"Analysis for ${budget:.2f}")
            print(f"  Satisfaction: {best.max_satisfaction:.1f}")
            print(f"  Efficiency: {efficiency:.2f} per $")
            print(f"  Budget Used: {utilization:.1f}%")
            print(f"  Guests: {len(best.guest_list)}")
            print(f"  Foods: {len(best.recommended_foods)}")
    
    # Compare strategies
    print_section("Step 4: Compare Strategies")
    
    strategies = [
        ("Maximize Satisfaction", 0.7, 0.2, 0.1),
        ("Maximize Savings", 0.2, 0.7, 0.1),
        ("Maximize Intimacy", 0.2, 0.2, 0.6),
        ("Balanced", 0.33, 0.33, 0.34)
    ]
    
    budget = 30.0
    print(f"Testing with ${budget:.2f} budget:\n")
    
    for name, w_sat, w_sav, w_int in strategies:
        config = OptimizationConfig(budget=budget, satisfaction_weight=w_sat,
                                   savings_weight=w_sav, intimacy_weight=w_int)
        recommendations = optimizer.get_top_recommendations(config, top_n=1)
        
        if recommendations:
            best = recommendations[0]
            print(f"{name}:")
            print(f"  → Guests: {', '.join(best.guest_list)}")
            print(f"  → Satisfaction: {best.max_satisfaction:.1f}")
            print(f"  → Cost: ${best.total_cost:.2f}")
            print(f"  → Happiness: {best.host_happiness:.2f}\n")
    
    print_section("Demo Complete!")
    print("✓ Optimization with Dynamic Programming (0/1 Knapsack)")
    print("✓ Multi-objective scoring (satisfaction + savings + intimacy)")
    print("✓ Numpy-accelerated for performance")


if __name__ == "__main__":
    try:
        run_demo()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()