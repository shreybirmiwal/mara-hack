import React, { useState, useEffect } from 'react';
import { LineChart, Line, Area, AreaChart, ResponsiveContainer, XAxis, YAxis, Tooltip, ReferenceLine } from 'recharts';

const PriceAnalytics = () => {
  const [priceHistory, setPriceHistory] = useState([]);
  const [sentiment, setSentiment] = useState('neutral');
  const [sentimentScore, setSentimentScore] = useState(0);
  const [hashTrend, setHashTrend] = useState(0);
  const [tokenTrend, setTokenTrend] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Load and parse CSV data
    const loadPriceHistory = async () => {
      try {
        const response = await fetch('/pricing_history.csv');
        const text = await response.text();
        
        const lines = text.split('\n');
        const headers = lines[0].split(',');
        
        const data = lines.slice(1)
          .filter(line => line.trim())
          .map(line => {
            const values = line.split(',');
            return {
              timestamp: values[0],
              time: new Date(values[0]).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
              energy: parseFloat(values[1]),
              hash: parseFloat(values[2]),
              token: parseFloat(values[3])
            };
          })
          .reverse() // Reverse to show oldest to newest
          .slice(-50); // Keep last 50 data points for performance
        
        setPriceHistory(data);
        calculateTrends(data);
        calculateSentiment(data);
        setLoading(false);
      } catch (error) {
        console.error('Error loading price history:', error);
        setLoading(false);
      }
    };

    loadPriceHistory();
    const interval = setInterval(loadPriceHistory, 30000); // Refresh every 30 seconds
    
    return () => clearInterval(interval);
  }, []);

  const calculateTrends = (data) => {
    if (data.length < 2) return;
    
    const recent = data.slice(-10);
    const older = data.slice(-20, -10);
    
    const recentHashAvg = recent.reduce((sum, d) => sum + d.hash, 0) / recent.length;
    const olderHashAvg = older.reduce((sum, d) => sum + d.hash, 0) / older.length;
    const hashChange = ((recentHashAvg - olderHashAvg) / olderHashAvg) * 100;
    
    const recentTokenAvg = recent.reduce((sum, d) => sum + d.token, 0) / recent.length;
    const olderTokenAvg = older.reduce((sum, d) => sum + d.token, 0) / older.length;
    const tokenChange = ((recentTokenAvg - olderTokenAvg) / olderTokenAvg) * 100;
    
    setHashTrend(hashChange);
    setTokenTrend(tokenChange);
  };

  const calculateSentiment = (data) => {
    if (data.length < 5) return;
    
    const recent = data.slice(-5);
    const volatility = calculateVolatility(recent);
    const momentum = calculateMomentum(data);
    const priceStrength = calculatePriceStrength(recent);
    
    // Composite sentiment score (-100 to 100)
    const score = (momentum * 0.4 + priceStrength * 0.4 - volatility * 0.2);
    setSentimentScore(score);
    
    if (score > 30) {
      setSentiment('bullish');
    } else if (score > 10) {
      setSentiment('positive');
    } else if (score < -30) {
      setSentiment('bearish');
    } else if (score < -10) {
      setSentiment('negative');
    } else {
      setSentiment('neutral');
    }
  };

  const calculateVolatility = (data) => {
    const prices = data.map(d => (d.hash + d.token) / 2);
    const mean = prices.reduce((sum, p) => sum + p, 0) / prices.length;
    const variance = prices.reduce((sum, p) => sum + Math.pow(p - mean, 2), 0) / prices.length;
    return Math.sqrt(variance) / mean * 100;
  };

  const calculateMomentum = (data) => {
    if (data.length < 10) return 0;
    const recent = data.slice(-5);
    const older = data.slice(-10, -5);
    
    const recentAvg = recent.reduce((sum, d) => sum + (d.hash + d.token) / 2, 0) / recent.length;
    const olderAvg = older.reduce((sum, d) => sum + (d.hash + d.token) / 2, 0) / older.length;
    
    return ((recentAvg - olderAvg) / olderAvg) * 100;
  };

  const calculatePriceStrength = (data) => {
    const lastPrice = (data[data.length - 1].hash + data[data.length - 1].token) / 2;
    const maxPrice = Math.max(...data.map(d => (d.hash + d.token) / 2));
    const minPrice = Math.min(...data.map(d => (d.hash + d.token) / 2));
    
    return ((lastPrice - minPrice) / (maxPrice - minPrice) - 0.5) * 200;
  };

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="chart-tooltip">
          <p className="tooltip-label">{label}</p>
          {payload.map((entry, index) => (
            <p key={index} className="tooltip-value" style={{ color: entry.color }}>
              {entry.name}: ${entry.value.toFixed(4)}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  const getSentimentColor = () => {
    switch (sentiment) {
      case 'bullish': return '#22c55e';
      case 'positive': return '#86efac';
      case 'bearish': return '#ef4444';
      case 'negative': return '#fca5a5';
      default: return '#9ca3af';
    }
  };

  const getSentimentIcon = () => {
    switch (sentiment) {
      case 'bullish': return '↑↑';
      case 'positive': return '↑';
      case 'bearish': return '↓↓';
      case 'negative': return '↓';
      default: return '→';
    }
  };

  if (loading) {
    return (
      <div className="price-analytics loading">
        <div className="loading-spinner">Loading price data...</div>
      </div>
    );
  }

  return (
    <div className="price-analytics">
      {/* Sentiment Analysis Card */}
      <div className="sentiment-card">
        <div className="sentiment-header">
          <h4 className="sentiment-title">Market Sentiment</h4>
          <div className="sentiment-indicator" style={{ color: getSentimentColor() }}>
            <span className="sentiment-icon">{getSentimentIcon()}</span>
            <span className="sentiment-label">{sentiment.toUpperCase()}</span>
          </div>
        </div>
        <div className="sentiment-score">
          <div className="score-bar">
            <div className="score-fill" style={{ 
              width: `${Math.abs(sentimentScore) + 50}%`,
              background: getSentimentColor(),
              marginLeft: sentimentScore < 0 ? `${50 + sentimentScore}%` : '50%'
            }}></div>
            <div className="score-marker"></div>
          </div>
          <div className="score-labels">
            <span>Bearish</span>
            <span>Neutral</span>
            <span>Bullish</span>
          </div>
        </div>
        <div className="sentiment-metrics">
          <div className="metric">
            <span className="metric-label">Score</span>
            <span className="metric-value">{sentimentScore.toFixed(1)}</span>
          </div>
          <div className="metric">
            <span className="metric-label">Volatility</span>
            <span className="metric-value">{calculateVolatility(priceHistory.slice(-5)).toFixed(1)}%</span>
          </div>
          <div className="metric">
            <span className="metric-label">Momentum</span>
            <span className="metric-value">{calculateMomentum(priceHistory).toFixed(1)}%</span>
          </div>
        </div>
      </div>

      {/* Hash Price Chart */}
      <div className="price-chart-container">
        <div className="chart-header">
          <div className="chart-title-group">
            <h4 className="chart-title">Hash Price</h4>
            <span className={`trend-indicator ${hashTrend > 0 ? 'positive' : 'negative'}`}>
              {hashTrend > 0 ? '↑' : '↓'} {Math.abs(hashTrend).toFixed(2)}%
            </span>
          </div>
          <div className="current-price">
            ${priceHistory[priceHistory.length - 1]?.hash.toFixed(4) || '0.0000'}
          </div>
        </div>
        <ResponsiveContainer width="100%" height={150}>
          <AreaChart data={priceHistory} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="hashGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#22c55e" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#22c55e" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <XAxis 
              dataKey="time" 
              axisLine={false} 
              tickLine={false} 
              tick={{ fontSize: 10, fill: '#6b7280' }}
              interval="preserveStartEnd"
            />
            <YAxis 
              axisLine={false} 
              tickLine={false} 
              tick={{ fontSize: 10, fill: '#6b7280' }}
              domain={['dataMin - 0.1', 'dataMax + 0.1']}
            />
            <Tooltip content={<CustomTooltip />} />
            <Area 
              type="monotone" 
              dataKey="hash" 
              stroke="#22c55e" 
              strokeWidth={2}
              fill="url(#hashGradient)"
              name="Hash Price"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Token Price Chart */}
      <div className="price-chart-container">
        <div className="chart-header">
          <div className="chart-title-group">
            <h4 className="chart-title">Token Price</h4>
            <span className={`trend-indicator ${tokenTrend > 0 ? 'positive' : 'negative'}`}>
              {tokenTrend > 0 ? '↑' : '↓'} {Math.abs(tokenTrend).toFixed(2)}%
            </span>
          </div>
          <div className="current-price">
            ${priceHistory[priceHistory.length - 1]?.token.toFixed(4) || '0.0000'}
          </div>
        </div>
        <ResponsiveContainer width="100%" height={150}>
          <AreaChart data={priceHistory} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="tokenGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#f59e0b" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <XAxis 
              dataKey="time" 
              axisLine={false} 
              tickLine={false} 
              tick={{ fontSize: 10, fill: '#6b7280' }}
              interval="preserveStartEnd"
            />
            <YAxis 
              axisLine={false} 
              tickLine={false} 
              tick={{ fontSize: 10, fill: '#6b7280' }}
              domain={['dataMin - 0.1', 'dataMax + 0.1']}
            />
            <Tooltip content={<CustomTooltip />} />
            <Area 
              type="monotone" 
              dataKey="token" 
              stroke="#f59e0b" 
              strokeWidth={2}
              fill="url(#tokenGradient)"
              name="Token Price"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default PriceAnalytics; 