import React, { useState } from 'react';
import axios from 'axios';

const StochasticSolver = () => {
  const [land, setLand] = useState(500);
  const [scenarios, setScenarios] = useState(JSON.stringify([
    {
      name: "Good",
      probability: 0.33,
      yields: [3.0, 3.6, 24.0]
    },
    {
      name: "Average",
      probability: 0.33,
      yields: [2.5, 3.0, 20.0]
    },
    {
      name: "Bad",
      probability: 0.34,
      yields: [2.0, 2.4, 16.0]
    }
  ], null, 2));
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const solveStochastic = async () => {
    setLoading(true);
    setError(null);
    try {
      const payload = {
        total_land: parseFloat(land),
        scenarios: JSON.parse(scenarios)
      };

      const response = await axios.post('/api/stochastic', payload);
      setResult(response.data);
    } catch (err) {
      setError(err.message + (err.response ? ": " + JSON.stringify(err.response.data) : ""));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h2>Stochastic Programming (Farmer's Problem)</h2>
      <div className="form-group">
        <label>Total Land (Acres):</label>
        <input type="number" value={land} onChange={e => setLand(e.target.value)} />
      </div>
      <div className="form-group">
        <label>Scenarios (Name, Prob, Yields [Wheat, Corn, Beets]):</label>
        <textarea rows="15" value={scenarios} onChange={e => setScenarios(e.target.value)} />
      </div>
      <button className="solve-btn" onClick={solveStochastic} disabled={loading}>
        {loading ? 'Solving...' : 'Solve Stochastic LP'}
      </button>

      {error && <div style={{color: 'red', marginTop: '10px'}}>Error: {error}</div>}

      {result && (
        <div style={{marginTop: '20px'}}>
          <h3>Results</h3>
          <p>Status: {result.success ? "Optimal" : "Failed"}</p>
          <p>Expected Profit: ${result.expected_profit?.toFixed(2)}</p>
          <p>Acres Allocation (x): {result.x ? `Wheat: ${result.x[0].toFixed(1)}, Corn: ${result.x[1].toFixed(1)}, Beets: ${result.x[2].toFixed(1)}` : "None"}</p>
          {result.plot && (
            <div>
              <h4>Decision & Profit Distribution</h4>
              <img src={`data:image/png;base64,${result.plot}`} alt="Stochastic Plots" className="result-image" />
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default StochasticSolver;
