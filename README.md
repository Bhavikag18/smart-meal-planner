# Smart Diet Recommender 🥗

A personalized diet recommendation application that uses Machine Learning to generate realistic Indian meal plans based on your body metrics and preferences.

## 🌟 Features
- **Personalized Calorie Targets**: Calculates BMR (Basal Metabolic Rate) and TDEE (Total Daily Energy Expenditure) using the Mifflin-St Jeor Equation.
- **Smart Meal Composition**:
  - Combines Gravies/Curries with Staples (Roti/Rice).
  - **Intelligent Portion Control**: Calculates exact quantity of Chapatis/Rice needed.
  - **Realistic Limits**: Caps Chapatis at 4 and adds extra sides (Pulao, 2nd Sabzi) if more calories are needed.
  - **Complete Meals**: Adds sides (Raita, Salad) and beverages (Chaas, Lassi) to make meals wholesome.
- **Variety**: Ensures Lunch and Dinner are never the same dish in one day.
- **Modern UI**: Beautiful Glassmorphism design.

## 🚀 How to Run (Step-by-Step)

### Prerequisites
- **Python** (for the backend)
- **Node.js** (for the frontend)

### 1. Start the Backend (The Brain)
The backend handles the logic and ML calculations.

1.  Open a terminal/command prompt.
2.  Navigate to the project folder:
    ```bash
    cd smart-diet-recommender
    ```
3.  Go into the backend folder:
    ```bash
    cd backend
    ```
4.  Install the required Python libraries:
    ```bash
    pip install -r requirements.txt
    ```
5.  Start the server:
    ```bash
    uvicorn main:app --reload
    ```
    *You should see "Application startup complete". The server is now running at `http://localhost:8000`.*

### 2. Start the Frontend (The Interface)
The frontend is the website you interact with.

1.  Open a **new** terminal window (keep the backend running!).
2.  Navigate to the frontend folder:
    ```bash
    cd smart-diet-recommender/frontend
    ```
3.  Install the required JavaScript libraries:
    ```bash
    npm install
    ```
4.  Start the website:
    ```bash
    npm run dev
    ```
    *It will show a URL like `http://localhost:5173`. Open this in your browser.*

---

## 📂 Project Structure (What are these files?)

### `backend/` (Python)
- **`main.py`**: The entry point of the API. It receives data from the frontend and asks the Recommender for a plan.
- **`recommender.py`**: The "Brain" of the project.
    - Calculates Calories.
    - Uses **K-Nearest Neighbors (KNN)** to find food matches.
    - Contains the logic for combining Roti/Rice, adding sides, and ensuring variety.
- **`data_generator.py`**: A script that creates the `food_data.csv` file. It generates a dataset of Indian foods with nutrition info.
- **`food_data.csv`**: The database of foods (Calories, Protein, Carbs, Fats, Category).
- **`requirements.txt`**: List of Python libraries needed.

### `frontend/` (React + Vite)
- **`src/App.jsx`**: The main page of the website.
- **`src/components/Form.jsx`**: The input form where you enter Age, Weight, etc.
- **`src/components/Result.jsx`**: The card that displays your generated diet plan.
- **`src/index.css`**: Contains all the styling (colors, glass effect, animations).

---

## 🧠 Algorithms & Logic Used

### 1. Calorie Calculation (Mifflin-St Jeor Equation)
Before using ML, we need to know *how much* you should eat.
- **BMR**: Calories burned at rest.
- **TDEE**: BMR × Activity Level (Sedentary, Active, etc.).
- We split this TDEE into meals: Breakfast (25%), Lunch (35%), Dinner (30%), Snack (10%).

### 2. K-Nearest Neighbors (KNN)
This is the core ML algorithm.
- We treat every food item as a point in space based on its **Calories**.
- When we need a 500-calorie lunch, KNN searches the `food_data.csv` to find the food item that is mathematically "closest" to 500 calories.

### 3. Heuristic Logic (The "Smart" Part)
Raw ML isn't enough for realistic meals. We added custom logic:
- **Combination**: If KNN picks "Paneer Butter Masala" (300 cal) for a 700 cal target, the code calculates the gap (400 cal) and fills it with Staples (4 Chapatis).
- **Constraints**: If the gap requires 8 Chapatis, we cap it at 4 and trigger a "Side Dish Search" to fill the remaining calories with Pulao or a second vegetable.
- **Variety Filter**: We use a `Set` data structure to remember "Paneer Butter Masala" was used for Lunch, so KNN is forced to pick a different neighbor for Dinner.
