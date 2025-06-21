import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import Map, { Source, Layer, Popup } from 'react-map-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import './App.css';

// Mapbox access token - Get your free token at https://account.mapbox.com/access-tokens/
// Instructions: 1. Sign up at mapbox.com, 2. Go to access tokens, 3. Create a token, 4. Replace the token below
const MAPBOX_TOKEN = process.env.REACT_APP_MAPBOX_TOKEN || 'YOUR_MAPBOX_TOKEN_HERE';

function App() {
  const [energyData, setEnergyData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [showPopup, setShowPopup] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [cacheInfo, setCacheInfo] = useState(null);

  // Chat and scenario states
  const [chatInput, setChatInput] = useState('');
  const [isProcessingScenario, setIsProcessingScenario] = useState(false);
  const [notifications, setNotifications] = useState([]);

  // Map state
  const [viewState, setViewState] = useState({
    longitude: -99.9018,
    latitude: 31.9686,
    zoom: 6.5,
    pitch: 45,
    bearing: 0
  });

  const mapRef = useRef();

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      const energyResponse = await axios.get('http://localhost:5001/api/energy-data');

      if (energyResponse.data.success) {
        setEnergyData(energyResponse.data.data || []);
        setLastUpdated(new Date().toLocaleTimeString());
        setCacheInfo({
          cached: energyResponse.data.cached,
          cacheAge: energyResponse.data.cache_age_seconds
        });
      }

    } catch (error) {
      console.error('Error fetching data:', error);
      setError(`Failed to fetch data: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 300000); // Refresh every 5 minutes
    return () => clearInterval(interval);
  }, []);

  // Create GeoJSON for energy locations
  const energyLocationsGeoJSON = {
    type: 'FeatureCollection',
    features: energyData.map(location => ({
      type: 'Feature',
      properties: {
        ...location,
        size: Math.max(10, Math.min(50, (location.price_mwh + 50) / 10)) // Scale point size
      },
      geometry: {
        type: 'Point',
        coordinates: [location.lng, location.lat]
      }
    }))
  };

  // Layer styles
  const energyPointsLayer = {
    id: 'energy-points',
    type: 'circle',
    paint: {
      'circle-radius': [
        'interpolate',
        ['linear'],
        ['get', 'price_mwh'],
        0, 8,
        50, 15,
        100, 25,
        200, 35
      ],
      'circle-color': [
        'case',
        ['>', ['get', 'price_mwh'], 100], '#ff0000',
        ['>', ['get', 'price_mwh'], 50], '#ff8c00',
        ['>', ['get', 'price_mwh'], 25], '#ffd700',
        ['>', ['get', 'price_mwh'], 0], '#32cd32',
        '#808080'
      ],
      'circle-opacity': 0.8,
      'circle-stroke-width': 2,
      'circle-stroke-color': '#ffffff'
    }
  };

  const heatmapLayer = {
    id: 'energy-heatmap',
    type: 'heatmap',
    paint: {
      'heatmap-weight': [
        'interpolate',
        ['linear'],
        ['get', 'price_mwh'],
        0, 0,
        200, 1
      ],
      'heatmap-intensity': 0.6,
      'heatmap-color': [
        'interpolate',
        ['linear'],
        ['heatmap-density'],
        0, 'rgba(33,102,172,0)',
        0.2, 'rgb(103,169,207)',
        0.4, 'rgb(209,229,240)',
        0.6, 'rgb(253,219,199)',
        0.8, 'rgb(239,138,98)',
        1, 'rgb(178,24,43)'
      ],
      'heatmap-radius': 30,
      'heatmap-opacity': 0.7
    }
  };

  const onMapClick = (event) => {
    const features = event.features;
    if (features && features.length > 0) {
      const feature = features[0];
      if (feature.layer.id === 'energy-points') {
        setSelectedLocation({
          ...feature.properties,
          coordinates: feature.geometry.coordinates
        });
        setShowPopup(true);
      }
    }
  };

  const formatPrice = (price) => {
    if (price === null || price === undefined) return 'N/A';
    return `$${price.toFixed(2)}/MWh`;
  };

  // Handle scenario submission
  const handleScenarioSubmit = async (e) => {
    e.preventDefault();
    if (!chatInput.trim() || isProcessingScenario) return;

    setIsProcessingScenario(true);
    try {
      const response = await axios.post('http://localhost:5001/api/scenario-analysis', {
        scenario: chatInput.trim(),
        current_data: energyData
      });

      if (response.data.success) {
        // Add notifications from AI response
        const newNotifications = response.data.notifications.map((notification, index) => ({
          id: Date.now() + index,
          ...notification,
          timestamp: new Date()
        }));

        setNotifications(prev => [...newNotifications, ...prev].slice(0, 10)); // Keep only last 10
        setChatInput('');
      }
    } catch (error) {
      console.error('Error processing scenario:', error);
      setError('Failed to process scenario. Please try again.');
    } finally {
      setIsProcessingScenario(false);
    }
  };

  // Remove notification
  const removeNotification = (id) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  };

  // Check if Mapbox token is configured
  if (MAPBOX_TOKEN === 'YOUR_MAPBOX_TOKEN_HERE') {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center bg-gray-800 p-8 rounded-lg shadow-lg max-w-md">
          <div className="text-yellow-400 text-4xl mb-4">🗺️</div>
          <h2 className="text-white text-xl font-bold mb-4">Mapbox Token Required</h2>
          <p className="text-gray-300 mb-4">
            To use this map, you need a free Mapbox token:
          </p>
          <ol className="text-left text-gray-300 mb-6 space-y-2">
            <li>1. Sign up at <a href="https://account.mapbox.com/auth/signup/" target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:underline">mapbox.com</a></li>
            <li>2. Go to <a href="https://account.mapbox.com/access-tokens/" target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:underline">Access Tokens</a></li>
            <li>3. Create a token with public scopes</li>
            <li>4. Replace 'YOUR_MAPBOX_TOKEN_HERE' in App.js</li>
          </ol>
          <div className="bg-gray-700 p-3 rounded text-sm text-gray-300">
            <p className="font-mono">MAPBOX_TOKEN = 'pk.your_token_here'</p>
          </div>
        </div>
      </div>
    );
  }

  if (loading && energyData.length === 0) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p className="text-white mt-4">Loading West Texas Energy Map...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen bg-gray-900 text-white overflow-hidden">
      {/* Header */}
      <div className="bg-gray-800 p-4 shadow-lg z-10 relative">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-blue-400">
              West Texas Energy Pricing Map
            </h1>
            <p className="text-gray-300 text-sm">
              Real-time ERCOT energy pricing data • AI scenario analysis
            </p>
          </div>
          <div className="text-right">
            <div className="text-sm text-gray-400">
              Last Updated: {lastUpdated || 'Loading...'}
            </div>
            {cacheInfo && (
              <div className="text-xs text-gray-500">
                {cacheInfo.cached ? `Cached (${cacheInfo.cacheAge}s old)` : 'Live data'}
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="flex h-full">
        {/* Map Container */}
        <div className="flex-1 relative">
          <Map
            ref={mapRef}
            {...viewState}
            onMove={evt => setViewState(evt.viewState)}
            mapboxAccessToken={MAPBOX_TOKEN}
            mapStyle="mapbox://styles/mapbox/outdoors-v12"
            onClick={onMapClick}
            interactiveLayerIds={['energy-points']}
          >
            {/* Energy data heatmap */}
            <Source id="energy-heatmap" type="geojson" data={energyLocationsGeoJSON}>
              <Layer {...heatmapLayer} />
            </Source>

            {/* Energy data points */}
            <Source id="energy-data" type="geojson" data={energyLocationsGeoJSON}>
              <Layer {...energyPointsLayer} />
            </Source>

            {/* Popup for selected location */}
            {showPopup && selectedLocation && (
              <Popup
                longitude={selectedLocation.coordinates[0]}
                latitude={selectedLocation.coordinates[1]}
                anchor="bottom"
                onClose={() => setShowPopup(false)}
                closeButton={true}
                closeOnClick={false}
              >
                <div className="bg-gray-800 text-white p-3 rounded-lg shadow-lg min-w-[200px]">
                  <h3 className="font-bold text-lg text-blue-400 mb-2">
                    {selectedLocation.location_name}
                  </h3>
                  <div className="space-y-1 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-300">Type:</span>
                      <span className="font-medium">{selectedLocation.type}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-300">Price:</span>
                      <span className={`font-bold ${selectedLocation.price_mwh > 50 ? 'text-red-400' :
                        selectedLocation.price_mwh > 25 ? 'text-yellow-400' : 'text-green-400'
                        }`}>
                        {formatPrice(selectedLocation.price_mwh)}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-300">Location:</span>
                      <span className="text-xs text-gray-400">
                        {selectedLocation.lat.toFixed(3)}, {selectedLocation.lng.toFixed(3)}
                      </span>
                    </div>
                    {selectedLocation.timestamp && (
                      <div className="flex justify-between">
                        <span className="text-gray-300">Time:</span>
                        <span className="text-xs text-gray-400">
                          {new Date(selectedLocation.timestamp).toLocaleTimeString()}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              </Popup>
            )}
          </Map>

          {/* Map Controls */}
          <div className="absolute top-4 right-4 bg-gray-800 bg-opacity-90 rounded-lg p-3 space-y-2">
            <button
              onClick={() => setViewState(prev => ({ ...prev, zoom: prev.zoom + 0.5 }))}
              className="block w-full px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded text-sm"
            >
              Zoom In
            </button>
            <button
              onClick={() => setViewState(prev => ({ ...prev, zoom: prev.zoom - 0.5 }))}
              className="block w-full px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded text-sm"
            >
              Zoom Out
            </button>
            <button
              onClick={() => setViewState({
                longitude: -99.9018,
                latitude: 31.9686,
                zoom: 6.5,
                pitch: 45,
                bearing: 0
              })}
              className="block w-full px-3 py-1 bg-green-600 hover:bg-green-700 rounded text-sm"
            >
              Reset View
            </button>
          </div>

          {/* Legend */}
          <div className="absolute bottom-4 left-4 bg-gray-800 bg-opacity-90 rounded-lg p-4">
            <h3 className="font-bold text-sm mb-3 text-blue-400">Energy Pricing Legend</h3>
            <div className="space-y-2 text-xs">
              <div className="flex items-center">
                <div className="w-4 h-4 rounded-full bg-red-500 mr-2"></div>
                <span>Very High (&gt;$100/MWh)</span>
              </div>
              <div className="flex items-center">
                <div className="w-4 h-4 rounded-full bg-orange-500 mr-2"></div>
                <span>High ($50-100/MWh)</span>
              </div>
              <div className="flex items-center">
                <div className="w-4 h-4 rounded-full bg-yellow-500 mr-2"></div>
                <span>Medium ($25-50/MWh)</span>
              </div>
              <div className="flex items-center">
                <div className="w-4 h-4 rounded-full bg-green-500 mr-2"></div>
                <span>Low ($0-25/MWh)</span>
              </div>
              <div className="flex items-center">
                <div className="w-4 h-4 rounded-full bg-gray-500 mr-2"></div>
                <span>Zero/Negative</span>
              </div>
            </div>
            <div className="mt-3 pt-3 border-t border-gray-600">
              <div className="text-xs text-gray-400">
                • Point size = relative price
              </div>
              <div className="text-xs text-gray-400">
                • Click points for details
              </div>
            </div>
          </div>

          {/* Notification Popups */}
          <div className="absolute top-4 left-1/2 transform -translate-x-1/2 space-y-2 max-w-md z-50">
            {notifications.map((notification) => (
              <div
                key={notification.id}
                className={`bg-gray-800 bg-opacity-95 border-l-4 rounded-lg p-4 shadow-lg animate-slide-down ${notification.type === 'alert' ? 'border-red-500' :
                  notification.type === 'warning' ? 'border-yellow-500' :
                    notification.type === 'info' ? 'border-blue-500' :
                      'border-green-500'
                  }`}
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center mb-2">
                      <span className={`text-lg mr-2 ${notification.type === 'alert' ? 'text-red-400' :
                        notification.type === 'warning' ? 'text-yellow-400' :
                          notification.type === 'info' ? 'text-blue-400' :
                            'text-green-400'
                        }`}>
                        {notification.type === 'alert' ? '🚨' :
                          notification.type === 'warning' ? '⚠️' :
                            notification.type === 'info' ? 'ℹ️' : '✅'}
                      </span>
                      <h4 className="font-bold text-white text-sm">{notification.title}</h4>
                    </div>
                    <p className="text-gray-300 text-sm">{notification.message}</p>
                    {notification.impact && (
                      <p className="text-xs text-gray-400 mt-1">
                        Impact: {notification.impact}
                      </p>
                    )}
                  </div>
                  <button
                    onClick={() => removeNotification(notification.id)}
                    className="text-gray-400 hover:text-white ml-2"
                  >
                    ×
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Chat Sidebar */}
        <div className="w-80 bg-gray-800 flex flex-col">
          {/* Chat Header */}
          <div className="p-4 border-b border-gray-700">
            <h2 className="text-lg font-bold text-blue-400 mb-2">AI Scenario Analysis</h2>
            <p className="text-gray-400 text-sm">
              Ask what would happen if certain events occurred in West Texas energy markets.
            </p>
          </div>

          {/* Chat Input */}
          <div className="p-4 border-b border-gray-700">
            <form onSubmit={handleScenarioSubmit}>
              <div className="space-y-3">
                <textarea
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  placeholder="What would happen if a hurricane hit the Gulf Coast? Or if wind speeds doubled in West Texas?"
                  className="w-full h-24 bg-gray-700 border border-gray-600 rounded-lg p-3 text-white placeholder-gray-400 resize-none focus:outline-none focus:border-blue-500"
                  disabled={isProcessingScenario}
                />
                <button
                  type="submit"
                  disabled={!chatInput.trim() || isProcessingScenario}
                  className="w-full py-2 px-4 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-lg font-medium transition-colors"
                >
                  {isProcessingScenario ? (
                    <div className="flex items-center justify-center">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Analyzing...
                    </div>
                  ) : (
                    'Analyze Scenario'
                  )}
                </button>
              </div>
            </form>
          </div>

          {/* Recent Notifications History */}
          <div className="flex-1 overflow-y-auto p-4">
            <h3 className="text-md font-bold text-gray-300 mb-3">Recent Scenarios</h3>
            {notifications.length === 0 ? (
              <div className="text-gray-500 text-sm text-center py-8">
                <div className="text-4xl mb-2">🤖</div>
                <p>No scenarios analyzed yet.</p>
                <p className="mt-2">Try asking about weather events, infrastructure failures, or market changes!</p>
              </div>
            ) : (
              <div className="space-y-3">
                {notifications.map((notification) => (
                  <div
                    key={notification.id}
                    className="bg-gray-700 rounded-lg p-3 text-sm"
                  >
                    <div className="flex items-center mb-1">
                      <span className="text-xs text-gray-400">
                        {notification.timestamp.toLocaleTimeString()}
                      </span>
                    </div>
                    <div className="font-medium text-white mb-1">{notification.title}</div>
                    <div className="text-gray-300">{notification.message}</div>
                    {notification.impact && (
                      <div className="text-xs text-blue-400 mt-1">
                        {notification.impact}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Error Display */}
          {error && (
            <div className="p-4 border-t border-gray-700">
              <div className="bg-red-900 bg-opacity-50 border border-red-700 rounded-lg p-3">
                <h3 className="text-red-400 font-bold text-sm">Error</h3>
                <p className="text-red-300 text-xs mt-1">{error}</p>
                <button
                  onClick={fetchData}
                  className="mt-2 px-3 py-1 bg-red-600 hover:bg-red-700 rounded text-xs"
                >
                  Retry
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
