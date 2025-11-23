from fastapi import FastAPI
from pydantic import BaseModel
from recommender import DietRecommender
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize recommender
# Ensure data exists
if not os.path.exists("food_data.csv"):
    pass

recommender = DietRecommender(data_path="food_data.csv")

class UserInput(BaseModel):
    age: int
    weight: float
    height: float
    gender: str
    activity: str
    preference: str
    goal: str # Added goal field

@app.post("/recommend")
def get_recommendation(user_input: UserInput):
    plan = recommender.recommend(
        user_input.age,
        user_input.weight,
        user_input.height,
        user_input.gender,
        user_input.activity,
        user_input.preference,
        user_input.goal # Pass goal to recommender
    )
    return plan

@app.get("/")
def read_root():
    return {"message": "Smart Diet Recommender API is running"}
