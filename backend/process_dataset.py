import pandas as pd
import numpy as np

def preprocess_new_dataset(input_path, output_path):
    print(f"Reading from {input_path}...")
    df = pd.read_csv(input_path)
    
    # 1. Rename Columns
    rename_map = {
        "Dish Name": "Name",
        "Calories (kcal)": "Calories",
        "Protein (g)": "Proteins",
        "Fats (g)": "Fats",
        "Carbohydrates (g)": "Carbs"
    }
    df = df.rename(columns=rename_map)
    
    # 2. Infer Type (Veg/Non-Veg)
    non_veg_keywords = ["Chicken", "Mutton", "Fish", "Egg", "Prawn", "Keema", "Omelette", "Beef", "Pork", "Bacon", "Ham", "Salami", "Sausage", "Meat", "Lamb", "Crab", "Shrimp"]
    def get_type(name):
        for kw in non_veg_keywords:
            if kw.lower() in str(name).lower():
                return "Non-Veg"
        return "Veg"
    
    df['Type'] = df['Name'].apply(get_type)
    
    # 3. Infer Category & Meal Type
    def get_category_meal(name):
        name = str(name).lower()
        
        # --- 1. STRICT EXCLUSIONS (Ingredients / Not a Meal) ---
        # These should be removed from the dataset entirely by the caller loop, 
        # but if they slip through, mark them as Snack/Side to be safe.
        ingredient_keywords = [
            "icing", "frosting", "filling", "spread", "sauce", "dip", "jam", "jelly", 
            "syrup", "concentrate", "crush", "squash", "puree", "paste", "powder", 
            "flour", "oil", "seeds", "raw", "dough", "batter", "extract", "essence",
            "stock", "vinegar", "dressing", "mayonnaise", "butter", "ghee", "cream",
            "sugar", "salt", "spice", "condiment", "masala"
        ]
        # Exceptions: "Butter Chicken", "Ice Cream", "Fruit Salad with Cream", "Paneer Butter Masala"
        if any(x in name for x in ingredient_keywords):
             if "butter" in name and any(x in name for x in ["chicken", "paneer", "masala", "milk", "nan", "roti"]):
                 pass # Allow Butter Chicken, Paneer Butter Masala
             elif "cream" in name and any(x in name for x in ["soup", "salad", "chicken", "veg", "fruit", "ice"]):
                 pass # Allow Cream soups, Ice cream
             elif "sauce" in name and any(x in name for x in ["pasta", "spaghetti", "fish", "chicken", "veg"]):
                 pass # Allow dishes in sauce
             elif "masala" in name:
                 # Only allow Masala if it specifies a main ingredient
                 if any(x in name for x in ["paneer", "chicken", "chana", "rajma", "gobi", "bhindi", "aloo", "mushroom", "egg", "fish", "mutton", "veg", "kofta", "dosa", "vada", "prawn", "shrimp", "crab", "lobia", "soya", "chaat"]):
                     pass
                 else:
                     return "Exclude", "Exclude"
             else:
                 return "Exclude", "Exclude"

        # --- 2. SNACKS (Deep Fried / Junk / Light) ---
        # These should NEVER be Lunch/Dinner main courses
        snack_keywords = [
            "murukku", "chakli", "sev", "mixture", "bhujia", "chips", "puff", 
            "vada", "samosa", "pakora", "pakoda", "cutlet", "roll", "bonda", "bajji", 
            "mathri", "khakhra", "chivda", "dhokla", "khandvi", "patra", "muthiya",
            "manchurian", "65", "lollipop", "fingers", "nuggets", "pizza", "burger", 
            "fries", "frankie", "tacos", "nachos", "popcorn", "sandwich", "toast",
            "biscuit", "cookie", "cake", "pastry", "tart", "pie", "doughnut", 
            "chocolate", "candy", "sweet", "dessert", "ice cream", "halwa", "kheer", 
            "laddu", "barfi", "burfi", "pedha", "gulab jamun", "rasgulla", "jalebi", "mysore pak",
            "sonpapdi", "rasmalai", "petha", "gazak", "chikki", "kalakand", "pinni", "modak"
        ]
        
        if any(x in name for x in snack_keywords):
            # Exceptions for Breakfast
            if "sandwich" in name or "toast" in name or "cutlet" in name or "dhokla" in name:
                 # Some can be breakfast, but let's keep them out of Lunch/Dinner
                 return "Snack", "Snack" 
            return "Snack", "Snack"

        # --- 3. BEVERAGES ---
        if any(x in name for x in ["tea", "coffee", "juice", "shake", "lassi", "buttermilk", "milk", "drink", "sherbet", "thandai", "kanji", "smoothie", "soda", "water", "soup", "shorba", "cooler", "squash"]):
            return "Beverage", "Side"

        # --- 4. SIDES ---
        if any(x in name for x in ["raita", "salad", "papad", "chutney", "pickle", "yogurt", "curd", "achar"]):
            return "Side", "Side"

        # --- 5. BREAKFAST ---
        breakfast_keywords = ["paratha", "dosa", "idli", "poha", "upma", "omelette", "bhurji", "cheela", "pancake", "waffle", "cereal", "oats", "cornflakes", "muesli", "appam", "uthappam", "puri", "poori", "bhatura", "thepla", "thalipeeth", "roti", "chapati", "naan", "kulcha"]
        
        if any(x in name for x in breakfast_keywords):
            return "Breakfast", "Breakfast"

        # --- 6. MAIN COURSE (LUNCH/DINNER) ---
        
        # Rice / Complete Meals
        if any(x in name for x in ["biryani", "pulao", "khichdi", "fried rice", "rice", "tahri", "bisibelebath", "lemon rice", "tamarind rice", "jeera rice", "curd rice", "daliya", "pasta", "noodle", "macaroni", "spaghetti", "lasagne", "chowmein"]):
            if any(x in name for x in ["biryani", "khichdi", "bisibelebath", "curd rice", "fried rice", "daliya", "pasta", "noodle", "macaroni", "spaghetti", "lasagne", "chowmein"]):
                return "Complete", "Lunch/Dinner"
            return "RiceSide", "Lunch/Dinner"

        # Gravies (Curries)
        if any(x in name for x in ["curry", "masala", "dal", "korma", "makhani", "vindaloo", "saag", "gravy", "paneer", "chicken", "mutton", "fish", "kofta", "kadhi", "sambhar", "rajma", "chole", "lobia", "kootu", "stew", "handi", "lababdar", "do pyaza", "butter", "pasanda", "rezala", "rogan josh", "moilee", "xacuti"]):
            return "Gravy", "Lunch/Dinner"

        # Dry Sabzis
        if any(x in name for x in ["fry", "bharta", "jeera aloo", "gobi", "bhindi", "mix veg", "poriyal", "thoran", "sabzi", "saute", "methi", "palak", "bhurji", "chana", "baingan", "capsicum", "cabbage", "beans", "aloo", "gajar", "mutter", "sarson", "dry"]):
            return "Dry", "Lunch/Dinner"
        
        # Default fallback - If we don't know what it is, it's safer to call it a Snack than a main meal
        return "Snack", "Snack"

    # Rebuild dataframe with exploded rows for Lunch/Dinner
    new_rows = []
    
    for _, row in df.iterrows():
        cat, meal_type = get_category_meal(row['Name'])
        
        if cat == "Exclude":
            continue
            
        meals = []
        if meal_type == "Lunch/Dinner":
            meals = ["Lunch", "Dinner"]
        else:
            meals = [meal_type]
    
        for m in meals:
            new_row = row.copy()
            new_row['Category'] = cat
            new_row['Meal_Type'] = m
            new_rows.append(new_row)
    
    processed_df = pd.DataFrame(new_rows)
    
    # Ensure numeric columns
    for col in ['Calories', 'Proteins', 'Fats', 'Carbs']:
        processed_df[col] = pd.to_numeric(processed_df[col], errors='coerce').fillna(0)
    
    # Select final columns
    final_cols = ["Name", "Type", "Calories", "Proteins", "Fats", "Carbs", "Meal_Type", "Category"]
    processed_df = processed_df[final_cols]
    
    print(f"Writing to {output_path}...")
    processed_df.to_csv(output_path, index=False)
    print("Done!")

if __name__ == "__main__":
    preprocess_new_dataset("Indian_Food_Nutrition_Processed.csv", "food_data_processed.csv")
