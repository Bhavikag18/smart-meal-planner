import pandas as pd
import random

# Foods with Category: 'Gravy', 'Dry', 'Complete', 'Snack', 'Breakfast', 'Side', 'Beverage', 'RiceSide'
foods = [
    # Breakfast
    ("Oatmeal", "Veg", 150, 5, 3, 27, "Breakfast", "Complete"),
    ("Scrambled Eggs", "Non-Veg", 200, 14, 15, 2, "Breakfast", "Complete"),
    ("Idli Sambar", "Veg", 180, 6, 2, 35, "Breakfast", "Complete"),
    ("Poha", "Veg", 200, 4, 8, 30, "Breakfast", "Complete"),
    ("Avocado Toast", "Veg", 250, 6, 18, 20, "Breakfast", "Complete"),
    ("Masala Dosa", "Veg", 350, 8, 12, 50, "Breakfast", "Complete"),
    ("Aloo Paratha", "Veg", 300, 8, 15, 40, "Breakfast", "Complete"),
    ("Upma", "Veg", 180, 4, 6, 30, "Breakfast", "Complete"),
    ("Besan Chilla", "Veg", 220, 10, 8, 25, "Breakfast", "Complete"),
    ("Paneer Paratha", "Veg", 320, 12, 16, 35, "Breakfast", "Complete"),
    ("Moong Dal Cheela", "Veg", 200, 12, 6, 28, "Breakfast", "Complete"),
    ("Veg Grilled Sandwich", "Veg", 280, 8, 10, 40, "Breakfast", "Complete"),
    ("Methi Thepla", "Veg", 200, 5, 8, 28, "Breakfast", "Complete"),
    ("Vermicelli Upma", "Veg", 220, 5, 7, 35, "Breakfast", "Complete"),
    ("Rava Idli", "Veg", 160, 6, 4, 25, "Breakfast", "Complete"),
    ("Oats Pancake", "Veg", 240, 8, 8, 32, "Breakfast", "Complete"),
    ("Egg Bhurji + Toast", "Non-Veg", 300, 16, 18, 20, "Breakfast", "Complete"),
    ("Cheese Omelette", "Non-Veg", 320, 18, 22, 5, "Breakfast", "Complete"),
    ("Muesli with Milk", "Veg", 280, 10, 6, 45, "Breakfast", "Complete"),
    ("Sabudana Khichdi", "Veg", 350, 3, 15, 55, "Breakfast", "Complete"),
    
    # Lunch/Dinner - Gravies/Curries (Need Staple)
    ("Paneer Butter Masala", "Veg", 300, 12, 25, 10, "Lunch/Dinner", "Gravy"),
    ("Dal Makhani", "Veg", 280, 10, 15, 20, "Lunch/Dinner", "Gravy"),
    ("Chana Masala", "Veg", 220, 12, 8, 30, "Lunch/Dinner", "Gravy"),
    ("Palak Paneer", "Veg", 260, 14, 20, 8, "Lunch/Dinner", "Gravy"),
    ("Chicken Curry", "Non-Veg", 300, 25, 18, 5, "Lunch/Dinner", "Gravy"),
    ("Butter Chicken", "Non-Veg", 350, 28, 22, 8, "Lunch/Dinner", "Gravy"),
    ("Fish Curry", "Non-Veg", 280, 25, 15, 5, "Lunch/Dinner", "Gravy"),
    ("Egg Curry", "Non-Veg", 220, 12, 16, 6, "Lunch/Dinner", "Gravy"),
    ("Kadai Vegetable", "Veg", 180, 5, 10, 15, "Lunch/Dinner", "Gravy"),
    ("Rajma Masala", "Veg", 240, 10, 8, 30, "Lunch/Dinner", "Gravy"),
    ("Mutter Paneer", "Veg", 270, 11, 18, 12, "Lunch/Dinner", "Gravy"),
    ("Malai Kofta", "Veg", 320, 8, 22, 18, "Lunch/Dinner", "Gravy"),
    
    # Lunch/Dinner - Dry/Sides (Can be main with staple or side)
    ("Bhindi Masala", "Veg", 150, 4, 8, 12, "Lunch/Dinner", "Dry"),
    ("Aloo Gobi", "Veg", 180, 5, 9, 20, "Lunch/Dinner", "Dry"),
    ("Chicken Stir Fry", "Non-Veg", 250, 25, 10, 8, "Lunch/Dinner", "Dry"),
    ("Jeera Aloo", "Veg", 160, 3, 8, 22, "Lunch/Dinner", "Dry"),
    ("Baingan Bharta", "Veg", 140, 3, 6, 15, "Lunch/Dinner", "Dry"),
    ("Mix Veg", "Veg", 170, 4, 8, 18, "Lunch/Dinner", "Dry"),
    
    # Lunch/Dinner - Complete Meals (No staple needed)
    ("Vegetable Biryani", "Veg", 350, 8, 12, 50, "Lunch/Dinner", "Complete"),
    ("Chicken Biryani", "Non-Veg", 450, 25, 18, 45, "Lunch/Dinner", "Complete"),
    ("Rice and Dal", "Veg", 300, 10, 5, 50, "Lunch/Dinner", "Complete"),
    ("Khichdi", "Veg", 250, 8, 6, 40, "Lunch/Dinner", "Complete"),
    ("Pasta Arrabbiata", "Veg", 350, 10, 12, 55, "Lunch/Dinner", "Complete"),
    ("Grilled Chicken Salad", "Non-Veg", 300, 30, 10, 15, "Lunch/Dinner", "Complete"),
    ("Curd Rice", "Veg", 220, 6, 8, 35, "Lunch/Dinner", "Complete"),
    
    # Rice Sides (To be added when Chapatis are capped)
    ("Veg Pulao", "Veg", 200, 4, 6, 35, "Lunch/Dinner", "RiceSide"),
    ("Jeera Rice", "Veg", 180, 3, 5, 32, "Lunch/Dinner", "RiceSide"),
    ("Peas Pulao", "Veg", 190, 4, 5, 34, "Lunch/Dinner", "RiceSide"),
    ("Ghee Rice", "Veg", 220, 2, 10, 30, "Lunch/Dinner", "RiceSide"),

    # Snacks
    ("Greek Yogurt", "Veg", 100, 10, 0, 15, "Snack", "Snack"),
    ("Almonds (Handful)", "Veg", 160, 6, 14, 6, "Snack", "Snack"),
    ("Fruit Salad", "Veg", 120, 2, 0, 30, "Snack", "Snack"),
    ("Chickpea Salad", "Veg", 200, 10, 8, 25, "Snack", "Snack"),
    ("Roasted Makhana", "Veg", 100, 3, 0, 20, "Snack", "Snack"),
    ("Sprouts Salad", "Veg", 150, 8, 1, 25, "Snack", "Snack"),
    ("Corn Chaat", "Veg", 180, 5, 2, 35, "Snack", "Snack"),
    ("Vegetable Sandwich", "Veg", 250, 8, 8, 35, "Snack", "Snack"),
    ("Boiled Eggs (2)", "Non-Veg", 140, 12, 10, 1, "Snack", "Snack"),
    ("Protein Smoothie", "Veg", 200, 20, 4, 25, "Snack", "Snack"),
    ("Dhokla", "Veg", 160, 6, 4, 25, "Snack", "Snack"),
    
    # Sides / Beverages (To be added to meals)
    ("Cucumber Raita", "Veg", 80, 4, 3, 8, "Side", "Side"),
    ("Boondi Raita", "Veg", 120, 3, 6, 12, "Side", "Side"),
    ("Green Salad", "Veg", 50, 1, 0, 10, "Side", "Side"),
    ("Buttermilk (Chaas)", "Veg", 60, 2, 2, 8, "Side", "Beverage"),
    ("Lassi (Sweet)", "Veg", 200, 6, 8, 30, "Side", "Beverage"),
    ("Masala Chai", "Veg", 100, 2, 3, 15, "Side", "Beverage"),
    ("Green Tea", "Veg", 5, 0, 0, 1, "Side", "Beverage")
]

data = []

# Expand main dishes
for _ in range(3): 
    for name, type_, cal, prot, fat, carb, meal_time, category in foods:
        # Split Lunch/Dinner
        meals = ["Lunch", "Dinner"] if meal_time == "Lunch/Dinner" else [meal_time]
        
        for m in meals:
            data.append({
                "Name": name,
                "Type": type_,
                "Calories": int(cal * random.uniform(0.95, 1.05)),
                "Proteins": int(prot * random.uniform(0.95, 1.05)),
                "Fats": int(fat * random.uniform(0.95, 1.05)),
                "Carbs": int(carb * random.uniform(0.95, 1.05)),
                "Meal_Type": m,
                "Category": category
            })

df = pd.DataFrame(data)
df.to_csv("food_data.csv", index=False)
print("food_data.csv created with expanded breakfast")
