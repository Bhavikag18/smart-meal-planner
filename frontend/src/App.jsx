import React, { useState } from 'react';
import axios from 'axios';
import Form from './components/Form';
import Result from './components/Result';
import './index.css';

function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (formData) => {
    setLoading(true);
    setResult(null);
    try {
      const response = await axios.post('http://localhost:8000/recommend', {
        age: parseInt(formData.age),
        weight: parseFloat(formData.weight),
        height: parseFloat(formData.height),
        gender: formData.gender,
        activity: formData.activity,
        preference: formData.preference,
        goal: formData.goal
      });
      setResult(response.data);
    } catch (error) {
      console.error('Error fetching recommendation:', error);
      alert('Failed to get recommendation. Please ensure backend is running.');
    }
    setLoading(false);
  };

  return (
    <div className="container">
      <h1>Smart Diet Recommender</h1>
      <Form onSubmit={handleSubmit} />
      {loading && <div className="loading">Calculating your perfect plan...</div>}
      <Result data={result} />
    </div>
  );
}

export default App;
