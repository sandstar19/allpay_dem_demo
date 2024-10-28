import React, { useState } from 'react';

function PredictionForm() {
  const [formData, setFormData] = useState({
    Company: '',
    Vendor: '',
    PO: '',
    Material: '',
    MatGroup: '',
    Plant: '',
  });
  const [predictions, setPredictions] = useState(null);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const response = await fetch('http://localhost:5000/predict_Email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        throw new Error('Failed to fetch predictions');
      }

      const data = await response.json();
      setPredictions(data);
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="form-container">
      <h1>prediction form</h1>
      <form className="predict-form" onSubmit={handleSubmit}>
        <label>Company Code:</label>
        <input
          type="text"
          name="Company"
          placeholder="Company"
          value={formData.Company}
          onChange={handleChange}
          required
        />
        <label>Vendor Code:</label>
        <input
          type="text"
          name="Vendor"
          placeholder="Vendor"
          value={formData.Vendor}
          onChange={handleChange}
          required
        />
        <label>Purchase Order Number:</label>
        <input
          type="text"
          name="PO"
          placeholder="PO"
          value={formData.PO}
          onChange={handleChange}
          required
        />
        <label>Material Code:</label>
        <input
          type="text"
          name="Material"
     
          value={formData.Material}
          onChange={handleChange}
          required
        />
        <label>Mat Group:</label>
        <input
          type="text"
          name="MatGroup"
       
          value={formData.MatGroup}
          onChange={handleChange}
          required
        />
        <label>Plant Code:</label>
        <input
          type="text"
          name="Plant"
       
          value={formData.Plant}
          onChange={handleChange}
          required
        />
        <button type="submit">Get Email</button>
      </form>

      {error && <p className="error">{error}</p>}

      {predictions && (
        <div className="predictions">
          <h2>Predictions</h2>
          <p><strong>Email:</strong> {predictions.predicted_Email}</p>
          <p><strong>Name:</strong> {predictions.predicted_Name}</p>
          <h3>Detailed Scores</h3>
            <div className="scores">
                <div>
                    <h4>Email Scores</h4>
                    <ul>
                    {predictions.sorted_prediction_scores_Email.slice(0, 3).map((item, index) => (
                        <li key={index}>
                        {item.label}: {item.score.toFixed(2)}%
                        </li>
                    ))}
                    </ul>
                </div>
                <div>
                    <h4>Name Scores</h4>
                    <ul>
                    {predictions.sorted_prediction_scores_Name.slice(0, 3).map((item, index) => (
                        <li key={index}>
                        {item.label}: {item.score.toFixed(2)}%
                        </li>
                    ))}
                    </ul>
                </div>
            </div>
        </div>
      )}
    </div>
  );
}

export default PredictionForm;
