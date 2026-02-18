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
    <div className="glass-panel p-6">
      <h2 className="text-2xl font-bold mb-6 text-cyan-100">Stochastic Programming (Farmer's Problem)</h2>
      <div className="mb-4">
        <label htmlFor="stochastic-land" className="block text-sm font-medium text-slate-300 mb-2">Total Land (Acres):</label>
        <input
          id="stochastic-land"
          type="number"
          value={land}
          onChange={e => setLand(e.target.value)}
          className="glass-input w-full"
        />
      </div>
      <div className="mb-4">
        <label htmlFor="stochastic-scenarios" className="block text-sm font-medium text-slate-300 mb-2">Scenarios (Name, Prob, Yields [Wheat, Corn, Beets]):</label>
        <textarea
          id="stochastic-scenarios"
          rows="15"
          value={scenarios}
          onChange={e => setScenarios(e.target.value)}
          className="glass-input w-full font-mono text-sm leading-relaxed"
        />
      </div>
      <button
        className="glass-btn-primary w-full md:w-auto flex items-center justify-center gap-2"
        onClick={solveStochastic}
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
        ) : 'Solve Stochastic LP'}
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
              <span className="text-slate-400 block text-sm">Expected Profit</span>
              <span className="text-lg font-semibold text-white">${result.expected_profit?.toFixed(2)}</span>
            </div>
            <div className="col-span-1 md:col-span-2 bg-white/5 p-4 rounded-lg">
              <span className="text-slate-400 block text-sm">Acres Allocation</span>
              <span className="text-lg font-semibold text-cyan-300">
                {result.x ? `Wheat: ${result.x[0].toFixed(1)}, Corn: ${result.x[1].toFixed(1)}, Beets: ${result.x[2].toFixed(1)}` : "None"}
              </span>
            </div>
          </div>

          {result.plot && (
            <div>
              <h4 className="text-lg font-semibold mb-3 text-slate-200">Decision & Profit Distribution</h4>
              <img src={`data:image/png;base64,${result.plot}`} alt="Stochastic Plots" className="w-full rounded-lg border border-white/20 shadow-lg" />
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default StochasticSolver;
