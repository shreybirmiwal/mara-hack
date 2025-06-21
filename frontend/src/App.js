import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import Globe from 'react-globe.gl';

const API_BASE_URL = 'http://localhost:5001/api';

function App() {
  const [backendStatus, setBackendStatus] = useState('Checking...');
  const [energyData, setEnergyData] = useState([]);
  const [energyStats, setEnergyStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedLocation, setSelectedLocation] = useState(null);
  const globeEl = useRef();

  useEffect(() => {
    checkBackendHealth();
    fetchEnergyData();
    fetchEnergyStats();

    // Auto-refresh every 5 minutes
    const interval = setInterval(() => {
      fetchEnergyData();
      fetchEnergyStats();
    }, 300000);

    return () => clearInterval(interval);
  }, []);

  const checkBackendHealth = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/health`);
      setBackendStatus(response.data.message);
    } catch (error) {
      setBackendStatus('Backend not responding');
    }
  };

  const fetchEnergyData = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/energy-data`);
      if (response.data.success) {
        setEnergyData(response.data.data);
        setError(null);
      } else {
        setError(response.data.message);
      }
    } catch (error) {
      console.error('Error fetching energy data:', error);
      setError('Failed to fetch energy data. Make sure the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  const fetchEnergyStats = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/energy-stats`);
      setEnergyStats(response.data);
    } catch (error) {
      console.error('Error fetching energy stats:', error);
    }
  };

  // Convert energy data to globe points
  const globeData = energyData.map(location => ({
    lat: location.lat,
    lng: location.lng,
    size: Math.max(0.1, location.price_mwh / 100), // Scale size based on price
    color: getPriceColor(location.price_mwh),
    label: `${location.location_name}<br/>$${location.price_mwh}/MWh<br/>${location.type}`,
    ...location
  }));

  function getPriceColor(price) {
    if (price > 75) return '#ff4444'; // High price - Red
    if (price > 50) return '#ff8844'; // Medium-high - Orange
    if (price > 25) return '#ffdd44'; // Medium - Yellow
    if (price > 10) return '#88ff44'; // Low-medium - Light Green
    return '#44ff44'; // Low price - Green
  }

  const handleLocationClick = (location) => {
    setSelectedLocation(location);
  };

  if (loading && energyData.length === 0) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center text-white">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-400 mx-auto"></div>
          <p className="mt-4 text-lg">Loading Texas Energy Data...</p>
        </div>
      </div>
    );
  }

  if (error && energyData.length === 0) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center bg-gray-800 p-8 rounded-lg shadow-lg text-white">
          <div className="text-red-400 text-xl mb-4">⚠️ Error</div>
          <p className="text-gray-300 mb-4">{error}</p>
          <button
            onClick={() => {
              fetchEnergyData();
              fetchEnergyStats();
            }}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <header className="bg-gray-800 shadow-lg">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-blue-400">MARA Energy Visualization</h1>
              <p className="text-gray-300 text-sm">Real-time Texas ERCOT Energy Pricing</p>
            </div>
            <div className="flex items-center space-x-4">
              <div className={`w-3 h-3 rounded-full ${backendStatus === 'Backend is running' ? 'bg-green-500' : 'bg-red-500'
                }`}></div>
              <span className="text-sm text-gray-300">{backendStatus}</span>
              <button
                onClick={() => {
                  fetchEnergyData();
                  fetchEnergyStats();
                }}
                className="px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
                disabled={loading}
              >
                {loading ? 'Refreshing...' : 'Refresh'}
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="flex h-screen">
        {/* Stats Sidebar */}
        <div className="w-80 bg-gray-800 p-4 overflow-y-auto">
          <div className="space-y-4">

            {/* Summary Stats */}
            <div className="bg-gray-700 p-4 rounded-lg">
              <h3 className="text-lg font-semibold mb-3 text-blue-400">Market Overview</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-300">Active Locations:</span>
                  <span className="font-medium">{energyData.length}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-300">Avg Price:</span>
                  <span className="font-medium">${energyStats.avg_price || 0}/MWh</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-300">Max Price:</span>
                  <span className="font-medium text-red-400">${energyStats.max_price || 0}/MWh</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-300">Min Price:</span>
                  <span className="font-medium text-green-400">${energyStats.min_price || 0}/MWh</span>
                </div>
              </div>
            </div>

            {/* Price Legend */}
            <div className="bg-gray-700 p-4 rounded-lg">
              <h3 className="text-lg font-semibold mb-3 text-blue-400">Price Legend</h3>
              <div className="space-y-2 text-sm">
                <div className="flex items-center">
                  <div className="w-4 h-4 bg-red-500 rounded-full mr-2"></div>
                  <span>$75+ /MWh - Very High</span>
                </div>
                <div className="flex items-center">
                  <div className="w-4 h-4 bg-orange-500 rounded-full mr-2"></div>
                  <span>$50-75 /MWh - High</span>
                </div>
                <div className="flex items-center">
                  <div className="w-4 h-4 bg-yellow-500 rounded-full mr-2"></div>
                  <span>$25-50 /MWh - Medium</span>
                </div>
                <div className="flex items-center">
                  <div className="w-4 h-4 bg-lime-500 rounded-full mr-2"></div>
                  <span>$10-25 /MWh - Low</span>
                </div>
                <div className="flex items-center">
                  <div className="w-4 h-4 bg-green-500 rounded-full mr-2"></div>
                  <span>$0-10 /MWh - Very Low</span>
                </div>
              </div>
            </div>

            {/* Location Details */}
            {selectedLocation && (
              <div className="bg-gray-700 p-4 rounded-lg">
                <h3 className="text-lg font-semibold mb-3 text-blue-400">Selected Location</h3>
                <div className="space-y-2 text-sm">
                  <div>
                    <span className="text-gray-300">Name:</span>
                    <p className="font-medium">{selectedLocation.location_name}</p>
                  </div>
                  <div>
                    <span className="text-gray-300">Type:</span>
                    <p className="font-medium">{selectedLocation.type}</p>
                  </div>
                  <div>
                    <span className="text-gray-300">Price:</span>
                    <p className="font-medium text-xl" style={{ color: getPriceColor(selectedLocation.price_mwh) }}>
                      ${selectedLocation.price_mwh}/MWh
                    </p>
                  </div>
                  <div>
                    <span className="text-gray-300">Last Updated:</span>
                    <p className="font-medium text-xs">{selectedLocation.timestamp}</p>
                  </div>
                  <div>
                    <span className="text-gray-300">Coordinates:</span>
                    <p className="font-medium text-xs">{selectedLocation.lat.toFixed(4)}, {selectedLocation.lng.toFixed(4)}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Top Locations by Price */}
            <div className="bg-gray-700 p-4 rounded-lg">
              <h3 className="text-lg font-semibold mb-3 text-blue-400">Highest Prices</h3>
              <div className="space-y-2">
                {energyData.slice(0, 5).map((location, index) => (
                  <div
                    key={location.location_code}
                    className="flex justify-between items-center p-2 bg-gray-600 rounded cursor-pointer hover:bg-gray-500"
                    onClick={() => handleLocationClick(location)}
                  >
                    <div>
                      <div className="font-medium text-sm">{location.location_name}</div>
                      <div className="text-xs text-gray-300">{location.type}</div>
                    </div>
                    <div className="text-right">
                      <div className="font-bold" style={{ color: getPriceColor(location.price_mwh) }}>
                        ${location.price_mwh}
                      </div>
                      <div className="text-xs text-gray-300">/MWh</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

          </div>
        </div>

        {/* 3D Globe */}
        <div className="flex-1 relative">
          <Globe
            ref={globeEl}
            globeImageUrl="//unpkg.com/three-globe/example/img/earth-night.jpg"
            bumpImageUrl="//unpkg.com/three-globe/example/img/earth-topology.png"
            backgroundImageUrl="//unpkg.com/three-globe/example/img/night-sky.png"

            pointsData={globeData}
            pointAltitude="size"
            pointColor="color"
            pointRadius={0.4}
            pointResolution={8}

            onPointClick={handleLocationClick}
            pointLabel="label"

            // Initial camera position focused on Texas
            pointOfView={{ lat: 31.5, lng: -99.5, altitude: 1.5 }}

            // Styling
            width={window.innerWidth - 320}
            height={window.innerHeight - 80}

            // Animation
            animateIn={true}
          />

          {/* Overlay Instructions */}
          <div className="absolute top-4 right-4 bg-gray-800 bg-opacity-90 p-4 rounded-lg max-w-sm">
            <h3 className="font-semibold text-blue-400 mb-2">How to Use</h3>
            <ul className="text-sm text-gray-300 space-y-1">
              <li>• <strong>Click</strong> on points to view details</li>
              <li>• <strong>Drag</strong> to rotate the globe</li>
              <li>• <strong>Scroll</strong> to zoom in/out</li>
              <li>• Point size = relative price</li>
              <li>• Point color = price category</li>
            </ul>
          </div>

          {loading && (
            <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
              <div className="bg-gray-800 bg-opacity-90 p-4 rounded-lg text-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-400 mx-auto mb-2"></div>
                <p className="text-sm">Updating data...</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
