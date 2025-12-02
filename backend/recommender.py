import pandas as pd
from sklearn.neighbors import NearestNeighbors
import numpy as np
import random

class DietRecommender:
    def __init__(self, data_path="food_data.csv"):
        self.df = pd.read_csv(data_path)
        # Check if it's the new dataset by checking columns
        if "Dish Name" in self.df.columns:
            self.df = self._preprocess_new_dataset(self.df)
            
        self.staples = {
            "Chapati": {"Calories": 100, "Proteins": 3, "Fats": 1, "Carbs": 20},
            "Steamed Rice (1 cup)": {"Calories": 150, "Proteins": 3, "Fats": 0.5, "Carbs": 35}
        }
        # Pre-filter sides and beverages
        self.sides_df = self.df[self.df['Category'].isin(['Side', 'Beverage'])].drop_duplicates(subset=['Name'])

    def _preprocess_new_dataset(self, df):
        # 1. Rename Columns
        df = df.rename(columns={
            "Dish Name": "Name",
            "Calories (kcal)": "Calories",
            "Protein (g)": "Proteins",
            "Fats (g)": "Fats",
            "Carbohydrates (g)": "Carbs"
        })
        
        # 2. Infer Type (Veg/Non-Veg)
        non_veg_keywords = ["Chicken", "Mutton", "Fish", "Egg", "Prawn", "Keema", "Omelette", "Beef", "Pork"]
        def get_type(name):
            for kw in non_veg_keywords:
                if kw.lower() in str(name).lower():
                    return "Non-Veg"
            return "Veg"
        
        df['Type'] = df['Name'].apply(get_type)
        
        # 3. Infer Category & Meal Type
        def get_category_meal(name):
            name = str(name).lower()
            
            # 1. Desserts (Strictly exclude from main meals)
            if any(x in name for x in ["burfi", "barfi", "laddu", "ladoo", "halwa", "kheer", "payasam", "jamun", "jalebi", "cake", "cookie", "chocolate", "sweet", "mysore pak", "peda", "rasgulla", "rasmalai", "gajak", "kalakand", "petha", "sandesh", "shrikhand", "pinni", "modak"]):
                return "Snack", "Snack"

            # 2. Beverages
            if any(x in name for x in ["tea", "coffee", "juice", "shake", "lassi", "buttermilk", "milk", "drink", "sherbet", "thandai", "kanji"]):
                return "Beverage", "Side"

            # 3. Sides (Accompaniments)
            if any(x in name for x in ["raita", "salad", "papad", "chutney", "pickle", "sauce", "dip", "ketchup", "yogurt", "curd"]):
                return "Side", "Side"

            # 4. Breakfast (Specific items)
            if any(x in name for x in ["paratha", "dosa", "idli", "poha", "upma", "sandwich", "toast", "omelette", "bhurji", "cheela", "pancake", "waffle", "cereal", "oats", "cornflakes", "muesli", "appam", "uthappam"]):
                return "Breakfast", "Breakfast"

            # 5. Snacks (Savoury/Light)
            if any(x in name for x in ["samosa", "pakora", "burger", "pizza", "roll", "cutlet", "chaat", "bhel", "puri", "vada", "bonda", "bajji", "dhokla", "khandvi", "mathri", "khakhra", "biscuit", "puff", "fries", "chips", "namkeen", "sev", "bhujia", "tikki", "kachori", "momo", "spring roll", "wrap", "frankie"]):
                return "Snack", "Snack"

            # 6. Main Course - Rice/Complete
            if any(x in name for x in ["biryani", "pulao", "khichdi", "fried rice", "rice", "tahri", "bisibelebath", "lemon rice", "tamarind rice"]):
                return "Complete", "Lunch/Dinner"

            # 7. Main Course - Gravies (Curries)
            if any(x in name for x in ["curry", "masala", "dal", "korma", "makhani", "vindaloo", "saag", "gravy", "paneer", "chicken", "mutton", "fish", "kofta", "kadhi", "sambhar", "rajma", "chole", "lobia", "kootu", "stew"]):
                return "Gravy", "Lunch/Dinner"

            # 8. Main Course - Dry Sabzis
            if any(x in name for x in ["fry", "bharta", "jeera aloo", "gobi", "bhindi", "mix veg", "poriyal", "thoran", "sabzi", "saute", "methi", "palak", "bhurji", "chana"]):
                return "Dry", "Lunch/Dinner"
            
            # Default fallback - Safer to assume Snack/Side if unknown, to avoid weird main courses
            return "Snack", "Snack"

        # Rebuild dataframe with exploded rows for Lunch/Dinner
        new_rows = []
        
        # Keywords to exclude (Ingredients, Raw items)
        exclude_keywords = [
            "powder", "masala", "flour", "oil", "seeds", "raw", "dough", "batter", 
            "paste", "puree", "extract", "essence", "crushed", "dried", "flakes", 
            "cubes", "slices", "chopped", "grated", "peeled", "whole", "split", 
            "kernel", "pulp", "juice concentrate", "syrup", "sauce", "dip", 
            "dressing", "vinegar", "yeast", "gelatin", "agar", "baking", "cooking",
            "cream", "butter", "ghee", "cheese", "curd", "yogurt", "milk", "whey",
            "sugar", "salt", "spice", "herb", "condiment", "pickle", "chutney",
            "jam", "jelly", "marmalade", "preserve", "spread", "topping", "filling",
            "frosting", "icing", "glaze", "coating", "batter", "mix", "base",
            "stock", "broth", "bouillon", "cube", "granule", "concentrate"
        ]
        
        # Exception list: Items that contain exclude keywords but are actual dishes
        # e.g. "Paneer Butter Masala" contains "Masala" and "Butter" but is a dish.
        # "Sambar Powder" is an ingredient, "Sambar" is a dish.
        # We will filter based on if the name is *mostly* an ingredient.
        
        for _, row in df.iterrows():
            name_lower = str(row['Name']).lower()
            
            # Skip if it's clearly an ingredient
            if any(x in name_lower for x in ["powder", "flour", "oil", "seeds", "raw", "dough", "batter", "paste", "puree", "extract", "essence"]):
                 # But allow specific dishes like "Paneer Butter Masala" or "Chana Masala"
                 if "masala" in name_lower and not any(x in name_lower for x in ["paneer", "chicken", "chana", "rajma", "gobi", "bhindi", "aloo", "mushroom", "egg", "fish", "mutton"]):
                     continue
                 if "powder" in name_lower:
                     continue
                 if "flour" in name_lower:
                     continue
            
            cat, meal_type = get_category_meal(row['Name'])
            
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
        
        df = pd.DataFrame(new_rows)
        
        # Ensure numeric columns are actually numeric
        for col in ['Calories', 'Proteins', 'Fats', 'Carbs']:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
        return df
    
    def calculate_bmr(self, weight, height, age, gender):
        if gender.lower() == 'male':
            return (10 * weight) + (6.25 * height) - (5 * age) + 5
        else:
            return (10 * weight) + (6.25 * height) - (5 * age) - 161

    def calculate_tdee(self, bmr, activity_level, goal):
        multipliers = {
            "sedentary": 1.2, "light": 1.375, "moderate": 1.55,
            "active": 1.725, "extra_active": 1.9
        }
        tdee = bmr * multipliers.get(activity_level, 1.2)
        
        if goal == "weight_loss":
            # Target should be between BMR and TDEE-500
            target = tdee - 500
            tdee = max(bmr - 100, target) if target < bmr else target
        elif goal == "weight_gain":
            tdee += 300
            
        return max(1200, tdee)

    def recommend(self, age, weight, height, gender, activity_level, veg_preference, goal):
        bmr = self.calculate_bmr(weight, height, age, gender)
        tdee = self.calculate_tdee(bmr, activity_level, goal)
        
        targets = {
            "Breakfast": tdee * 0.25, "Lunch": tdee * 0.35,
            "Dinner": tdee * 0.30, "Snack": tdee * 0.10
        }
        
        recommendations = {}
        used_dishes = set()
        
        # Base filter for Veg/Non-Veg
        base_df = self.df if veg_preference != "Veg" else self.df[self.df['Type'] == 'Veg']
        
        for meal, target in targets.items():
            if meal in ["Lunch", "Dinner"]:
                rec = self._recommend_lunch_dinner(meal, target, base_df, veg_preference, used_dishes)
            elif meal == "Breakfast":
                rec = self._recommend_breakfast(target, base_df, used_dishes)
            else:
                rec = self._recommend_simple(meal, target, base_df, used_dishes)
            
            if rec:
                recommendations[meal] = rec
                # Add main components to used list to avoid repetition
                for part in rec['Name'].split(" + "):
                    used_dishes.add(part.strip())

        total_cal = sum(m['Calories'] for m in recommendations.values() if m)
        
        # Calculate Accuracy (Total Calorie Match)
        accuracy = 0
        if tdee > 0:
            accuracy = max(0, 100 - (abs(total_cal - tdee) / tdee * 100))

        # Calculate Precision (Meal-wise Match)
        meal_deviations = []
        for meal, target in targets.items():
            if meal in recommendations:
                actual = recommendations[meal]['Calories']
                if target > 0:
                    deviation = abs(actual - target) / target
                    meal_deviations.append(deviation)
            else:
                meal_deviations.append(1.0) # 100% error if meal missing
        
        precision = 0
        if meal_deviations:
            avg_deviation = sum(meal_deviations) / len(meal_deviations)
            precision = max(0, 100 - (avg_deviation * 100))

        return {
            "BMR": round(bmr, 2),
            "TDEE": round(tdee, 2),
            "TotalCalories": int(total_cal),
            "Accuracy": round(accuracy, 2),
            "Precision": round(precision, 2),
            "Plan": recommendations
        }

    def _get_meal_options(self, meal_type, base_df, used_dishes, veg_preference="Any"):
        # Filter by meal type and exclude used dishes
        options = base_df[
            (base_df['Meal_Type'] == meal_type) & 
            (~base_df['Name'].isin(used_dishes))
        ]
        
        # Fallback: if ran out of options, reuse dishes
        if options.empty:
            options = base_df[base_df['Meal_Type'] == meal_type]
            
        # Prioritize Non-Veg if user is Non-Veg
        if veg_preference == "Non-Veg":
            nv_options = options[options['Type'] == 'Non-Veg']
            if not nv_options.empty:
                return nv_options
                
        return options

    def _recommend_lunch_dinner(self, meal_type, target, base_df, veg_preference, used_dishes):
        options = self._get_meal_options(meal_type, base_df, used_dishes, veg_preference)
        if options.empty: return None
        
        current_target = target
        side_dish = None
        
        # 1. Select Side Dish (80% chance)
        # Filter for savory sides (exclude sweet drinks)
        savory_sides = self.sides_df[self.sides_df['Name'].apply(lambda x: not any(s in str(x).lower() for s in ['shake', 'juice', 'coffee', 'tea']))]
        if veg_preference == "Veg": 
            savory_sides = savory_sides[savory_sides['Type'] == 'Veg']
            
        if not savory_sides.empty and random.random() < 0.8:
            side_dish = savory_sides.sample(1).iloc[0].to_dict()
            current_target -= side_dish['Calories']

        # 2. Select Main Dish Strategy: Complete Meal vs Curry + Staple
        curries = options[options['Category'].isin(['Gravy', 'Dry'])]
        complete = options[options['Category'].isin(['RiceSide', 'Complete'])]
        
        # Default to Curry+Staple (70%), unless no curries available
        use_complete = False
        if not complete.empty and (curries.empty or random.random() < 0.3):
            use_complete = True
            
        main_dish = None
        staple_info = None
        extra_dish = None
        
        if not use_complete and not curries.empty:
            # --- Curry + Staple Logic ---
            main_target = current_target * 0.6
            main_dish = self._find_closest(curries, main_target).to_dict()
            
            # Determine Staple (Rice or Chapati)
            remaining = current_target - main_dish['Calories']
            is_rice_dish = any(x in main_dish['Name'] for x in ['Rice', 'Fish'])
            staple_name = "Steamed Rice (1 cup)" if is_rice_dish else "Chapati"
            staple_cal = self.staples[staple_name]['Calories']
            
            # Calculate Quantity
            qty = max(0.5, round(remaining / staple_cal * 2) / 2)
            if staple_name == "Chapati" and qty > 4: qty = 4 # Cap at 4 Chapatis
            
            staple_info = {"Name": staple_name, "Qty": qty, "Stats": self.staples[staple_name]}
            
            # Check for large calorie deficit -> Add Extra Dish
            deficit = remaining - (qty * staple_cal)
            if deficit > 100:
                extra_opts = options[options['Category'].isin(['RiceSide', 'Gravy', 'Dry'])]
                extra_opts = extra_opts[extra_opts['Name'] != main_dish['Name']]
                if not extra_opts.empty:
                    extra_dish = self._find_closest(extra_opts, deficit).to_dict()
        else:
            # --- Complete Meal Logic ---
            pool = complete if not complete.empty else options
            main_dish = self._find_closest(pool, current_target).to_dict()
            
            # Scale up if portion is too small (< 60% of target)
            if main_dish['Calories'] < current_target * 0.6:
                main_dish['Name'] = f"2 servings of {main_dish['Name']}"
                for k in ['Calories', 'Proteins', 'Fats', 'Carbs']: 
                    main_dish[k] *= 2

        return self._format_meal(main_dish, staple_info, side_dish, extra_dish, meal_type)

    def _recommend_breakfast(self, target, base_df, used_dishes):
        options = self._get_meal_options("Breakfast", base_df, used_dishes)
        if options.empty: return None
        
        # Pick random option close to target (minus buffer for potential side)
        target_search = max(200, target - 150)
        X = options[['Calories']].values
        nbrs = NearestNeighbors(n_neighbors=min(10, len(options)), algorithm='ball_tree').fit(X)
        indices = nbrs.kneighbors([[target_search]])[1][0]
        main_dish = options.iloc[random.choice(indices)].to_dict()
        
        # Check for pairings (e.g. Idli + Sambar)
        side_dish = self._find_pairing(main_dish['Name'])
        
        return self._format_meal(main_dish, None, side_dish, None, "Breakfast")

    def _recommend_simple(self, meal_type, target, base_df, used_dishes):
        options = self._get_meal_options(meal_type, base_df, used_dishes)
        if options.empty: return None
        
        main_dish = self._find_closest(options, target).to_dict()
        return self._format_meal(main_dish, None, None, None, meal_type)

    def _find_pairing(self, dish_name):
        pairings = {
            "Bhatura": ["Chole", "Chickpeas"], "Poori": ["Aloo", "Potato"],
            "Idli": ["Sambar", "Chutney"], "Dosa": ["Sambar", "Chutney"],
            "Paratha": ["Curd", "Yogurt"], "Roti": ["Dal", "Sabzi"]
        }
        for key, sides in pairings.items():
            if key.lower() in dish_name.lower():
                if any(s.lower() in dish_name.lower() for s in sides): return None # Already has side
                
                for s in sides:
                    matches = self.df[self.df['Name'].str.contains(s, case=False)]
                    if not matches.empty:
                        return matches.sort_values('Calories').iloc[0].to_dict()
        return None

    def _format_meal(self, main, staple, side, extra, meal_type):
        total_stats = {k: main[k] for k in ['Calories', 'Proteins', 'Fats', 'Carbs']}
        name_parts = [main['Name']]
        
        if staple:
            s_name = "Steamed Rice" if "Rice" in staple['Name'] else "Chapati"
            qty_str = f"{staple['Qty']} cups" if "Rice" in s_name else f"{int(staple['Qty'])} {s_name}"
            # Avoid redundant "Rice + Rice"
            if "Rice" in main['Name'] and "Rice" in s_name:
                 name_parts.append(qty_str)
            else:
                 name_parts.append(qty_str + (" " + s_name if "Rice" in s_name else ""))
            
            for k in total_stats: total_stats[k] += staple['Qty'] * staple['Stats'][k]
            
        if extra:
            name_parts.append(extra['Name'])
            for k in total_stats: total_stats[k] += extra[k]
            
        if side:
            name_parts.append(side['Name'])
            for k in total_stats: total_stats[k] += side[k]
            
        return {
            "Name": " + ".join(name_parts),
            "Type": main['Type'],
            "Meal_Type": meal_type,
            "Category": main.get('Category', 'Unknown'),
            **{k: int(v) for k, v in total_stats.items()}
        }

    def _find_closest(self, df, target_cal):
        X = df[['Calories']].values
        nbrs = NearestNeighbors(n_neighbors=1, algorithm='ball_tree').fit(X)
        distances, indices = nbrs.kneighbors([[target_cal]])
        return df.iloc[indices[0][0]]
