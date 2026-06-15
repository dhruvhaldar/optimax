import React, { useState, useEffect, Suspense, lazy } from 'react';
import './App.css';

// Lazy load solver components for performance optimization (Code Splitting)
const LPSolver = lazy(() => import('./components/LPSolver'));
const IPSolver = lazy(() => import('./components/IPSolver'));
const ColGenSolver = lazy(() => import('./components/ColGenSolver'));
const LagrangianSolver = lazy(() => import('./components/LagrangianSolver'));
const StochasticSolver = lazy(() => import('./components/StochasticSolver'));

// Loading component for Suspense fallback
const LoadingSpinner = () => (
  <div role="status" aria-live="polite" className="flex flex-col items-center justify-center py-20 h-full w-full">
    <svg aria-hidden="true" className="animate-spin h-10 w-10 text-cyan-400 mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
    </svg>
    <p className="text-slate-300 font-medium">Loading Solver...</p>
  </div>
);

const TABS = [
  { id: 'lp', label: 'LP (Simplex)' },
  { id: 'ip', label: 'IP (B&B)' },
  { id: 'colgen', label: 'Column Generation' },
  { id: 'lagrangian', label: 'Lagrangian Relaxation' },
  { id: 'stochastic', label: 'Stochastic Prog' },
];

const CAPABILITIES = [
  'Solve Linear Programming models via Simplex',
  'Run Integer Programming with Branch & Bound',
  'Experiment with Column Generation workflows',
  'Apply Lagrangian Relaxation techniques',
  'Compare decisions under stochastic scenarios',
];

function App() {
  const [activeTab, setActiveTab] = useState('lp');
  const [visitedTabs, setVisitedTabs] = useState(new Set(['lp']));

  useEffect(() => {
    const activeLabel = TABS.find(tab => tab.id === activeTab)?.label || 'Optimax';
    document.title = `${activeLabel} | Optimax`;
  }, [activeTab]);

  const changeTab = (id) => {
    setActiveTab(id);
    setVisitedTabs(prev => {
      if (prev.has(id)) return prev;
      const next = new Set(prev);
      next.add(id);
      return next;
    });
  };

  return (
    <div className="container mx-auto px-4 py-8 relative">
      <a
        href="#main-content"
        className="absolute -top-96 left-4 z-50 bg-cyan-600 text-white font-semibold py-3 px-6 rounded-lg shadow-xl transition-all focus:top-4 focus:outline-none focus-visible:ring-4 focus-visible:ring-cyan-400"
      >
        Skip to main content
      </a>

      <header className="glass-panel p-8 mb-8 text-center bg-gradient-to-r from-white/5 to-white/10">
        <h1 className="text-4xl font-bold mb-2 bg-clip-text text-transparent bg-gradient-to-r from-cyan-300 to-purple-300">
          Optimax: SF2812 Optimization Toolkit
        </h1>
        <p className="text-slate-300 text-lg">Applied Linear Optimization - Solver & Visualizer</p>
      </header>

      <section aria-label="Library capabilities" className="glass-panel p-6 mb-8">
        <h2 className="text-2xl font-semibold text-cyan-200 mb-4">What this frontend showcases</h2>
        <ul className="grid gap-3 md:grid-cols-2">
          {CAPABILITIES.map((capability) => (
            <li key={capability} className="rounded-lg bg-white/5 border border-white/10 p-3 text-slate-200">
              {capability}
            </li>
          ))}
        </ul>
      </section>

      <div role="tablist" aria-label="Solver selection" className="flex flex-wrap justify-center gap-4 mb-8">
        {TABS.map((tab, index) => (
          <button
            key={tab.id}
            role="tab"
            id={`tab-${tab.id}`}
            aria-controls={`panel-${tab.id}`}
            aria-selected={activeTab === tab.id}
            tabIndex={activeTab === tab.id ? 0 : -1}
            className={`glass-btn ${activeTab === tab.id ? 'bg-cyan-500/40 border-cyan-400 shadow-cyan-500/30' : ''}`}
            onClick={() => changeTab(tab.id)}
            onKeyDown={(e) => {
              let newIndex = index;
              if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
                newIndex = (index + 1) % TABS.length;
              } else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
                newIndex = (index - 1 + TABS.length) % TABS.length;
              } else if (e.key === 'Home') {
                newIndex = 0;
              } else if (e.key === 'End') {
                newIndex = TABS.length - 1;
              } else {
                return;
              }
              e.preventDefault();
              changeTab(TABS[newIndex].id);
              document.getElementById(`tab-${TABS[newIndex].id}`)?.focus();
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <main
        id="main-content"
        className="glass-panel p-6 min-h-[400px] focus:outline-none"
        tabIndex="-1"
      >
        <Suspense fallback={<LoadingSpinner />}>
          <div id="panel-lp" role="tabpanel" aria-labelledby="tab-lp" hidden={activeTab !== 'lp'}>
            {visitedTabs.has('lp') && <LPSolver />}
          </div>
          <div id="panel-ip" role="tabpanel" aria-labelledby="tab-ip" hidden={activeTab !== 'ip'}>
            {visitedTabs.has('ip') && <IPSolver />}
          </div>
          <div id="panel-colgen" role="tabpanel" aria-labelledby="tab-colgen" hidden={activeTab !== 'colgen'}>
            {visitedTabs.has('colgen') && <ColGenSolver />}
          </div>
          <div id="panel-lagrangian" role="tabpanel" aria-labelledby="tab-lagrangian" hidden={activeTab !== 'lagrangian'}>
            {visitedTabs.has('lagrangian') && <LagrangianSolver />}
          </div>
          <div id="panel-stochastic" role="tabpanel" aria-labelledby="tab-stochastic" hidden={activeTab !== 'stochastic'}>
            {visitedTabs.has('stochastic') && <StochasticSolver />}
          </div>
        </Suspense>
      </main>

      <footer className="mt-8 glass-panel p-4 text-center text-slate-300 text-sm">
        <div className="flex flex-wrap justify-center items-center gap-2">
          <a href="https://github.com/dhruvhaldar/optimax" target="_blank" rel="noreferrer" className="text-cyan-300 hover:text-cyan-200 underline inline-flex items-center gap-1 focus:outline-none focus-visible:ring-2 focus-visible:ring-cyan-400 rounded-sm">
            GitHub Repository
            <span className="sr-only">(opens in a new tab)</span>
            <svg aria-hidden="true" className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
          </a>
          <span aria-hidden="true">·</span>
          <a href="https://github.com/dhruvhaldar/optimax/blob/main/LICENSE" target="_blank" rel="noreferrer" className="text-cyan-300 hover:text-cyan-200 underline inline-flex items-center gap-1 focus:outline-none focus-visible:ring-2 focus-visible:ring-cyan-400 rounded-sm">
            MIT License
            <span className="sr-only">(opens in a new tab)</span>
            <svg aria-hidden="true" className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
          </a>
          <span aria-hidden="true">·</span>
          <span>Built by{' '}</span>
          <a href="https://dhruvhaldar.vercel.app/" target="_blank" rel="noreferrer" className="text-cyan-300 hover:text-cyan-200 underline inline-flex items-center gap-1 focus:outline-none focus-visible:ring-2 focus-visible:ring-cyan-400 rounded-sm">
            Dhruv Haldar
            <span className="sr-only">(opens in a new tab)</span>
            <svg aria-hidden="true" className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
          </a>
        </div>
      </footer>
    </div>
  );
}

export default App;
