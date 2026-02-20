import React, { useState } from 'react';
import axios from 'axios';

const LPSolver = () => {
  const [c, setC] = useState("[3, 2]");
  const [A, setA] = useState("[[2, 1], [1, 1], [1, 0]]");
  const [b, setB] = useState("[100, 80, 40]");
  const [maximize, setMaximize] = useState(true);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const solveLP = async () => {
    setLoading(true);
    setError(null);
    try {
      const payload = {
        c: JSON.parse(c),
        A_ub: JSON.parse(A),
        b_ub: JSON.parse(b),
        maximize: maximize
      };

      const response = await axios.post('/api/lp', payload);
      setResult(response.data);
    } catch (err) {
      setError(err.message + (err.response ? ": " + JSON.stringify(err.response.data) : ""));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-panel p-6">
      <h2 className="text-2xl font-bold mb-6 text-cyan-100">Linear Programming Solver (Simplex/Interior Point)</h2>
      <div className="mb-4">
        <label htmlFor="lp-c" className="block text-sm font-medium text-slate-300 mb-2">Objective Coefficients (c):</label>
        <input
          id="lp-c"
          type="text"
          value={c}
          onChange={e => setC(e.target.value)}
          placeholder="[c1, c2]"
          className="glass-input w-full"
        />
      </div>
      <div className="mb-4">
        <label htmlFor="lp-A" className="block text-sm font-medium text-slate-300 mb-2">Constraint Matrix (A_ub):</label>
        <textarea
          id="lp-A"
          rows="3"
          value={A}
          onChange={e => setA(e.target.value)}
          placeholder="[[a11, a12], [a21, a22]]"
          className="glass-input w-full font-mono"
        />
      </div>
      <div className="mb-4">
        <label htmlFor="lp-b" className="block text-sm font-medium text-slate-300 mb-2">Constraint RHS (b_ub):</label>
        <input
          id="lp-b"
          type="text"
          value={b}
          onChange={e => setB(e.target.value)}
          placeholder="[b1, b2]"
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
        className="glass-btn-primary w-full md:w-auto flex items-center justify-center gap-2"
        onClick={solveLP}
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
        ) : 'Solve LP'}
      </button>

      {error && (
        <div role="alert" className="mt-4 p-4 bg-red-500/20 border border-red-500/50 rounded-lg text-red-200">
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

          {result.plot && (
            <div>
              <h4 className="text-lg font-semibold mb-3 text-slate-200">Feasible Region & Optimal Solution</h4>
              <img src={`data:image/png;base64,${result.plot}`} alt="LP Plot" className="w-full rounded-lg border border-white/20 shadow-lg" />
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default LPSolver;
