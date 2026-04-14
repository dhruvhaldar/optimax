import React, { useState } from 'react';
import axios from 'axios';
import { useOsShortcut } from '../hooks/useOsShortcut';
import { useResultFocus } from '../hooks/useResultFocus';

const IPSolver = () => {
  const { shortcutSymbol, shortcutText } = useOsShortcut();
  const [c, setC] = useState("[5, 8]");
  const [A, setA] = useState("[[1, 1], [5, 9]]");
  const [b, setB] = useState("[6, 45]");
  const [maximize, setMaximize] = useState(true);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [copied, setCopied] = useState(false);

  const resultRef = useResultFocus(loading, result);

  const handleCopySolution = () => {
    if (!result?.x) return;
    navigator.clipboard.writeText(JSON.stringify(result.x)).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  const solveIP = async () => {
    if (loading) return;
    setLoading(true);
    setError(null);
    let payload;
    try {
      payload = {
        c: JSON.parse(c),
        A_ub: JSON.parse(A),
        b_ub: JSON.parse(b),
        maximize: maximize
      };
    } catch (err) {
      setError("Invalid input format. Please ensure your vectors and matrices are formatted as valid JSON (e.g., [1, 2] or [[1, 2], [3, 4]]).");
      setLoading(false);
      return;
    }

    try {
      const response = await axios.post('/api/ip', payload);
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
    <form aria-labelledby="solver-title" className="glass-panel p-6" onKeyDown={handleKeyDown} onSubmit={e => { e.preventDefault(); if (!loading) solveIP(); }}>
      <h2 id="solver-title" className="text-2xl font-bold mb-6 text-cyan-100">Integer Programming (Branch and Bound)</h2>
      <div className="mb-4">
        <label htmlFor="ip-c" className="block text-sm font-medium text-slate-300 mb-2">Objective Coefficients (c) <span className="text-red-400" aria-hidden="true">*</span>:</label>
        <input
          id="ip-c"
          type="text"
          value={c}
          onChange={e => setC(e.target.value)}
          placeholder="[c1, c2]"
          spellCheck={false}
          autoComplete="off"
          autoCorrect="off"
          autoCapitalize="none"
          required className="glass-input w-full"
        />
      </div>
      <div className="mb-4">
        <label htmlFor="ip-A" className="block text-sm font-medium text-slate-300 mb-2">Constraint Matrix (A_ub) <span className="text-red-400" aria-hidden="true">*</span>:</label>
        <textarea
          id="ip-A"
          rows="3"
          value={A}
          onChange={e => setA(e.target.value)}
          placeholder="[[a11, a12], [a21, a22]]"
          spellCheck={false}
          autoComplete="off"
          autoCorrect="off"
          autoCapitalize="none"
          required className="glass-input w-full font-mono"
        />
      </div>
      <div className="mb-4">
        <label htmlFor="ip-b" className="block text-sm font-medium text-slate-300 mb-2">Constraint RHS (b_ub) <span className="text-red-400" aria-hidden="true">*</span>:</label>
        <input
          id="ip-b"
          type="text"
          value={b}
          onChange={e => setB(e.target.value)}
          placeholder="[b1, b2]"
          spellCheck={false}
          autoComplete="off"
          autoCorrect="off"
          autoCapitalize="none"
          required className="glass-input w-full"
        />
      </div>
      <fieldset className="mb-6">
        <legend className="block text-sm font-medium text-slate-300 mb-2">Objective Direction:</legend>
        <div className="flex items-center space-x-6">
          <label htmlFor="ip-maximize" className="flex items-center space-x-3 cursor-pointer">
            <input
              id="ip-maximize"
              type="radio"
              name="ip-objective-direction"
              checked={maximize === true}
              onChange={() => setMaximize(true)}
              className="form-radio h-5 w-5 text-cyan-500 rounded-full border-gray-300 focus:ring-cyan-500 bg-white/10"
            />
            <span className="text-slate-300">Maximize</span>
          </label>
          <label htmlFor="ip-minimize" className="flex items-center space-x-3 cursor-pointer">
            <input
              id="ip-minimize"
              type="radio"
              name="ip-objective-direction"
              checked={maximize === false}
              onChange={() => setMaximize(false)}
              className="form-radio h-5 w-5 text-cyan-500 rounded-full border-gray-300 focus:ring-cyan-500 bg-white/10"
            />
            <span className="text-slate-300">Minimize</span>
          </label>
        </div>
      </fieldset>
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
            Solve IP <kbd aria-hidden="true" className="text-xs opacity-80 ml-2 font-mono hidden sm:inline px-1.5 py-0.5 bg-white/10 border border-white/20 rounded-md shadow-sm">{shortcutSymbol}</kbd>
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
              <dd className={`text-lg font-semibold ${result.success ? 'text-green-400' : 'text-red-400'}`}>
                {result.success ? "Optimal" : "Failed"}
              </dd>
            </div>
            <div className="bg-white/5 p-4 rounded-lg">
              <dt className="text-slate-400 block text-sm">Objective Value</dt>
              <dd className="text-lg font-semibold text-white">{result.fun !== null && result.fun !== undefined ? result.fun.toFixed(4) : "N/A"}</dd>
            </div>
            <div className="col-span-1 md:col-span-2 bg-white/5 p-4 rounded-lg">
              <dt className="flex justify-between items-center mb-1">
                <span className="text-slate-400 block text-sm">Solution (x)</span>
                <button
                  type="button"
                  onClick={handleCopySolution}
                  className={`text-xs px-2 py-1 rounded transition-colors focus:outline-none focus-visible:ring-2 ${copied ? 'bg-green-500/20 hover:bg-green-500/30 text-green-300 focus-visible:ring-green-400' : 'bg-white/10 hover:bg-white/20 text-cyan-300 focus-visible:ring-cyan-400'}`}
                  aria-label={copied ? "Copied solution to clipboard" : "Copy solution to clipboard"}
                >
                  {copied ? "Copied!" : "Copy"}
                </button>
                <span aria-live="polite" className="sr-only">{copied ? "Copied to clipboard" : ""}</span>
              </dt>
              <dd>
                <code className="text-cyan-300 font-mono overflow-x-auto block focus:outline-none focus-visible:ring-2 focus-visible:ring-cyan-400" tabIndex={0} role="region" aria-label="Solution code">{JSON.stringify(result.x)}</code>
              </dd>
            </div>
          </dl>

          {result.tree_plot && (
            <div>
              <h4 className="text-lg font-semibold mb-3 text-slate-200">Branch and Bound Tree</h4>
              <img src={`data:image/png;base64,${result.tree_plot}`} alt="Branch and Bound Tree Visualization" tabIndex={0} className="w-full rounded-lg border border-white/20 shadow-lg focus:outline-none focus-visible:ring-2 focus-visible:ring-cyan-400" />
            </div>
          )}
        </div>
      )}
    </form>
  );
};

export default IPSolver;
