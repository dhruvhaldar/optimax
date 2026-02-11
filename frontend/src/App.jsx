import React, { useState } from 'react';
import './App.css';
import LPSolver from './components/LPSolver';
import IPSolver from './components/IPSolver';
import ColGenSolver from './components/ColGenSolver';
import LagrangianSolver from './components/LagrangianSolver';
import StochasticSolver from './components/StochasticSolver';

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
    <div className="container mx-auto px-4 py-8">
      <div className="glass-panel p-8 mb-8 text-center bg-gradient-to-r from-white/5 to-white/10">
        <h1 className="text-4xl font-bold mb-2 bg-clip-text text-transparent bg-gradient-to-r from-cyan-300 to-purple-300">
          Optimax: SF2812 Optimization Toolkit
        </h1>
        <p className="text-slate-300 text-lg">Applied Linear Optimization - Solver & Visualizer</p>
      </div>

      <div className="flex flex-wrap justify-center gap-4 mb-8">
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
          >
            {tab.label}
          </button>
        ))}
      </div>

      <div className="glass-panel p-6 min-h-[400px]">
        {renderSolver()}
      </div>
    </div>
  );
}

export default App;
