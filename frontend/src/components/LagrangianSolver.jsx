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
    <div className="glass-panel p-6">
      <h2 className="text-2xl font-bold mb-6 text-cyan-100">Lagrangian Relaxation (Generalized Assignment)</h2>
      <div className="mb-4">
        <label htmlFor="lagrangian-costs" className="block text-sm font-medium text-slate-300 mb-2">Costs (Task x Agent):</label>
        <textarea
          id="lagrangian-costs"
          rows="3"
          value={costs}
          onChange={e => setCosts(e.target.value)}
          placeholder="[[c11, c12], [c21, c22]]"
          className="glass-input w-full font-mono"
        />
      </div>
      <div className="mb-4">
        <label htmlFor="lagrangian-weights" className="block text-sm font-medium text-slate-300 mb-2">Weights (Task x Agent):</label>
        <textarea
          id="lagrangian-weights"
          rows="3"
          value={weights}
          onChange={e => setWeights(e.target.value)}
          placeholder="[[w11, w12], [w21, w22]]"
          className="glass-input w-full font-mono"
        />
      </div>
      <div className="mb-4">
        <label htmlFor="lagrangian-capacities" className="block text-sm font-medium text-slate-300 mb-2">Agent Capacities:</label>
        <input
          id="lagrangian-capacities"
          type="text"
          value={capacities}
          onChange={e => setCapacities(e.target.value)}
          placeholder="[C1, C2]"
          className="glass-input w-full"
        />
      </div>
      <button
        className="glass-btn-primary w-full md:w-auto flex items-center justify-center gap-2"
        onClick={solveLagrangian}
        disabled={loading}
        aria-busy={loading}
      >
        {loading ? (
          <>
            <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Solving...
          </>
        ) : 'Solve Lagrangian'}
      </button>

      {error && (
        <div className="mt-4 p-4 bg-red-500/20 border border-red-500/50 rounded-lg text-red-200">
          Error: {error}
        </div>
      )}

      {result && (
        <div className="mt-8 p-6 bg-black/20 rounded-xl border border-white/5">
          <h3 className="text-xl font-bold mb-4 text-white">Results</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div className="bg-white/5 p-4 rounded-lg">
              <span className="text-slate-400 block text-sm">Status</span>
              <span className="text-lg font-semibold text-green-400">{result.status}</span>
            </div>
            <div className="bg-white/5 p-4 rounded-lg">
              <span className="text-slate-400 block text-sm">Final Lower Bound</span>
              <span className="text-lg font-semibold text-white">{result.lb_history[result.lb_history.length - 1].toFixed(2)}</span>
            </div>
            <div className="bg-white/5 p-4 rounded-lg">
              <span className="text-slate-400 block text-sm">Best Upper Bound (Feasible)</span>
              <span className="text-lg font-semibold text-white">{result.ub ? result.ub.toFixed(2) : "None"}</span>
            </div>
            <div className="bg-white/5 p-4 rounded-lg">
              <span className="text-slate-400 block text-sm">Best Solution</span>
              <code className="text-cyan-300 font-mono text-sm">{result.best_solution ? JSON.stringify(result.best_solution) : "None"}</code>
            </div>
          </div>

          {result.plot && (
            <div className="mb-6">
              <h4 className="text-lg font-semibold mb-3 text-slate-200">Lower Bound Convergence</h4>
              <img src={`data:image/png;base64,${result.plot}`} alt="Lagrangian Convergence" className="w-full rounded-lg border border-white/20 shadow-lg" />
            </div>
          )}

          <h4 className="text-lg font-semibold mb-2 text-slate-200">Logs</h4>
          <pre className="bg-black/30 p-4 rounded-lg border border-white/10 text-slate-400 text-sm overflow-y-auto max-h-60 font-mono">
            {result.logs.join('\n')}
          </pre>
        </div>
      )}
    </div>
  );
};

export default LagrangianSolver;
