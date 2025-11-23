import pandas as pd
from sklearn.neighbors import NearestNeighbors
import numpy as np
import random

class DietRecommender:
    def __init__(self, data_path="food_data.csv"):
        try:
            self.df = pd.read_csv(data_path)
            # Check if it's the new dataset by checking columns
            if "Dish Name" in self.df.columns:
                self.df = self._preprocess_new_dataset(self.df)
        except FileNotFoundError:
            # Fallback to old default if new file not found (for safety)
            self.df = pd.read_csv("food_data.csv")
            
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
            bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
        else:
            bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
        return bmr

    def recommend(self, age, weight, height, gender, activity_level, veg_preference, goal):
        bmr = self.calculate_bmr(weight, height, age, gender)
        
        activity_multipliers = {
            "sedentary": 1.2,
            "light": 1.375,
            "moderate": 1.55,
            "active": 1.725,
            "extra_active": 1.9
        }
        tdee = bmr * activity_multipliers.get(activity_level, 1.2)
        
        # Adjust for Goal based on provided equations
        if goal == "weight_loss":
            # Image says TDEE - 300 to 500. We use 500.
            # User Constraint: Target must be < BMR
            target_loss = tdee - 500
            if target_loss >= bmr:
                 tdee = bmr - 100
            else:
                 tdee = target_loss
        elif goal == "weight_gain":
            # Image says TDEE + 200 to 400. We use 300.
            tdee += 300
        
        if tdee < 1200: tdee = 1200
        
        targets = {
            "Breakfast": tdee * 0.25,
            "Lunch": tdee * 0.35,
            "Dinner": tdee * 0.30,
            "Snack": tdee * 0.10
        }
        
        recommendations = {}
        
        if veg_preference == "Veg":
            filtered_df = self.df[self.df['Type'] == 'Veg']
            sides_pool = self.sides_df[self.sides_df['Type'] == 'Veg']
        else:
            filtered_df = self.df 
            sides_pool = self.sides_df
        
        used_dishes = set()

        for meal, target_cal in targets.items():
            # Filter out already used dishes
            meal_df = filtered_df[
                (filtered_df['Meal_Type'] == meal) & 
                (~filtered_df['Name'].isin(used_dishes))
            ].copy()
            
            # If we ran out of unique options, fall back to full list
            if meal_df.empty:
                 meal_df = filtered_df[filtered_df['Meal_Type'] == meal].copy()

            if meal_df.empty:
                recommendations[meal] = None
                continue
            
            current_meal_cal_target = target_cal
            side_dish = None
            
            # Add a Side/Beverage to Lunch and Dinner (80% chance)
            if meal in ["Lunch", "Dinner"] and not sides_pool.empty:
                if random.random() < 0.8:
                    # Pick a random side
                    side_row = sides_pool.sample(1).iloc[0]
                    side_dish = side_row.to_dict()
                    current_meal_cal_target -= side_dish['Calories']
            
            # Logic for Lunch/Dinner to include staples
            if meal in ["Lunch", "Dinner"]:
                # 70% chance to pick a Gravy/Dry dish that needs a staple
                if random.random() < 0.7:
                    sub_df = meal_df[meal_df['Category'].isin(['Gravy', 'Dry'])]
                    if not sub_df.empty:
                        # Target for main dish is roughly 50-60% of remaining calories
                        main_target = current_meal_cal_target * 0.6
                        
                        best_match = self._find_closest(sub_df, main_target)
                        
                        # Calculate remaining calories for staple
                        remaining_cal = current_meal_cal_target - best_match['Calories']
                        
                        # Choose staple
                        staple_name = "Steamed Rice (1 cup)" if "Rice" in best_match['Name'] or "Fish" in best_match['Name'] else "Chapati"
                        staple_stats = self.staples[staple_name]
                        
                        # Calculate quantity
                        qty = max(1, round(remaining_cal / staple_stats['Calories'], 1))
                        qty = round(qty * 2) / 2
                        if qty < 1: qty = 1
                        
                        extra_dish = None
                        
                        # Cap Chapatis at 4
                        if staple_name == "Chapati" and qty > 4:
                            # Cap at 4
                            qty = 4
                            # Calculate deficit
                            cal_covered = 4 * staple_stats['Calories']
                            deficit = remaining_cal - cal_covered
                            
                            if deficit > 100: # Only add extra if deficit is significant
                                # Strategy: 50% chance for RiceSide (Pulao), 50% for 2nd Veg
                                rice_sides = meal_df[meal_df['Category'] == 'RiceSide']
                                other_veg = meal_df[meal_df['Category'].isin(['Gravy', 'Dry'])]
                                
                                # Filter out the already picked main dish from other_veg
                                other_veg = other_veg[other_veg['Name'] != best_match['Name']]
                                
                                if not rice_sides.empty and (random.random() < 0.5 or other_veg.empty):
                                    # Add RiceSide (Pulao)
                                    # Find closest to deficit
                                    extra_dish = self._find_closest(rice_sides, deficit).to_dict()
                                elif not other_veg.empty:
                                    # Add 2nd Vegetable
                                    extra_dish = self._find_closest(other_veg, deficit).to_dict()
                        
                        # Format quantity string
                        if "Rice" in staple_name:
                             qty_str = f"{qty} cups"
                             display_staple = "Steamed Rice"
                        else:
                             qty_int = int(qty) if qty.is_integer() else qty
                             qty_str = f"{qty_int} Chapatis" if qty > 1 else f"{qty_int} Chapati"
                             display_staple = "" 

                        name_str = f"{best_match['Name']} + {qty_str} {display_staple}".strip()
                        
                        if extra_dish:
                            name_str += f" + {extra_dish['Name']}"
                            used_dishes.add(extra_dish['Name'])
                        
                        # Add side to name if present
                        if side_dish:
                            name_str += f" + {side_dish['Name']}"

                        # Combine stats
                        total_cal = best_match['Calories'] + (qty * staple_stats['Calories'])
                        total_prot = best_match['Proteins'] + (qty * staple_stats['Proteins'])
                        total_fat = best_match['Fats'] + (qty * staple_stats['Fats'])
                        total_carb = best_match['Carbs'] + (qty * staple_stats['Carbs'])
                        
                        if extra_dish:
                            total_cal += extra_dish['Calories']
                            total_prot += extra_dish['Proteins']
                            total_fat += extra_dish['Fats']
                            total_carb += extra_dish['Carbs']

                        if side_dish:
                            total_cal += side_dish['Calories']
                            total_prot += side_dish['Proteins']
                            total_fat += side_dish['Fats']
                            total_carb += side_dish['Carbs']
                        
                        used_dishes.add(best_match['Name'])
                        recommendations[meal] = {
                            "Name": name_str,
                            "Type": best_match['Type'],
                            "Calories": int(total_cal),
                            "Proteins": int(total_prot),
                            "Fats": int(total_fat),
                            "Carbs": int(total_carb),
                            "Meal_Type": meal
                        }
                        continue

            # Fallback
            # For Breakfast, pick randomly from top 3 closest to ensure variety
            if meal == "Breakfast":
                X = meal_df[['Calories']].values
                nbrs = NearestNeighbors(n_neighbors=min(3, len(meal_df)), algorithm='ball_tree').fit(X)
                distances, indices = nbrs.kneighbors([[current_meal_cal_target]])
                
                # Pick random index from the top k neighbors
                random_idx = random.choice(indices[0])
                best_match = meal_df.iloc[random_idx]
            else:
                best_match = self._find_closest(meal_df, current_meal_cal_target)
            
            used_dishes.add(best_match['Name'])
            
            name_str = best_match['Name']
            total_cal = best_match['Calories']
            total_prot = best_match['Proteins']
            total_fat = best_match['Fats']
            total_carb = best_match['Carbs']
            
            if side_dish and meal in ["Lunch", "Dinner"]:
                name_str += f" + {side_dish['Name']}"
                total_cal += side_dish['Calories']
                total_prot += side_dish['Proteins']
                total_fat += side_dish['Fats']
                total_carb += side_dish['Carbs']

            recommendations[meal] = {
                "Name": name_str,
                "Type": best_match['Type'],
                "Calories": int(total_cal),
                "Proteins": int(total_prot),
                "Fats": int(total_fat),
                "Carbs": int(total_carb),
                "Meal_Type": meal,
                "Category": best_match['Category']
            }
        
        # Calculate actual total calories
        total_plan_calories = sum(m['Calories'] for m in recommendations.values() if m)

        return {
            "BMR": round(bmr, 2),
            "TDEE": round(tdee, 2),
            "TotalCalories": total_plan_calories,
            "Plan": recommendations
        }

    def _find_closest(self, df, target_cal):
        X = df[['Calories']].values
        nbrs = NearestNeighbors(n_neighbors=1, algorithm='ball_tree').fit(X)
        distances, indices = nbrs.kneighbors([[target_cal]])
        best_match_idx = indices[0][0]
        return df.iloc[best_match_idx]
