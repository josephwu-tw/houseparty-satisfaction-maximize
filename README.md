# 🎉 House Party Optimizer

A Python application that optimizes house party planning by balancing guest satisfaction, budget constraints, and social intimacy using combinatorial optimization.

## Contributors

**Chen-Yen Wu, Jinghong Yang, Yuting Wan**

**Python Version:** 3.11

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Algorithm Design](#algorithm-design)
- [Project Structure](#project-structure)
- [Data Models](#data-models)

## Overview

When hosting a house party, hosts face a multi-objective optimization problem: selecting the right guests, choosing menu items that satisfy everyone's preferences, and staying within budget—all while maximizing overall party satisfaction.

This project applies **combinatorial optimization** to solve this real-world problem, resembling an extended version of the **0-1 Knapsack Problem** with additional constraints and multiple objectives.

### Problem Definition

Given:
- A set of friends with food preferences (1-5 rating) and intimacy levels (1-10)
- A set of food/drink items with costs
- A budget constraint
- Menu composition rules (1-3 foods + 1-2 drinks)

Find:
- Optimal guest list
- Optimal menu selection
- Maximum host happiness score

## Features

- **Smart Optimization**: Multi-objective optimization balancing satisfaction, cost savings, and intimacy
- **Flexible Constraints**: Configurable menu composition (1-3 foods + 1-2 drinks)
- **Data Management**: Full CRUD operations for friends and food items
- **CSV Import/Export**: Bulk data operations with pandas
- **Random Data Generator**: Generate realistic test datasets
- **Data Visualization**: Matplotlib/Seaborn charts for analysis
- **Interactive CLI**: User-friendly menu-driven interface

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/houseparty-optimizer.git
cd houseparty-optimizer

# Install dependencies
pip install -r requirements.txt
```

### Requirements

```
numpy>=1.24.0
pandas>=2.0.0
matplotlib>=3.7.0
seaborn>=0.12.0
```

## Usage

```bash
python main.py
```

### Quick Start

1. **Run optimization** (Option 1): Enter budget, max guests, and preference weights
2. **View recommendations**: Select from top 5 optimized party configurations
3. **Export results**: Save recommendations as JSON

### Example Session

```
🎉 HOUSE PARTY OPTIMIZER 🎉

Enter your budget ($): 50

Guest Selection:
  Maximum guests [default: 8]: 5
  → Will consider 1-5 guests

Weights (Press Enter for defaults):
  Satisfaction (0.4): 
  Savings (0.2): 
  Intimacy (0.4): 

Running optimization...
  [Optimizer] Searching guest counts: 1 to 5
  [Optimizer] Generated 31 valid recommendations

--- Recommendation #1 ---
Guests: Mike, Bob, Tom
Satisfaction: 126.0
Host Happiness: 4.52
```

## Algorithm Design

### Why Not Dynamic Programming?

While this problem resembles the 0-1 Knapsack Problem, **classical DP does not apply** to the guest selection phase. Here's why:

#### The Core Issue: Non-Independent Subproblems

In standard 0-1 Knapsack, each item has a **fixed value independent of other selected items**. However, in our problem, the value of inviting a guest **changes based on who else is invited** because the optimal menu changes with different guest combinations. This violates DP's **optimal substructure** requirement.

For DP to work, we need:
```
Value(guest_i | guests_selected) = constant
```

But in reality:
```
Value(guest_i | guests_selected) = f(menu_optimization(guests_selected ∪ {guest_i}))
```

The menu optimization is a **nested optimization** that depends on the full guest combination.

### Our Approach: Multi-Objective Evaluation

We use **exhaustive enumeration** over guest combinations, then evaluate each combination using four key metrics:

```
ALGORITHM: PartyOptimizer

INPUT: 
  - friends[]: list of n friends with preferences and intimacy
  - foods[]: list of food items with costs and categories
  - budget: maximum spending limit
  - max_guests: maximum number of guests (k)
  - weights: (w_s, w_c, w_i) for satisfaction, savings, intimacy

OUTPUT:
  - recommendations[]: sorted list of (guests, menu, happiness_score)

PROCEDURE Optimize(config):
    recommendations ← []
    
    // Generate all possible guest combinations from size 1 to k
    // Total combinations = C(n,1) + C(n,2) + ... + C(n,k)
    FOR size FROM 1 TO max_guests:
        // C(n, size) = n! / (size! × (n-size)!)
        FOR guest_combo IN Combinations(friends, size):
            
            // Find best menu for this guest combination
            (satisfaction, menu, cost) ← FindBestMenu(guest_combo, budget)
            
            IF menu is not empty:
                // Calculate total intimacy: sum of all guest intimacy levels
                total_intimacy ← 0
                FOR guest IN guest_combo:
                    total_intimacy ← total_intimacy + guest.intimacy
                
                // Calculate cost savings: remaining budget after purchase
                cost_savings ← budget - cost
                
                // Calculate average satisfaction
                num_guests ← |guest_combo|
                num_items ← |menu|
                avg_satisfaction ← satisfaction / (num_guests × num_items)
                
                // Calculate host happiness (weighted multi-objective score)
                happiness ← (w_s × avg_satisfaction) + 
                            (w_c × cost_savings / 10) + 
                            (w_i × total_intimacy / 10)
                
                recommendations.APPEND((guest_combo, menu, happiness))
    
    // Sort by happiness score in descending order
    RETURN SortByHappiness(recommendations)


PROCEDURE FindBestMenu(guests, budget):
    best_satisfaction ← 0
    best_menu ← []
    best_cost ← 0
    num_guests ← |guests|
    
    // Enumerate all valid menu compositions (1-3 foods + 1-2 drinks)
    FOR num_foods FROM 1 TO min(3, |food_items|):
        FOR food_combo IN Combinations(food_items, num_foods):
            FOR num_drinks FROM 1 TO min(2, |drink_items|):
                FOR drink_combo IN Combinations(drink_items, num_drinks):
                    
                    menu ← food_combo ∪ drink_combo
                    
                    // Cost = sum of item prices × number of guests
                    cost ← 0
                    FOR item IN menu:
                        cost ← cost + item.cost
                    cost ← cost × num_guests
                    
                    // Check budget constraint
                    IF cost ≤ budget:
                        // Calculate total satisfaction
                        satisfaction ← 0
                        FOR item IN menu:
                            FOR guest IN guests:
                                satisfaction ← satisfaction + guest.preference[item]
                        
                        // Track best menu
                        IF satisfaction > best_satisfaction:
                            best_satisfaction ← satisfaction
                            best_menu ← menu
                            best_cost ← cost
    
    RETURN (best_satisfaction, best_menu, best_cost)
```

---

### Evaluation Metrics & Mathematical Formulas

#### 1. Guest Satisfaction

Total satisfaction is the sum of all preference ratings across all guests and menu items:

$S_{total} = \sum_{g \in Guests} \sum_{f \in Menu} P_{g,f}$

Where:
- $P_{g,f}$ = preference rating (1-5) of guest $g$ for food item $f$

**Average Satisfaction** (normalized to 1-5 scale):

$S_{avg} = \frac{S_{total}}{|Guests| \times |Menu|}$

---

#### 2. Cost Savings

The amount of budget remaining after purchasing the menu:

$C_{savings} = Budget - C_{total}$

Where total cost is:

$C_{total} = \left( \sum_{f \in Menu} cost_f \right) \times |Guests|$

---

#### 3. Intimacy Level

Total intimacy represents the closeness of relationships with invited guests:

$I_{total} = \sum_{g \in Guests} intimacy_g$

Where $intimacy_g$ is the intimacy level (1-10) for each guest.

---

#### 4. Host Happiness Score

The final **multi-objective weighted score** combining all metrics:

$H = w_s \cdot S_{avg} + w_c \cdot \frac{C_{savings}}{10} + w_i \cdot \frac{I_{total}}{10}$

Where:
- $w_s$ = satisfaction weight (default: 0.4)
- $w_c$ = cost savings weight (default: 0.2)
- $w_i$ = intimacy weight (default: 0.4)
- Constraint: $w_s + w_c + w_i = 1.0$

The normalization by 10 ensures all components are on comparable scales.

---

### Complete Evaluation Example

**Given:**
- Guests: {Tom, Bob, Mike} with intimacy levels {7, 8, 9}
- Menu: {Chips, Candy, Soda} with costs {$2.99, $0.99, $2.49}
- Budget: $50
- Weights: (0.4, 0.2, 0.4)

**Calculations:**

| Guest | Chips | Candy | Soda | Row Sum |
|-------|-------|-------|------|---------|
| Tom   | 3     | 1     | 5    | 9       |
| Bob   | 5     | 3     | 4    | 12      |
| Mike  | 5     | 2     | 5    | 12      |

$S_{total} = 9 + 12 + 12 = 33$

$S_{avg} = \frac{33}{3 \times 3} = 3.67$

$C_{total} = (2.99 + 0.99 + 2.49) \times 3 = \$19.41$

$C_{savings} = 50 - 19.41 = \$30.59$

$I_{total} = 7 + 8 + 9 = 24$

$H = 0.4 \times 3.67 + 0.2 \times \frac{30.59}{10} + 0.4 \times \frac{24}{10}$

$H = 1.47 + 0.61 + 0.96 = 3.04$

---

### Time Complexity Analysis

#### Why `max_guests` Parameter is Critical

The `max_guests` parameter transforms the algorithm from **exponential** to **polynomial** time complexity:

| Scenario | Complexity | With n=50 friends |
|----------|------------|-------------------|
| No limit (k=n) | $O(2^n)$ | 1,125,899,906,842,624 combinations |
| With limit k=8 | $O(n^k)$ | 536,878,650 combinations |
| **Speedup** | | **~2,097,152× faster** |

Without `max_guests`, we must evaluate all $2^n$ subsets of friends. With `max_guests = k`, we only evaluate:

$\sum_{i=1}^{k} C(n,i) = C(n,1) + C(n,2) + ... + C(n,k) = O(n^k)$

For fixed k, this is **polynomial** in n, making the algorithm practical for real-world use.

#### Complexity Breakdown

| Component | Complexity |
|-----------|------------|
| Guest combinations | $O(n^k)$ for max_guests = k |
| Menu combinations | $O(f^3 \cdot d^2)$ |
| Satisfaction calculation | $O(m \cdot g)$ per menu |
| **Overall** | $O(n^k \cdot f^3 \cdot d^2)$ |

Where: n = friends, k = max_guests, f = foods, d = drinks

#### Practical Performance

| Friends (n) | k=8 Combinations | Approx. Time |
|-------------|------------------|--------------|
| 10          | 45               | < 1 sec      |
| 20          | 125,970          | ~2 sec       |
| 30          | 5,852,925        | ~30 sec      |
| 50          | 536,878,650      | ~15 min      |

## Project Structure

```
houseparty-optimizer/
├── main.py                 # Entry point
├── app.py                  # Application coordinator
├── core/
│   ├── __init__.py
│   ├── config.py           # Configuration constants
│   ├── models.py           # Data models (Friend, Food, etc.)
│   ├── optimizer.py        # Optimization engine
│   └── repositories.py     # Data persistence (JSON)
├── menus/
│   ├── __init__.py
│   ├── base.py             # Base menu class
│   ├── optimization.py     # Optimization workflow
│   ├── friends.py          # Friend management
│   ├── foods.py            # Food management
│   └── analysis.py         # Data analysis
├── services/
│   ├── __init__.py
│   ├── csv_tools.py        # CSV import/export
│   ├── data_analysis.py    # Analytics & visualization
│   └── generator.py        # Random data generator
├── utils/
│   ├── __init__.py
│   └── helpers.py          # Utility functions
├── data/                   # JSON storage
└── exports/                # CSV/report exports
```

## Data Models

### Friend
| Field | Type | Description |
|-------|------|-------------|
| name | string | Friend's name |
| preferences | dict | Food → Rating (1-5) |
| intimacy | int | Closeness level (1-10) |
| dietary_restrictions | list | e.g., ["vegetarian"] |

### Food
| Field | Type | Description |
|-------|------|-------------|
| name | string | Item name |
| cost | float | Price per person |
| category | string | main/snack/dessert/drink |

### Sample Data

**Friends:**
| Name | Fried Chicken | Chips | Sandwich | Cookies | Candy | Soda | Juice | Tea | Intimacy |
|------|---------------|-------|----------|---------|-------|------|-------|-----|----------|
| Tom | 5 | 3 | 4 | 2 | 1 | 5 | 3 | 1 | 7 |
| Ariel | 3 | 2 | 5 | 3 | 4 | 2 | 3 | 4 | 6 |
| Bob | 4 | 5 | 3 | 4 | 3 | 4 | 2 | 2 | 8 |

**Food Prices:**
| Item | Fried Chicken | Chips | Sandwich | Cookies | Candy | Soda | Juice | Tea |
|------|---------------|-------|----------|---------|-------|------|-------|-----|
| Cost | $5.70 | $2.99 | $4.00 | $1.99 | $0.99 | $2.49 | $2.79 | $1.89 |

## License

MIT License - see [LICENSE](LICENSE) for details.

---

*Built for CS 5800 Algorithms @ Northeastern University*
