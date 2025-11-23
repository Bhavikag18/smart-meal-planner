# 🧠 The Machine Learning Behind Your Diet Plan

This project uses a fundamental Machine Learning algorithm called **K-Nearest Neighbors (KNN)** to recommend meals. Here is a simple breakdown of how it works.

## 1. The Goal
We want to find a meal from our database (food_data.csv) that matches your specific calorie needs.

*   **Input**: I need a Lunch with **700 calories**.
*   **Database**: Contains hundreds of foods, each with a calorie value (e.g., Paneer Butter Masala = 300 cal, Biryani = 450 cal).

## 2. The Algorithm: K-Nearest Neighbors (KNN)
Imagine all our foods are plotted on a line based on their calories.

*   **Low Calorie** <------------------------------------> **High Calorie**
*   (Salad: 100) ... (Paneer: 300) ... (Biryani: 450) ... (Thali: 800)

When you ask for **700 calories**, the KNN algorithm looks at this line and finds the Neighbor that is closest to the number 700.

### Why use ML instead of simple filtering?
While simple filtering (calories == 700) might fail if no food is *exactly* 700, KNN finds the **closest match** (e.g., a 680-calorie meal or a 720-calorie meal). It is robust and always gives an answer.

## 3. The Smart Logic (Heuristics)
ML is great at finding the *main dish*, but a real meal is more complex. We add custom logic on top of the ML predictions:

1.  **Gap Filling**: If the ML picks a 300-calorie curry but you need 700 calories, there is a 400-calorie Gap.
2.  **Staple Calculation**: We calculate how many Chapatis (100 cal each) fit into that gap.
    *   Gap: 400 / 100 = **4 Chapatis**.
3.  **Variety Enforcement**: We track what you ate for Lunch. If the ML suggests the same dish for Dinner, we force it to pick the *next* closest neighbor to ensure variety.

## Summary
1.  **Math (BMR/TDEE)** calculates *how much* you need.
2.  **ML (KNN)** finds the *best food match* from the database.
3.  **Code Logic** adds the *sides and staples* to make it a complete meal.
