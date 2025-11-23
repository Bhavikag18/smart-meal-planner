import React, { useState } from 'react';

const Form = ({ onSubmit }) => {
  const [formData, setFormData] = useState({
    age: '',
    weight: '',
    height: '',
    gender: 'male',
    activity: 'moderate',
    preference: 'Veg',
    goal: 'maintain' // Default goal
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="form-group">
        <label>Age (years)</label>
        <input type="number" name="age" value={formData.age} onChange={handleChange} required />
      </div>
      <div className="form-group">
        <label>Weight (kg)</label>
        <input type="number" name="weight" value={formData.weight} onChange={handleChange} required />
      </div>
      <div className="form-group">
        <label>Height (cm)</label>
        <input type="number" name="height" value={formData.height} onChange={handleChange} required />
      </div>
      <div className="form-group">
        <label>Gender</label>
        <select name="gender" value={formData.gender} onChange={handleChange}>
          <option value="male">Male</option>
          <option value="female">Female</option>
        </select>
      </div>
      <div className="form-group">
        <label>Activity Level</label>
        <select name="activity" value={formData.activity} onChange={handleChange}>
          <option value="sedentary">Sedentary (little or no exercise)</option>
          <option value="light">Lightly active (light exercise/sports 1-3 days/week)</option>
          <option value="moderate">Moderately active (moderate exercise/sports 3-5 days/week)</option>
          <option value="active">Very active (hard exercise/sports 6-7 days/week)</option>
          <option value="extra_active">Extra active (heavy training/physical job)</option>
        </select>
      </div>
      <div className="form-group">
        <label>Goal</label>
        <select name="goal" value={formData.goal} onChange={handleChange}>
          <option value="maintain">Maintain Weight</option>
          <option value="weight_loss">Weight Loss</option>
          <option value="weight_gain">Weight Gain</option>
        </select>
      </div>
      <div className="form-group">
        <label>Food Preference</label>
        <select name="preference" value={formData.preference} onChange={handleChange}>
          <option value="Veg">Vegetarian</option>
          <option value="Non-Veg">Non-Vegetarian</option>
        </select>
      </div>
      <button type="submit">Get My Diet Plan</button>
    </form>
  );
};

export default Form;
