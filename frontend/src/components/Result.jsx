import React from 'react';

const Result = ({ data }) => {
  if (!data) return null;

  return (
    <div className="result-card">
      <h2>Your Personalized Diet Plan</h2>
      <div className="stats-grid">
        <div className="stat-box">
          <div>BMR</div>
          <div className="stat-value">{data.BMR}</div>
          <div>kcal/day</div>
        </div>
        <div className="stat-box">
          <div>Target Calories</div>
          <div className="stat-value">{data.TDEE}</div>
          <div>kcal/day</div>
        </div>
        <div className="stat-box">
          <div>Plan Total</div>
          <div className="stat-value">{data.TotalCalories}</div>
          <div>kcal/day</div>
        </div>
      </div>

      <h3>Recommended Meals</h3>
      {Object.entries(data.Plan).map(([mealType, meal]) => (
        <div key={mealType} className="meal-item">
          <div className="meal-name">
            {mealType}: {meal ? meal.Name : 'No recommendation found'}
          </div>
          {meal && (
            <div className="meal-stats">
              {meal.Calories} kcal | P: {meal.Proteins}g | F: {meal.Fats}g | C: {meal.Carbs}g
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

export default Result;
