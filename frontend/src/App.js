import React, { useState, useEffect } from 'react';
import axios from 'axios';

function App() {
  const [sites, setSites] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({});
  const [prices, setPrices] = useState([]);
  const [profitability, setProfitability] = useState({});
  const [events, setEvents] = useState({});
  const [error, setError] = useState(null);
  const [optimizing, setOptimizing] = useState(false);
  const [eventDescription, setEventDescription] = useState('');
  const [siteProfitability, setSiteProfitability] = useState({});

  const API_BASE = 'http://127.0.0.1:5001/api';

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [sitesRes, statsRes, pricesRes, profitRes, eventsRes] = await Promise.all([
        axios.get(`${API_BASE}/sites`),
        axios.get(`${API_BASE}/stats`),
        axios.get(`${API_BASE}/prices`),
        axios.get(`${API_BASE}/profitability`),
        axios.get(`${API_BASE}/events`)
      ]);

      setSites(sitesRes.data);
      setStats(statsRes.data);
      setPrices(pricesRes.data);
      setProfitability(profitRes.data);
      setEvents(eventsRes.data);
      setError(null);
    } catch (err) {
      console.error('Error fetching data:', err);
      setError('Failed to fetch data. Make sure the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  const triggerOptimization = async () => {
    try {
      setOptimizing(true);
      await axios.post(`${API_BASE}/optimize`);
      // Refresh data after optimization
      setTimeout(() => {
        fetchData();
        setOptimizing(false);
      }, 2000);
    } catch (err) {
      console.error('Error triggering optimization:', err);
      setOptimizing(false);
    }
  };

  const simulateEvent = async () => {
    if (!eventDescription.trim()) return;

    try {
      const response = await axios.post(`${API_BASE}/simulate-event`, {
        description: eventDescription
      });

      console.log('Event simulation result:', response.data);
      setEventDescription('');

      // Refresh data to show event effects
      setTimeout(() => {
        fetchData();
      }, 1000);
    } catch (err) {
      console.error('Error simulating event:', err);
    }
  };

  const clearEvent = async (eventId) => {
    try {
      await axios.delete(`${API_BASE}/events/${eventId}`);
      fetchData(); // Refresh to show cleared effects
    } catch (err) {
      console.error('Error clearing event:', err);
    }
  };

  const formatNumber = (num) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num?.toString() || '0';
  };

  const formatCurrency = (num) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(num || 0);
  };

  const getPowerLevel = (power) => {
    if (power > 1500000) return { level: 'High', color: 'bg-red-500' };
    if (power > 800000) return { level: 'Medium', color: 'bg-orange-500' };
    return { level: 'Low', color: 'bg-green-500' };
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-lg text-gray-600">Loading MARA Sites...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center bg-white p-8 rounded-lg shadow-lg">
          <div className="text-red-600 text-xl mb-4">⚠️ Error</div>
          <p className="text-gray-700 mb-4">{error}</p>
          <button
            onClick={fetchData}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">MARA Site Dashboard</h1>
              <p className="text-gray-600">San Francisco Mining & Compute Sites</p>
            </div>
            <button
              onClick={fetchData}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Refresh Data
            </button>
          </div>
        </div>
      </header>

      {/* Stats Section */}
      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="text-2xl font-bold text-blue-600">{stats.total_sites || 0}</div>
            <div className="text-gray-600">Total Sites</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="text-2xl font-bold text-green-600">{stats.active_sites || 0}</div>
            <div className="text-gray-600">Active Sites</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="text-2xl font-bold text-purple-600">{formatNumber(stats.total_power)}</div>
            <div className="text-gray-600">Total Power (W)</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="text-2xl font-bold text-emerald-600">{formatCurrency(stats.total_revenue)}</div>
            <div className="text-gray-600">Total Revenue</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="text-2xl font-bold text-orange-600">
              {stats.api_connected ? 'Connected' : 'Disconnected'}
            </div>
            <div className="text-gray-600">MARA API Status</div>
          </div>
        </div>

        {/* Event Simulation */}
        <div className="bg-white p-6 rounded-lg shadow mb-8">
          <h2 className="text-xl font-semibold mb-4">🌪️ Event Simulation</h2>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Describe an event:
                </label>
                <input
                  type="text"
                  value={eventDescription}
                  onChange={(e) => setEventDescription(e.target.value)}
                  placeholder="e.g., 'flood in Mission District' or 'heatwave in downtown'"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  onKeyPress={(e) => e.key === 'Enter' && simulateEvent()}
                />
                <div className="text-xs text-gray-500 mt-1">
                  Try: flood, heatwave, power outage, earthquake + location (downtown, mission, soma, sunset)
                </div>
              </div>
              <button
                onClick={simulateEvent}
                disabled={!eventDescription.trim()}
                className={`px-4 py-2 rounded text-sm font-medium ${eventDescription.trim()
                  ? 'bg-red-600 text-white hover:bg-red-700'
                  : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  }`}
              >
                🚨 Simulate Event
              </button>
            </div>

            <div>
              <h3 className="font-medium mb-2">Active Events ({Object.keys(events).length})</h3>
              {Object.keys(events).length > 0 ? (
                <div className="space-y-2">
                  {Object.entries(events).map(([eventId, event]) => (
                    <div key={eventId} className="flex items-center justify-between p-2 bg-red-50 rounded border-l-4 border-red-500">
                      <div>
                        <div className="font-medium text-red-800 capitalize">{event.type}</div>
                        <div className="text-xs text-red-600">
                          {event.lat?.toFixed(4)}, {event.lng?.toFixed(4)}
                        </div>
                      </div>
                      <button
                        onClick={() => clearEvent(eventId)}
                        className="px-2 py-1 text-xs bg-red-600 text-white rounded hover:bg-red-700"
                      >
                        Clear
                      </button>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-gray-500 text-sm">No active events</div>
              )}
            </div>
          </div>
        </div>

        {/* Optimization Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Market Prices */}
          {prices.length > 0 && (
            <div className="bg-white p-6 rounded-lg shadow">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold">Market Prices</h2>
                <div className="text-xs text-gray-500">Updates every 5 min</div>
              </div>
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <div className="text-lg font-bold text-blue-600">${prices[0]?.energy_price?.toFixed(3)}</div>
                  <div className="text-sm text-gray-600">Energy Price</div>
                </div>
                <div>
                  <div className="text-lg font-bold text-green-600">${prices[0]?.hash_price?.toFixed(2)}</div>
                  <div className="text-sm text-gray-600">Hash Price</div>
                </div>
                <div>
                  <div className="text-lg font-bold text-purple-600">${prices[0]?.token_price?.toFixed(2)}</div>
                  <div className="text-sm text-gray-600">Token Price</div>
                </div>
              </div>
            </div>
          )}

          {/* Profitability & Optimization */}
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold">Auto-Optimization</h2>
              <button
                onClick={triggerOptimization}
                disabled={optimizing}
                className={`px-4 py-2 rounded text-sm font-medium ${optimizing
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-blue-600 text-white hover:bg-blue-700'
                  }`}
              >
                {optimizing ? '🔄 Optimizing...' : '🚀 Optimize Now'}
              </button>
            </div>

            {Object.keys(profitability).length > 0 && (
              <div className="space-y-2">
                <div className="text-sm text-gray-600 mb-3">Machine Profitability ($/hour):</div>
                {Object.entries(profitability)
                  .sort(([, a], [, b]) => b - a)
                  .map(([machine, profit]) => (
                    <div key={machine} className="flex justify-between items-center">
                      <span className="text-sm capitalize">
                        {machine.replace('_', ' ')}
                      </span>
                      <span className={`text-sm font-semibold ${profit > 0 ? 'text-green-600' : 'text-red-600'
                        }`}>
                        ${profit.toFixed(2)}
                      </span>
                    </div>
                  ))
                }
                <div className="text-xs text-gray-500 mt-3">
                  🤖 Sites auto-optimize every 5 minutes based on profitability
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Sites List */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b">
            <h2 className="text-xl font-semibold">Sites ({sites.length})</h2>
          </div>
          <div className="divide-y">
            {sites.map((site) => {
              const powerInfo = getPowerLevel(site.power);
              return (
                <div key={site.id} className="p-6 hover:bg-gray-50">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center">
                      <div className={`w-4 h-4 rounded-full ${powerInfo.color} mr-3`}></div>
                      <h3 className="text-lg font-semibold">{site.name}</h3>
                      <span className={`ml-3 px-2 py-1 text-xs rounded ${site.api_key ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                        }`}>
                        {site.api_key ? 'Active' : 'Inactive'}
                      </span>
                    </div>
                    <div className="text-right">
                      <div className="text-lg font-semibold">{formatNumber(site.power)}W</div>
                      <div className="text-sm text-gray-500">{powerInfo.level} Power</div>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <div className="text-gray-600">Location</div>
                      <div className="font-medium">{site.lat.toFixed(4)}, {site.lng.toFixed(4)}</div>
                    </div>
                    {site.api_key && (
                      <div>
                        <div className="text-gray-600">API Key</div>
                        <div className="font-mono text-xs">{site.api_key}</div>
                      </div>
                    )}
                  </div>

                  {/* Location Modifiers */}
                  {site.location_modifiers && (
                    <div className="mt-3 p-3 bg-blue-50 rounded">
                      <h4 className="font-medium mb-2 text-blue-800">📍 Location Effects</h4>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
                        <div>
                          <div className="text-gray-600">Energy Cost</div>
                          <div className={`font-semibold ${site.location_modifiers.energy_cost_modifier > 1 ? 'text-red-600' : 'text-green-600'}`}>
                            {(site.location_modifiers.energy_cost_modifier * 100).toFixed(0)}%
                          </div>
                        </div>
                        <div>
                          <div className="text-gray-600">Cooling Efficiency</div>
                          <div className={`font-semibold ${site.location_modifiers.cooling_efficiency > 1 ? 'text-green-600' : 'text-red-600'}`}>
                            {(site.location_modifiers.cooling_efficiency * 100).toFixed(0)}%
                          </div>
                        </div>
                        <div>
                          <div className="text-gray-600">Hydro Efficiency</div>
                          <div className={`font-semibold ${site.location_modifiers.hydro_efficiency > 1 ? 'text-green-600' : 'text-red-600'}`}>
                            {(site.location_modifiers.hydro_efficiency * 100).toFixed(0)}%
                          </div>
                        </div>
                        <div>
                          <div className="text-gray-600">Network Latency</div>
                          <div className={`font-semibold ${site.location_modifiers.network_latency < 1 ? 'text-green-600' : 'text-red-600'}`}>
                            {(site.location_modifiers.network_latency * 100).toFixed(0)}%
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Machine Details */}
                  {site.machines && (
                    <div className="mt-4 p-4 bg-gray-50 rounded">
                      <h4 className="font-medium mb-2">Machine Allocation</h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                        {/* Mining Machines */}
                        <div>
                          <h5 className="font-medium text-blue-800 mb-2">⛏️ Bitcoin Mining</h5>
                          <div className="space-y-1">
                            {site.machines.air_miners > 0 && (
                              <div className="flex justify-between">
                                <span className="text-gray-600">Air Miners (1 TH/s)</span>
                                <span className="font-semibold">{site.machines.air_miners}</span>
                              </div>
                            )}
                            {site.machines.hydro_miners > 0 && (
                              <div className="flex justify-between">
                                <span className="text-gray-600">Hydro Miners (5 TH/s)</span>
                                <span className="font-semibold">{site.machines.hydro_miners}</span>
                              </div>
                            )}
                            {site.machines.immersion_miners > 0 && (
                              <div className="flex justify-between">
                                <span className="text-gray-600">Immersion Miners (10 TH/s)</span>
                                <span className="font-semibold">{site.machines.immersion_miners}</span>
                              </div>
                            )}
                          </div>
                        </div>

                        {/* Compute Machines */}
                        <div>
                          <h5 className="font-medium text-purple-800 mb-2">🖥️ AI Compute</h5>
                          <div className="space-y-1">
                            {site.machines.gpu_compute > 0 && (
                              <div className="flex justify-between">
                                <span className="text-gray-600">GPU Compute (1K tok/hr)</span>
                                <span className="font-semibold">{site.machines.gpu_compute}</span>
                              </div>
                            )}
                            {site.machines.asic_compute > 0 && (
                              <div className="flex justify-between">
                                <span className="text-gray-600">ASIC Compute (50K tok/hr)</span>
                                <span className="font-semibold">{site.machines.asic_compute}</span>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                      {site.machines.total_revenue && (
                        <div className="mt-3 pt-3 border-t">
                          <div className="text-green-600 font-semibold">
                            Total Revenue: {formatCurrency(site.machines.total_revenue)}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
