import React, { useState } from 'react';
import { LineChart, Line, ResponsiveContainer, XAxis, YAxis } from 'recharts';
import DisasterSimulator from './DisasterSimulator';

const Sidebar = ({ siteData, onSiteDataUpdate }) => {
  const [activeTab, setActiveTab] = useState('dashboard');
  // Generate mock historical data for charts
  const generateChartData = (baseValue, volatility = 0.1) => {
    const data = [];
    const points = 24; // 24 hours of data
    
    for (let i = 0; i < points; i++) {
      const hour = 24 - points + i;
      const timeLabel = hour < 0 ? `${24 + hour}:00` : `${hour}:00`;
      const variance = (Math.random() - 0.5) * volatility;
      const value = baseValue * (1 + variance);
      
      data.push({
        time: timeLabel,
        value: value,
        timestamp: Date.now() - (points - i) * 3600000
      });
    }
    return data;
  };

  const hashRateData = generateChartData(siteData.current_prices.hash, 0.15);
  const tokenRateData = generateChartData(siteData.current_prices.token, 0.12);
  const energyPriceData = generateChartData(siteData.current_prices.energy, 0.08);

  const formatCurrency = (value) => `$${value.toFixed(4)}`;
  const formatLarge = (value) => {
    if (value >= 1000000) return `${(value / 1000000).toFixed(1)}M`;
    if (value >= 1000) return `${(value / 1000).toFixed(1)}K`;
    return value.toLocaleString();
  };



  return (
    <div className="sidebar">
      {/* Tab Navigation */}
      <div className="sidebar-tabs">
        <button 
          className={`sidebar-tab ${activeTab === 'dashboard' ? 'active' : ''}`}
          onClick={() => setActiveTab('dashboard')}
        >
          Dashboard
        </button>
        <button 
          className={`sidebar-tab ${activeTab === 'simulator' ? 'active' : ''}`}
          onClick={() => setActiveTab('simulator')}
        >
          Disaster Sim
        </button>
      </div>

      {activeTab === 'dashboard' && (
        <div className="sidebar-content">
          {/* Market Data Section */}
          <div className="sidebar-section">
            <h3 className="sidebar-title">Market Rates</h3>
        
        <div className="chart-container">
          <div className="chart-header">
            <span className="chart-title">Hash Rate</span>
            <span className="chart-value">{formatCurrency(siteData.current_prices.hash)}</span>
          </div>
          <ResponsiveContainer width="100%" height={100}>
            <LineChart data={hashRateData} margin={{ top: 10, right: 5, left: 5, bottom: 5 }}>
              <XAxis 
                dataKey="time" 
                axisLine={false} 
                tickLine={false} 
                tick={{ fontSize: 10, fill: '#6b7280' }}
                interval="preserveStartEnd"
              />
              <YAxis hide />
              <Line 
                type="monotone" 
                dataKey="value" 
                stroke="#22c55e" 
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 3, fill: '#22c55e' }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-container">
          <div className="chart-header">
            <span className="chart-title">Token Rate</span>
            <span className="chart-value">{formatCurrency(siteData.current_prices.token)}</span>
          </div>
          <ResponsiveContainer width="100%" height={100}>
            <LineChart data={tokenRateData} margin={{ top: 10, right: 5, left: 5, bottom: 5 }}>
              <XAxis 
                dataKey="time" 
                axisLine={false} 
                tickLine={false} 
                tick={{ fontSize: 10, fill: '#6b7280' }}
                interval="preserveStartEnd"
              />
              <YAxis hide />
              <Line 
                type="monotone" 
                dataKey="value" 
                stroke="#f59e0b" 
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 3, fill: '#f59e0b' }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-container">
          <div className="chart-header">
            <span className="chart-title">Energy Price</span>
            <span className="chart-value">{formatCurrency(siteData.current_prices.energy)}</span>
          </div>
          <ResponsiveContainer width="100%" height={100}>
            <LineChart data={energyPriceData} margin={{ top: 10, right: 5, left: 5, bottom: 5 }}>
              <XAxis 
                dataKey="time" 
                axisLine={false} 
                tickLine={false} 
                tick={{ fontSize: 10, fill: '#6b7280' }}
                interval="preserveStartEnd"
              />
              <YAxis hide />
              <Line 
                type="monotone" 
                dataKey="value" 
                stroke="#ef4444" 
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 3, fill: '#ef4444' }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Performance Metrics */}
      <div className="sidebar-section">
        <h3 className="sidebar-title">Performance Metrics</h3>
        
        <div className="metrics-grid">
          <div className="metric-item">
            <div className="metric-label">Total Sites</div>
            <div className="metric-value">{siteData.total_sites}</div>
          </div>
          
          <div className="metric-item">
            <div className="metric-label">Active Sites</div>
            <div className="metric-value">{siteData.sites.filter(s => s.optimization.net_profit > 0).length}</div>
          </div>
          
          <div className="metric-item">
            <div className="metric-label">Total Profit</div>
            <div className="metric-value">{formatLarge(siteData.total_profit)}</div>
          </div>
          
          <div className="metric-item">
            <div className="metric-label">Avg Efficiency</div>
            <div className="metric-value">
              {(siteData.sites.reduce((acc, site) => acc + site.optimization.efficiency, 0) / siteData.sites.length).toFixed(2)}
            </div>
          </div>
        </div>
      </div>

      {/* Top Locations */}
      <div className="sidebar-section">
        <h3 className="sidebar-title">Top Locations</h3>
        
        <div className="locations-list">
          {siteData.sites
            .filter(site => site.optimization.net_profit > 0)
            .slice(0, 5)
            .map((site, index) => (
              <div key={site.id} className="location-item">
                <div className="location-rank">#{index + 1}</div>
                <div className="location-info">
                  <div className="location-name">{site.name}</div>
                  <div className="location-profit">{formatLarge(site.optimization.net_profit)}</div>
                </div>
                <div className="location-status">
                  <div className={`status-dot ${site.optimization.net_profit > 1500000 ? 'high' : site.optimization.net_profit > 500000 ? 'medium' : 'low'}`}></div>
                </div>
              </div>
            ))}
        </div>
      </div>
        </div>
      )}

      {activeTab === 'simulator' && (
        <DisasterSimulator 
          siteData={siteData} 
          onSiteDataUpdate={onSiteDataUpdate}
        />
      )}
    </div>
  );
};

export default Sidebar; 