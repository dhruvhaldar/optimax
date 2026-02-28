import React, { useState, Suspense, lazy } from 'react';
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
    <svg className="animate-spin h-10 w-10 text-cyan-400 mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
    </svg>
    <p className="text-slate-300 font-medium">Loading Solver...</p>
  </div>
);

function App() {
  const [activeTab, setActiveTab] = useState('lp');

  const renderSolver = () => {
    switch (activeTab) {
      case 'lp': return <LPSolver />;
      case 'ip': return <IPSolver />;
      case 'colgen': return <ColGenSolver />;
      case 'lagrangian': return <LagrangianSolver />;
      case 'stochastic': return <StochasticSolver />;
      default: return <LPSolver />;
    }
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

      <nav aria-label="Solver selection" className="flex flex-wrap justify-center gap-4 mb-8">
        {[
          { id: 'lp', label: 'LP (Simplex)' },
          { id: 'ip', label: 'IP (B&B)' },
          { id: 'colgen', label: 'Column Generation' },
          { id: 'lagrangian', label: 'Lagrangian Relaxation' },
          { id: 'stochastic', label: 'Stochastic Prog' },
        ].map(tab => (
          <button
            key={tab.id}
            className={`glass-btn ${activeTab === tab.id ? 'bg-cyan-500/40 border-cyan-400 shadow-cyan-500/30' : ''}`}
            onClick={() => setActiveTab(tab.id)}
            aria-current={activeTab === tab.id ? 'true' : undefined}
          >
            {tab.label}
          </button>
        ))}
      </nav>

      <main id="main-content" className="glass-panel p-6 min-h-[400px] focus:outline-none" tabIndex="-1">
        <Suspense fallback={<LoadingSpinner />}>
          {renderSolver()}
        </Suspense>
      </main>
    </div>
  );
}

export default App;
