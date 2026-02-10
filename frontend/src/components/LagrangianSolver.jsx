import React, { useState } from 'react';
import axios from 'axios';

const LagrangianSolver = () => {
  const [costs, setCosts] = useState("[[10, 20], [15, 10], [5, 5]]");
  const [weights, setWeights] = useState("[[2, 5], [3, 2], [1, 1]]");
  const [capacities, setCapacities] = useState("[5, 5]");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const solveLagrangian = async () => {
    setLoading(true);
    setError(null);
    try {
      const payload = {
        costs: JSON.parse(costs),
        weights: JSON.parse(weights),
        capacities: JSON.parse(capacities)
      };

      const response = await axios.post('/api/lagrangian', payload);
      setResult(response.data);
    } catch (err) {
      setError(err.message + (err.response ? ": " + JSON.stringify(err.response.data) : ""));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h2>Lagrangian Relaxation (Generalized Assignment)</h2>
      <div className="form-group">
        <label>Costs (Task x Agent):</label>
        <textarea rows="3" value={costs} onChange={e => setCosts(e.target.value)} placeholder="[[c11, c12], [c21, c22]]" />
      </div>
      <div className="form-group">
        <label>Weights (Task x Agent):</label>
        <textarea rows="3" value={weights} onChange={e => setWeights(e.target.value)} placeholder="[[w11, w12], [w21, w22]]" />
      </div>
      <div className="form-group">
        <label>Agent Capacities:</label>
        <input type="text" value={capacities} onChange={e => setCapacities(e.target.value)} placeholder="[C1, C2]" />
      </div>
      <button className="solve-btn" onClick={solveLagrangian} disabled={loading}>
        {loading ? 'Solving...' : 'Solve Lagrangian'}
      </button>

      {error && <div style={{color: 'red', marginTop: '10px'}}>Error: {error}</div>}

      {result && (
        <div style={{marginTop: '20px'}}>
          <h3>Results</h3>
          <p>Status: {result.status}</p>
          <p>Final Lower Bound: {result.lb_history[result.lb_history.length - 1].toFixed(2)}</p>
          <p>Best Upper Bound (Feasible): {result.ub ? result.ub.toFixed(2) : "None"}</p>
          <p>Best Solution (Feasible): {result.best_solution ? JSON.stringify(result.best_solution) : "None"}</p>
          {result.plot && (
            <div>
              <h4>Lower Bound Convergence</h4>
              <img src={`data:image/png;base64,${result.plot}`} alt="Lagrangian Convergence" className="result-image" />
            </div>
          )}
          <h4>Logs:</h4>
          <pre style={{maxHeight: '200px', overflowY: 'scroll'}}>
            {result.logs.join('\n')}
          </pre>
        </div>
      )}
    </div>
  );
};

export default LagrangianSolver;
