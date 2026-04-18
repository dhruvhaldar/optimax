import React, { useState } from 'react';
import axios from 'axios';
import { useOsShortcut } from '../hooks/useOsShortcut';
import { useResultFocus } from '../hooks/useResultFocus';

const ColGenSolver = () => {
  const { shortcutSymbol, shortcutText } = useOsShortcut();
  const [rollLength, setRollLength] = useState(15);
  const [demands, setDemands] = useState("[[3, 25], [5, 20], [7, 15]]");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [copied, setCopied] = useState(false);

  const resultRef = useResultFocus(loading, result);

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
    if (loading) return;
    setLoading(true);
    setError(null);
    let payload;
    try {
      payload = {
        roll_length: parseFloat(rollLength),
        demands: JSON.parse(demands)
      };
    } catch (err) {
      setError("Invalid input format. Please ensure demands are formatted as a valid JSON matrix (e.g., [[3, 25], [5, 20]]).");
      setLoading(false);
      return;
    }

    try {
      const response = await axios.post('/api/colgen', payload);
      setResult(response.data);
    } catch (err) {
      setError(err.message + (err.response ? ": " + JSON.stringify(err.response.data) : ""));
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
      e.preventDefault();
      if (!loading) {
        e.currentTarget.requestSubmit();
      }
    }
  };

  return (
    <form aria-labelledby="solver-title" className="glass-panel p-6" onKeyDown={handleKeyDown} onSubmit={e => { e.preventDefault(); if (!loading) solveColGen(); }}>
      <h2 id="solver-title" className="text-2xl font-bold mb-6 text-cyan-100">Column Generation (Cutting Stock)</h2>
      <div className="mb-4">
        <label htmlFor="colgen-roll-length" className="block text-sm font-medium text-slate-300 mb-2">Roll Length <span className="text-red-400" aria-hidden="true">*</span>:</label>
        <input
          id="colgen-roll-length"
          type="number"
          step="any"
          min="0"
          value={rollLength}
          onChange={e => setRollLength(e.target.value)}
          placeholder="e.g. 15"
          disabled={loading} required className="glass-input w-full disabled:opacity-50 disabled:cursor-not-allowed"
        />
      </div>
      <div className="mb-4">
        <label htmlFor="colgen-demands" className="block text-sm font-medium text-slate-300 mb-2">Demands (Width, Quantity) <span className="text-red-400" aria-hidden="true">*</span>:</label>
        <textarea
          id="colgen-demands"
          rows="3"
          value={demands}
          onChange={e => setDemands(e.target.value)}
          placeholder="[[width, qty], ...]"
          spellCheck={false}
          autoComplete="off"
          autoCorrect="off"
          autoCapitalize="none"
          disabled={loading} required className="glass-input w-full font-mono disabled:opacity-50 disabled:cursor-not-allowed"
        />
      </div>
      <button
        className={`glass-btn-primary w-full md:w-auto flex items-center justify-center gap-2 ${loading ? 'opacity-80 cursor-wait' : ''}`}
        type="submit"
        disabled={loading}
        aria-busy={loading}
        title={`Press ${shortcutText} to solve`}
      >
        {loading ? (
          <>
            <svg aria-hidden="true" className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Solving...
          </>
        ) : (
          <>
            Solve Cutting Stock <kbd aria-hidden="true" className="text-xs opacity-80 ml-2 font-mono hidden sm:inline px-1.5 py-0.5 bg-white/10 border border-white/20 rounded-md shadow-sm">{shortcutSymbol}</kbd>
          </>
        )}
      </button>

      {error && (
        <div role="alert" aria-live="assertive" className="mt-4 p-4 bg-red-500/20 border border-red-500/50 rounded-lg text-red-200">
          Error: {error}
        </div>
      )}

      {!result && !error && (
        <div className={`mt-8 p-8 bg-white/5 rounded-xl border border-dashed border-white/20 flex flex-col items-center justify-center text-slate-400 text-center transition-opacity duration-200 ${loading ? 'opacity-50' : ''}`}>
          <svg aria-hidden="true" className="w-12 h-12 mb-3 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          <p>Ready to optimize.</p>
          <p className="text-sm mt-1 opacity-75">Enter your parameters above and click <strong>Solve</strong> to generate the solution.</p>
        </div>
      )}

      {result && (
        <div className={`mt-8 p-6 bg-black/20 rounded-xl border border-white/5 transition-opacity duration-200 ${loading ? 'opacity-50 pointer-events-none' : ''}`}>
          <h3
            className="text-xl font-bold mb-4 text-white focus:outline-none focus-visible:ring-2 focus-visible:ring-cyan-400 rounded-sm"
            tabIndex="-1"
            ref={resultRef}
          >
            Results
          </h3>
          <dl className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div className="bg-white/5 p-4 rounded-lg">
              <dt className="text-slate-400 block text-sm">Status</dt>
              <dd className="text-lg font-semibold text-green-400">{result.status}</dd>
            </div>
            <div className="bg-white/5 p-4 rounded-lg">
              <dt className="text-slate-400 block text-sm">Rolls Used (LP Relaxation)</dt>
              <dd className="text-lg font-semibold text-white">{result.objective !== null && result.objective !== undefined ? result.objective.toFixed(2) : "N/A"}</dd>
            </div>
          </dl>

          <h4 className="text-lg font-semibold mb-3 text-slate-200">Patterns Generated</h4>
          <ul className="space-y-2 mb-6">
            {result.patterns.map((pat, idx) => (
              <li key={idx} className="bg-white/5 p-3 rounded flex flex-col sm:flex-row justify-between items-start sm:items-center border border-white/10 gap-2">
                <div className="flex-1 min-w-0 max-w-full">
                  <span className="text-slate-400 text-sm block mb-1">Pattern {idx + 1}:</span>
                  <code
                    className="text-cyan-200 font-mono overflow-x-auto block focus:outline-none focus-visible:ring-2 focus-visible:ring-cyan-400 rounded-sm"
                    tabIndex={0}
                    role="region"
                    aria-label={`Pattern ${idx + 1} configuration`}
                  >
                    {JSON.stringify(pat)}
                  </code>
                </div>
                <span className="text-slate-400 text-sm whitespace-nowrap shrink-0">x_{idx + 1} = {result.solution[idx]?.toFixed(2)}</span>
              </li>
            ))}
          </ul>

          <div className="flex justify-between items-center mb-2">
            <h4 className="text-lg font-semibold text-slate-200">Logs</h4>
            <button
              type="button"
              onClick={handleCopyLogs}
              className={`text-xs px-2 py-1 rounded transition-colors focus:outline-none focus-visible:ring-2 ${copied ? 'bg-green-500/20 hover:bg-green-500/30 text-green-300 focus-visible:ring-green-400' : 'bg-white/10 hover:bg-white/20 text-cyan-300 focus-visible:ring-cyan-400'}`}
              aria-label={copied ? "Copied logs to clipboard" : "Copy logs to clipboard"}
            >
              {copied ? "Copied!" : "Copy Logs"}
            </button>
            <span aria-live="polite" className="sr-only">{copied ? "Copied to clipboard" : ""}</span>
          </div>
          <pre
            className="bg-black/30 p-4 rounded-lg border border-white/10 text-slate-400 text-sm overflow-y-auto max-h-60 font-mono focus:outline-none focus-visible:ring-2 focus-visible:ring-cyan-400"
            tabIndex={0}
            role="region"
            aria-label="Execution logs"
          >
            {result.logs.join('\n')}
          </pre>
        </div>
      )}
    </form>
  );
};

export default ColGenSolver;
