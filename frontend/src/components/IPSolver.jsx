import React, { useState } from 'react';
import axios from 'axios';

const IPSolver = () => {
  const [c, setC] = useState("[5, 8]");
  const [A, setA] = useState("[[1, 1], [5, 9]]");
  const [b, setB] = useState("[6, 45]");
  const [maximize, setMaximize] = useState(true);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const solveIP = async () => {
    setLoading(true);
    setError(null);
    try {
      const payload = {
        c: JSON.parse(c),
        A_ub: JSON.parse(A),
        b_ub: JSON.parse(b),
        maximize: maximize
      };

      const response = await axios.post('/api/ip', payload);
      setResult(response.data);
    } catch (err) {
      setError(err.message + (err.response ? ": " + JSON.stringify(err.response.data) : ""));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h2>Integer Programming (Branch and Bound)</h2>
      <div className="form-group">
        <label>Objective Coefficients (c):</label>
        <input type="text" value={c} onChange={e => setC(e.target.value)} />
      </div>
      <div className="form-group">
        <label>Constraint Matrix (A_ub):</label>
        <textarea rows="3" value={A} onChange={e => setA(e.target.value)} />
      </div>
      <div className="form-group">
        <label>Constraint RHS (b_ub):</label>
        <input type="text" value={b} onChange={e => setB(e.target.value)} />
      </div>
      <div className="form-group">
        <label>
          <input type="checkbox" checked={maximize} onChange={e => setMaximize(e.target.checked)} /> Maximize Objective
        </label>
      </div>
      <button className="solve-btn" onClick={solveIP} disabled={loading}>
        {loading ? 'Solving...' : 'Solve IP'}
      </button>

      {error && <div style={{color: 'red', marginTop: '10px'}}>Error: {error}</div>}

      {result && (
        <div style={{marginTop: '20px'}}>
          <h3>Results</h3>
          <p>Status: {result.success ? "Optimal" : "Failed"}</p>
          <p>Objective Value: {result.fun.toFixed(4)}</p>
          <p>Solution (x): {JSON.stringify(result.x)}</p>
          {result.tree_plot && (
            <div>
              <h4>Branch and Bound Tree</h4>
              <img src={`data:image/png;base64,${result.tree_plot}`} alt="B&B Tree" className="result-image" />
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default IPSolver;
