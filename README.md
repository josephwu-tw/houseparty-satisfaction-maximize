# **Maximizing House Party Hosting Satisfaction**

**Creators:** Chen-Yen Wu, Jinghong Yang, Yuting Wan

## **Project Summary
### **Problem Definition:**
	  
Joseph \-  
When hosting a house party, the host might need to consider which type of snacks to prepare and how many to purchase within a limited budget. Besides, each friend has a different level of intimacy with the host. Therefore, we decided to create a tool to help people plan their house party.

Yuting \-  
	This project applies dynamic programming into a real-life house party scenario, making the learned algorithm both fun and practical. We simulate a budget-constrained optimization problem, different intimacy friends with different weights. By selecting a set of snacks to maximize overall satisfaction. It resembles an extended version of the 0-1 knapsack problem.

Jinghong \-  
	In the real life scenario, the host may be concerned about whether the preparation of the house party is enough to make the guests satisfied,  so we are going to make an application which can help people to avoid such disappointment due to this reason. Also, this is a good way for the host to get to know the preferences of others.

### **Scope:**

Our dataset features several notable characteristics:  
	Friend \-

* name  
* preference for each type of food (1-5)  
* intimacy Level (1-10)

	Food \-

* type  
* cost per unit


	Computation Process:

1. Given a budget limit  
2. Calculate the guest's satisfaction level with related food preferences  
3. Find the combinations of total cost and the host’s happiness (by level of intimacy)  
4. Evaluate the combinations by measuring happiness and cost savings  
5. Provide a recommended guest list and food preparation.

### **Description:**

1. Data collecting and cleaning  
2. Design and test the guest satisfaction calculator  
3. Design and test the generator of guest lists and intimacy level combinations  
4. Design the evaluation system of host satisfaction by balancing cost saving and intimacy happiness under different scenarios  
5. Overall testing and final proposal documenting

### **Tasks:**

We divided the project into three parts, each teammate mainly owner for a different area. We’ll also have group discussions together for each part.

Chen-Yen Wu:   
Responsible for designing and testing the generator of guest lists and intimacy level combinations, and participating in the design and testing of the guest satisfaction calculator.

Jinghong Yang:   
Responsible for participating in the design and testing and the evaluation system of host satisfaction.

Yuting Wan:   
Responsible for data collecting, cleaning and participating in guest satisfaction calculator design and test. 

### **Course Relation:**

Dynamic Programming  
It involves breaking the problem into smaller parts. Each time we should decide whether or not to buy a snack, the rest of the problem stays the same in structure. And also it involves building up to the optimal solutions step by step, the best choice at the current point equals the best satisfaction in the previous budget, and plus the extra value this snack brings.   
Maximize i(satisfaction of snacks)i, subject to icostbudget  
We use DP’s state definition and transition formula to find the best combination, which is faster than trying out all possibilities with brute-force.

## App Design

### **Data Structure Example**

Friend List

| Name | Fried Chicken | Chips | Sand-wich | Cookies | Sweeties | Soda | Juice | Black Tea | Intimacy level |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| Tom | 5 | 3 | 4 | 2 | 1 | 5 | 3 | 1 | 7 |
| Ariel | 3 | 2 | 5 | 3 | 4 | 2 | 3 | 4 | 6 |

Food Price per unit Table

| Fried Chicken | Chips | Sand-wich | Cookies | Candy | Soda | Juice | Tea |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| 5.7 | 2.99 | 4.0 | 1.99 | 0.99 | 2.49 | 2.79 | 1.89 |

### **Interface** 

