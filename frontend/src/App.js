import React, { useState, useEffect } from 'react';
import axios from 'axios';

function App() {
  const [sites, setSites] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({});
  const [prices, setPrices] = useState([]);
  const [error, setError] = useState(null);

  const API_BASE = 'http://127.0.0.1:5000/api';

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [sitesRes, statsRes, pricesRes] = await Promise.all([
        axios.get(`${API_BASE}/sites`),
        axios.get(`${API_BASE}/stats`),
        axios.get(`${API_BASE}/prices`)
      ]);

      setSites(sitesRes.data);
      setStats(statsRes.data);
      setPrices(pricesRes.data);
      setError(null);
    } catch (err) {
      console.error('Error fetching data:', err);
      setError('Failed to fetch data. Make sure the backend is running.');
    } finally {
      setLoading(false);
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
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
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
            <div className="text-2xl font-bold text-orange-600">
              {stats.api_connected ? 'Connected' : 'Disconnected'}
            </div>
            <div className="text-gray-600">MARA API Status</div>
          </div>
        </div>

        {/* Market Prices */}
        {prices.length > 0 && (
          <div className="bg-white p-6 rounded-lg shadow mb-8">
            <h2 className="text-xl font-semibold mb-4">Current Market Prices</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <div className="text-lg font-bold text-blue-600">${prices[0]?.energy_price?.toFixed(3)}</div>
                <div className="text-gray-600">Energy Price</div>
              </div>
              <div>
                <div className="text-lg font-bold text-green-600">${prices[0]?.hash_price?.toFixed(2)}</div>
                <div className="text-gray-600">Hash Price</div>
              </div>
              <div>
                <div className="text-lg font-bold text-purple-600">${prices[0]?.token_price?.toFixed(2)}</div>
                <div className="text-gray-600">Token Price</div>
              </div>
            </div>
          </div>
        )}

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

                  {/* Machine Details */}
                  {site.machines && (
                    <div className="mt-4 p-4 bg-gray-50 rounded">
                      <h4 className="font-medium mb-2">Machine Allocation</h4>
                      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-sm">
                        {site.machines.air_miners > 0 && (
                          <div>
                            <div className="text-gray-600">Air Miners</div>
                            <div className="font-semibold">{site.machines.air_miners}</div>
                          </div>
                        )}
                        {site.machines.hydro_miners > 0 && (
                          <div>
                            <div className="text-gray-600">Hydro Miners</div>
                            <div className="font-semibold">{site.machines.hydro_miners}</div>
                          </div>
                        )}
                        {site.machines.immersion_miners > 0 && (
                          <div>
                            <div className="text-gray-600">Immersion Miners</div>
                            <div className="font-semibold">{site.machines.immersion_miners}</div>
                          </div>
                        )}
                        {site.machines.gpu_compute > 0 && (
                          <div>
                            <div className="text-gray-600">GPU Compute</div>
                            <div className="font-semibold">{site.machines.gpu_compute}</div>
                          </div>
                        )}
                        {site.machines.asic_compute > 0 && (
                          <div>
                            <div className="text-gray-600">ASIC Compute</div>
                            <div className="font-semibold">{site.machines.asic_compute}</div>
                          </div>
                        )}
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
