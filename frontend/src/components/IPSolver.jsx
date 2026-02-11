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
    <div className="glass-panel p-6">
      <h2 className="text-2xl font-bold mb-6 text-cyan-100">Integer Programming (Branch and Bound)</h2>
      <div className="mb-4">
        <label className="block text-sm font-medium text-slate-300 mb-2">Objective Coefficients (c):</label>
        <input
          type="text"
          value={c}
          onChange={e => setC(e.target.value)}
          className="glass-input w-full"
        />
      </div>
      <div className="mb-4">
        <label className="block text-sm font-medium text-slate-300 mb-2">Constraint Matrix (A_ub):</label>
        <textarea
          rows="3"
          value={A}
          onChange={e => setA(e.target.value)}
          className="glass-input w-full font-mono"
        />
      </div>
      <div className="mb-4">
        <label className="block text-sm font-medium text-slate-300 mb-2">Constraint RHS (b_ub):</label>
        <input
          type="text"
          value={b}
          onChange={e => setB(e.target.value)}
          className="glass-input w-full"
        />
      </div>
      <div className="mb-6">
        <label className="flex items-center space-x-3 cursor-pointer">
          <input
            type="checkbox"
            checked={maximize}
            onChange={e => setMaximize(e.target.checked)}
            className="form-checkbox h-5 w-5 text-cyan-500 rounded border-gray-300 focus:ring-cyan-500 bg-white/10"
          />
          <span className="text-slate-300">Maximize Objective</span>
        </label>
      </div>
      <button
        className="glass-btn-primary w-full md:w-auto"
        onClick={solveIP}
        disabled={loading}
      >
        {loading ? 'Solving...' : 'Solve IP'}
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
              <span className={`text-lg font-semibold ${result.success ? 'text-green-400' : 'text-red-400'}`}>
                {result.success ? "Optimal" : "Failed"}
              </span>
            </div>
            <div className="bg-white/5 p-4 rounded-lg">
              <span className="text-slate-400 block text-sm">Objective Value</span>
              <span className="text-lg font-semibold text-white">{result.fun.toFixed(4)}</span>
            </div>
            <div className="col-span-1 md:col-span-2 bg-white/5 p-4 rounded-lg">
              <span className="text-slate-400 block text-sm">Solution (x)</span>
              <code className="text-cyan-300 font-mono">{JSON.stringify(result.x)}</code>
            </div>
          </div>

          {result.tree_plot && (
            <div>
              <h4 className="text-lg font-semibold mb-3 text-slate-200">Branch and Bound Tree</h4>
              <img src={`data:image/png;base64,${result.tree_plot}`} alt="B&B Tree" className="w-full rounded-lg border border-white/20 shadow-lg" />
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default IPSolver;
