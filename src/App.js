import React, { useState, useEffect } from 'react';
import './App.css';
import MapComponent from './components/MapComponent';
import Sidebar from './components/Sidebar';

function App() {
  const [siteData, setSiteData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Load site data from JSON file
    const loadSiteData = async () => {
      try {
        const response = await fetch('/site_data.json');
        if (!response.ok) {
          throw new Error('Failed to load site data');
        }
        const data = await response.json();
        setSiteData(data);
        setLoading(false);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    };

    loadSiteData();
  }, []);

  const formatCurrency = (num) => {
    return `$${num.toLocaleString()}`;
  };

  const formatDateTime = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  if (loading) {
    return (
      <div className="App">
        <div className="App-header">
          <div className="header-left">
            <h1 className="App-title">Loading MARA Data...</h1>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="App">
        <div className="App-header">
          <div className="header-left">
            <h1 className="App-title">Error Loading Data</h1>
            <p className="App-subtitle">{error}</p>
          </div>
        </div>
        <div style={{ padding: '40px', textAlign: 'center' }}>
          <p style={{ fontSize: '1rem', color: '#9ca3af' }}>
            Please run: <code style={{ background: 'rgba(255,255,255,0.1)', padding: '4px 8px', borderRadius: '4px' }}>python export_map_data.py</code> to generate the site data.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="App">
      <div className="App-header">
        <div className="header-left">
          <h1 className="App-title">MARA Geographic Optimizer</h1>
          <p className="App-subtitle">
            Real-time mining optimization across {siteData.total_sites} locations
          </p>
        </div>
        <div className="header-right">
          <div className="status-indicator">
            <div className="status-dot"></div>
            <span>System Active</span>
          </div>
        </div>
      </div>

      <div className="main-content">
        <div className="map-container">
          <MapComponent siteData={siteData} />
          
          {/* Map Controls */}
          <div className="map-controls">
            <div className="price-grid">
              <div className="price-item">
                <div className="price-label">Energy</div>
                <div className="price-value">${siteData.current_prices.energy.toFixed(4)}</div>
              </div>
              <div className="price-item">
                <div className="price-label">Hash</div>
                <div className="price-value">${siteData.current_prices.hash.toFixed(4)}</div>
              </div>
              <div className="price-item">
                <div className="price-label">Token</div>
                <div className="price-value">${siteData.current_prices.token.toFixed(4)}</div>
              </div>
            </div>
            
            <div className="total-profit">
              <div className="profit-label">Total Profit</div>
              <div className="profit-value">{formatCurrency(siteData.total_profit)}</div>
            </div>
            
            <div className="instructions">
              Hover markers for quick info • Click markers for detailed view
              <br />
              Last updated: {formatDateTime(siteData.timestamp)}
            </div>
          </div>
        </div>
        
        <Sidebar siteData={siteData} />
      </div>
    </div>
  );
}

export default App; 