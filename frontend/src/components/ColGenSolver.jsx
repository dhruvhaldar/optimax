import React, { useState } from 'react';
import axios from 'axios';

const ColGenSolver = () => {
  const [rollLength, setRollLength] = useState(15);
  const [demands, setDemands] = useState("[[3, 25], [5, 20], [7, 15]]");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const solveColGen = async () => {
    setLoading(true);
    setError(null);
    try {
      const payload = {
        roll_length: parseFloat(rollLength),
        demands: JSON.parse(demands)
      };

      const response = await axios.post('/api/colgen', payload);
      setResult(response.data);
    } catch (err) {
      setError(err.message + (err.response ? ": " + JSON.stringify(err.response.data) : ""));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h2>Column Generation (Cutting Stock)</h2>
      <div className="form-group">
        <label>Roll Length:</label>
        <input type="number" value={rollLength} onChange={e => setRollLength(e.target.value)} />
      </div>
      <div className="form-group">
        <label>Demands (Width, Quantity):</label>
        <textarea rows="3" value={demands} onChange={e => setDemands(e.target.value)} placeholder="[[width, qty], ...]" />
      </div>
      <button className="solve-btn" onClick={solveColGen} disabled={loading}>
        {loading ? 'Solving...' : 'Solve Cutting Stock'}
      </button>

      {error && <div style={{color: 'red', marginTop: '10px'}}>Error: {error}</div>}

      {result && (
        <div style={{marginTop: '20px'}}>
          <h3>Results</h3>
          <p>Status: {result.status}</p>
          <p>Rolls Used: {result.objective.toFixed(2)} (LP Relaxation)</p>
          <h4>Patterns Generated:</h4>
          <ul>
            {result.patterns.map((pat, idx) => (
              <li key={idx}>Pattern {idx + 1}: {JSON.stringify(pat)} (x_{idx+1} = {result.solution[idx]?.toFixed(2)})</li>
            ))}
          </ul>
          <h4>Logs:</h4>
          <pre style={{maxHeight: '200px', overflowY: 'scroll'}}>
            {result.logs.join('\n')}
          </pre>
        </div>
      )}
    </div>
  );
};

export default ColGenSolver;
