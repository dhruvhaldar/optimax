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
    <div className="container">
      <div className="header">
        <h1>Optimax: SF2812 Optimization Toolkit</h1>
        <p>Applied Linear Optimization - Solver & Visualizer</p>
      </div>

      <div className="nav">
        <button className={`nav-button ${activeTab === 'lp' ? 'active' : ''}`} onClick={() => setActiveTab('lp')}>LP (Simplex)</button>
        <button className={`nav-button ${activeTab === 'ip' ? 'active' : ''}`} onClick={() => setActiveTab('ip')}>IP (B&B)</button>
        <button className={`nav-button ${activeTab === 'colgen' ? 'active' : ''}`} onClick={() => setActiveTab('colgen')}>Column Generation</button>
        <button className={`nav-button ${activeTab === 'lagrangian' ? 'active' : ''}`} onClick={() => setActiveTab('lagrangian')}>Lagrangian Relaxation</button>
        <button className={`nav-button ${activeTab === 'stochastic' ? 'active' : ''}`} onClick={() => setActiveTab('stochastic')}>Stochastic Prog</button>
      </div>

      <div className="content">
        {renderSolver()}
      </div>
    </div>
  );
}

export default App;
