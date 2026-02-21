import React, { useState } from 'react';
import axios from 'axios';

const ColGenSolver = () => {
  const [rollLength, setRollLength] = useState(15);
  const [demands, setDemands] = useState("[[3, 25], [5, 20], [7, 15]]");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [copied, setCopied] = useState(false);

  const handleCopyLogs = () => {
    if (!result?.logs) return;
    const text = result.logs.join('\n');
    navigator.clipboard.writeText(text).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }).catch(err => {
      console.error('Failed to copy logs:', err);
    });
  };

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
    <div className="glass-panel p-6">
      <h2 className="text-2xl font-bold mb-6 text-cyan-100">Column Generation (Cutting Stock)</h2>
      <div className="mb-4">
        <label htmlFor="colgen-roll-length" className="block text-sm font-medium text-slate-300 mb-2">Roll Length:</label>
        <input
          id="colgen-roll-length"
          type="number"
          value={rollLength}
          onChange={e => setRollLength(e.target.value)}
          className="glass-input w-full"
        />
      </div>
      <div className="mb-4">
        <label htmlFor="colgen-demands" className="block text-sm font-medium text-slate-300 mb-2">Demands (Width, Quantity):</label>
        <textarea
          id="colgen-demands"
          rows="3"
          value={demands}
          onChange={e => setDemands(e.target.value)}
          placeholder="[[width, qty], ...]"
          className="glass-input w-full font-mono"
        />
      </div>
      <button
        className="glass-btn-primary w-full md:w-auto flex items-center justify-center gap-2"
        onClick={solveColGen}
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
        ) : 'Solve Cutting Stock'}
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
              <span className="text-lg font-semibold text-green-400">{result.status}</span>
            </div>
            <div className="bg-white/5 p-4 rounded-lg">
              <span className="text-slate-400 block text-sm">Rolls Used (LP Relaxation)</span>
              <span className="text-lg font-semibold text-white">{result.objective.toFixed(2)}</span>
            </div>
          </div>

          <h4 className="text-lg font-semibold mb-3 text-slate-200">Patterns Generated</h4>
          <ul className="space-y-2 mb-6">
            {result.patterns.map((pat, idx) => (
              <li key={idx} className="bg-white/5 p-3 rounded flex justify-between items-center border border-white/10">
                <span className="text-cyan-200">Pattern {idx + 1}: {JSON.stringify(pat)}</span>
                <span className="text-slate-400 text-sm">x_{idx + 1} = {result.solution[idx]?.toFixed(2)}</span>
              </li>
            ))}
          </ul>

          <div className="flex justify-between items-center mb-2">
            <h4 className="text-lg font-semibold text-slate-200">Logs</h4>
            <button
              onClick={handleCopyLogs}
              className="text-xs bg-white/10 hover:bg-white/20 text-cyan-300 px-2 py-1 rounded transition-colors"
              aria-label={copied ? "Copied logs to clipboard" : "Copy logs to clipboard"}
            >
              {copied ? "Copied!" : "Copy Logs"}
            </button>
          </div>
          <pre className="bg-black/30 p-4 rounded-lg border border-white/10 text-slate-400 text-sm overflow-y-auto max-h-60 font-mono">
            {result.logs.join('\n')}
          </pre>
        </div>
      )}
    </div>
  );
};

export default ColGenSolver;
