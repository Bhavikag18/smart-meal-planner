from recommender import DietRecommender
import os

# Ensure we find the file
path = "backend/food_data.csv" if os.path.exists("backend/food_data.csv") else "food_data.csv"
r = DietRecommender(path)
print(r.recommend(25, 70, 175, "male", "moderate", "Veg"))
