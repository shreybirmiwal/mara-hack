import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import Map, { Source, Layer, Popup } from 'react-map-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import './App.css';

// Mapbox access token - Get your free token at https://account.mapbox.com/access-tokens/
// Instructions: 1. Sign up at mapbox.com, 2. Go to access tokens, 3. Create a token, 4. Replace the token below
const MAPBOX_TOKEN = process.env.REACT_APP_MAPBOX_TOKEN || 'YOUR_MAPBOX_TOKEN_HERE';

// Simple trend chart component
const MiniChart = ({ data, width = 120, height = 40 }) => {
  // Ensure data is an array and has at least 2 points
  if (!data || !Array.isArray(data) || data.length < 2) {
    return <span className="text-xs text-gray-500">No trend data</span>;
  }

  // Filter out any invalid values
  const validData = data.filter(val => typeof val === 'number' && !isNaN(val));
  if (validData.length < 2) {
    return <span className="text-xs text-gray-500">Insufficient data</span>;
  }

  const max = Math.max(...validData);
  const min = Math.min(...validData);
  const range = max - min || 1;

  const points = validData.map((value, index) => {
    const x = (index / (validData.length - 1)) * width;
    const y = height - ((value - min) / range) * height;
    return `${x},${y}`;
  }).join(' ');

  return (
    <svg width={width} height={height} className="inline-block">
      <polyline
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        points={points}
      />
      <circle
        cx={(validData.length - 1) / (validData.length - 1) * width}
        cy={height - ((validData[validData.length - 1] - min) / range) * height}
        r="2"
        fill="currentColor"
      />
    </svg>
  );
};

function App() {
  const [energyData, setEnergyData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [showPopup, setShowPopup] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [isProcessingScenario, setIsProcessingScenario] = useState(false);
  const [scenarioEffectsActive, setScenarioEffectsActive] = useState(false);
  const [showNewsTab, setShowNewsTab] = useState(true); // Always show news panel
  const [allEffects, setAllEffects] = useState([]);

  const mapRef = useRef();

  const [viewState, setViewState] = useState({
    longitude: -99.9018,
    latitude: 31.9686,
    zoom: 6.5,
    pitch: 45,
    bearing: 0
  });

  const fetchData = async () => {
    try {
      setLoading(true);
      const response = await axios.get('http://localhost:5001/api/energy-data');

      if (response.data.success) {
        setEnergyData(response.data.data);
        setError(null);
      } else {
        setError('Failed to fetch energy data');
      }
    } catch (err) {
      console.error('Error fetching data:', err);
      setError('Failed to connect to backend');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();

    // Auto-refresh every 30 seconds to see price changes
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  // Create GeoJSON for energy locations
  const energyLocationsGeoJSON = {
    type: 'FeatureCollection',
    features: energyData.map(location => ({
      type: 'Feature',
      geometry: {
        type: 'Point',
        coordinates: [location.lng, location.lat]
      },
      properties: {
        ...location
      }
    }))
  };

  // Energy points layer
  const energyPointsLayer = {
    id: 'energy-points',
    type: 'circle',
    paint: {
      'circle-radius': [
        'interpolate',
        ['linear'],
        ['get', 'price_mwh'],
        0, 6,
        50, 10,
        100, 14,
        200, 18,
        500, 22
      ],
      'circle-color': [
        'interpolate',
        ['linear'],
        ['get', 'price_mwh'],
        0, '#22c55e',
        25, '#eab308',
        50, '#f97316',
        100, '#ef4444',
        200, '#991b1b',
        500, '#7c2d12'
      ],
      'circle-stroke-width': [
        'case',
        ['==', ['get', 'scenario_affected'], true],
        4, // Thicker stroke for affected locations
        2
      ],
      'circle-stroke-color': [
        'case',
        ['==', ['get', 'scenario_affected'], true],
        '#fbbf24', // Gold stroke for affected locations
        '#ffffff'
      ],
      'circle-opacity': [
        'case',
        ['==', ['get', 'scenario_affected'], true],
        1.0, // Full opacity for affected locations
        0.8
      ]
    }
  };

  // Scenario effects layer (pulsing animation for affected locations)
  const scenarioEffectsLayer = {
    id: 'scenario-effects',
    type: 'circle',
    filter: ['==', ['get', 'scenario_affected'], true],
    paint: {
      'circle-radius': [
        'interpolate',
        ['linear'],
        ['get', 'price_mwh'],
        0, 15,
        50, 20,
        100, 25,
        200, 30,
        500, 35
      ],
      'circle-color': '#fbbf24',
      'circle-opacity': 0.3,
      'circle-stroke-width': 2,
      'circle-stroke-color': '#f59e0b',
      'circle-stroke-opacity': 0.6
    }
  };

  // Heatmap layer
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
      'heatmap-intensity': [
        'interpolate',
        ['linear'],
        ['zoom'],
        0, 1,
        9, 3
      ],
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
      'heatmap-opacity': 0.4
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

  const formatPriceChange = (change, percent) => {
    if (change === 0) return 'No change';
    const sign = change > 0 ? '+' : '';
    return `${sign}$${change.toFixed(2)} (${sign}${percent.toFixed(1)}%)`;
  };

  const getTrendIcon = (trend) => {
    switch (trend) {
      case 'rising': return '📈';
      case 'falling': return '📉';
      default: return '➡️';
    }
  };

  const getTrendColor = (trend) => {
    switch (trend) {
      case 'rising': return '#ef4444';
      case 'falling': return '#22c55e';
      default: return '#6b7280';
    }
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
        // Handle multiple notifications
        if (response.data.notifications && Array.isArray(response.data.notifications)) {
          const newNotifications = response.data.notifications.map((notif, index) => ({
            id: Date.now() + index,
            ...notif,
            timestamp: new Date()
          }));

          setNotifications(newNotifications);

          // Auto-dismiss notifications after 20 seconds
          setTimeout(() => {
            setNotifications([]);
          }, 20000);
        }

        // Update energy data with scenario effects if available
        if (response.data.modified_data) {
          setEnergyData(response.data.modified_data);
          setScenarioEffectsActive(true);

          // Store all effects for the news tab
          if (response.data.effects_summary) {
            setAllEffects(prev => [...prev, ...response.data.effects_summary]);
          }

          // Simulation now runs indefinitely - no auto-reset
        }

        setChatInput('');
      }
    } catch (error) {
      console.error('Error processing scenario:', error);
      setError('Failed to process scenario. Please try again.');
    } finally {
      setIsProcessingScenario(false);
    }
  };

  // Remove specific notification
  const removeNotification = (id) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  };

  // Clear all notifications
  const clearAllNotifications = () => {
    setNotifications([]);
  };

  // Function to zoom to a specific location on the map
  const zoomToLocation = (lat, lng, name) => {
    if (mapRef.current) {
      setViewState({
        longitude: lng,
        latitude: lat,
        zoom: 12,
        pitch: 45,
        bearing: 0
      });

      // Find the location in energyData and show popup
      const location = energyData.find(loc => loc.lat === lat && loc.lng === lng);
      if (location) {
        setSelectedLocation({
          ...location,
          coordinates: [lng, lat]
        });
        setShowPopup(true);
      }
    }
  };

  // Check if Mapbox token is configured
  if (MAPBOX_TOKEN === 'YOUR_MAPBOX_TOKEN_HERE') {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center bg-gray-800 p-8 rounded-lg shadow-lg max-w-md">
          <div className="text-yellow-400 text-4xl mb-4">🗺️</div>
          <h2 className="text-white text-xl font-bold mb-4">Mapbox Token Required</h2>
          <p className="text-gray-300 mb-4">
            To use this application, you need a free Mapbox access token.
          </p>
          <div className="text-left bg-gray-700 p-4 rounded text-sm text-gray-300 mb-4">
            <p className="font-semibold mb-2">Setup Instructions:</p>
            <ol className="list-decimal list-inside space-y-1">
              <li>Go to <span className="text-blue-400">account.mapbox.com</span></li>
              <li>Sign up for a free account</li>
              <li>Navigate to "Access tokens"</li>
              <li>Create a new token</li>
              <li>Add it to your .env file as REACT_APP_MAPBOX_TOKEN</li>
            </ol>
          </div>
          <button
            onClick={() => window.open('https://account.mapbox.com/access-tokens/', '_blank')}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded"
          >
            Get Mapbox Token
          </button>
        </div>
      </div>
    );
  }

  if (loading && energyData.length === 0) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-white text-xl">Loading energy data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen bg-gray-900 relative overflow-hidden">
      {/* Multiple Breaking News Style Notifications - Top Left */}
      {notifications.length > 0 && (
        <div className="absolute top-4 left-4 z-50 max-w-md space-y-3">
          {/* Clear All Button */}
          {notifications.length > 1 && (
            <div className="flex justify-end">
              <button
                onClick={clearAllNotifications}
                className="bg-gray-700 hover:bg-gray-600 text-white px-2 py-1 rounded text-xs"
              >
                Clear All ({notifications.length})
              </button>
            </div>
          )}

          {/* Notifications */}
          {notifications.map((notification, index) => (
            <div key={notification.id} className="animate-slide-down" style={{ animationDelay: `${index * 200}ms` }}>
              <div className="bg-red-600 text-white px-4 py-2 shadow-2xl border-l-4 border-red-800">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
                    <span className="text-xs font-bold tracking-wider">
                      {notification.timestamp.toLocaleTimeString()} | BREAKING ENERGY ALERT
                    </span>
                  </div>
                  <button
                    onClick={() => removeNotification(notification.id)}
                    className="text-white hover:text-red-200 text-lg font-bold"
                  >
                    ×
                  </button>
                </div>
                <div className="mt-2 text-sm font-medium leading-relaxed">
                  {notification.message}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* News panel is now always visible */}

      {/* News/Nodes Side Panel - Always Visible */}
      <div className="fixed top-0 right-0 w-96 h-full bg-gray-900 bg-opacity-95 backdrop-blur-sm z-40 overflow-y-auto border-l border-gray-700">
        <div className="p-4">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-white text-xl font-bold flex items-center space-x-2">
              <span>📰</span>
              <span>Live News & Affected Nodes</span>
            </h2>
            {/* Close button removed - panel always visible */}
          </div>

          {/* Active Notifications */}
          {notifications.length > 0 && (
            <div className="mb-6">
              <h3 className="text-white text-lg font-semibold mb-3 flex items-center space-x-2">
                <span className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></span>
                <span>Breaking News</span>
              </h3>
              <div className="space-y-3">
                {notifications.map((notification) => (
                  <div key={notification.id} className="bg-red-800 bg-opacity-50 p-3 rounded-lg border border-red-600">
                    <div className="text-red-200 text-sm font-medium">
                      {notification.timestamp.toLocaleTimeString()} | {notification.region || 'Texas Grid'}
                    </div>
                    <div className="text-white text-sm mt-1">
                      {notification.message}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Affected Nodes */}
          {allEffects.length > 0 && (
            <div className="mb-6">
              <h3 className="text-white text-lg font-semibold mb-3 flex items-center space-x-2">
                <span>⚡</span>
                <span>Affected Nodes ({allEffects.length})</span>
              </h3>
              <div className="space-y-2">
                {allEffects.map((effect, index) => (
                  <div key={index} className="bg-gray-800 bg-opacity-70 p-3 rounded-lg border border-gray-600 hover:bg-gray-700 cursor-pointer transition-colors duration-200"
                    onClick={() => {
                      // Find the location in energyData to get coordinates
                      const location = energyData.find(loc => loc.name === effect.location);
                      if (location) {
                        zoomToLocation(location.lat, location.lng, location.name);
                        // Panel stays open since it's always visible now
                      }
                    }}
                  >
                    <div className="flex justify-between items-start mb-2">
                      <div className="text-white font-semibold text-sm">
                        {effect.location}
                      </div>
                      <div className={`text-sm font-bold ${effect.change_percent > 0 ? 'text-red-400' : 'text-green-400'
                        }`}>
                        {effect.change_percent > 0 ? '▲' : '▼'} {Math.abs(effect.change_percent)}%
                      </div>
                    </div>
                    <div className="text-gray-300 text-xs mb-2">
                      {effect.effect}
                    </div>
                    <div className="flex justify-between items-center text-xs">
                      <span className="text-gray-400">
                        ${effect.old_price.toFixed(2)} → ${effect.new_price.toFixed(2)}
                      </span>
                      <span className="text-blue-400 hover:text-blue-300">
                        📍 Zoom to location
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Clear All Button */}
          {(notifications.length > 0 || allEffects.length > 0) && (
            <button
              onClick={() => {
                setNotifications([]);
                setAllEffects([]);
              }}
              className="w-full bg-gray-700 hover:bg-gray-600 text-white py-2 px-4 rounded-lg transition-colors duration-200"
            >
              Clear All News & Effects
            </button>
          )}

          {/* No Data State */}
          {notifications.length === 0 && allEffects.length === 0 && (
            <div className="text-center text-gray-400 py-8">
              <div className="text-4xl mb-4">📡</div>
              <div className="text-lg mb-2">No active news or effects</div>
              <div className="text-sm">
                Run a scenario simulation to see live updates and affected nodes here.
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Map Container */}
      <div className="relative h-full">
        <Map
          ref={mapRef}
          {...viewState}
          onMove={evt => setViewState(evt.viewState)}
          mapStyle="mapbox://styles/mapbox/dark-v11"
          mapboxAccessToken={MAPBOX_TOKEN}
          onClick={onMapClick}
          interactiveLayerIds={['energy-points']}
          terrain={{ source: 'mapbox-dem', exaggeration: 1.5 }}
        >
          {/* Terrain Source */}
          <Source
            id="mapbox-dem"
            type="raster-dem"
            url="mapbox://styles/mapbox/outdoors-v12"
            tileSize={512}
            maxzoom={14}
          />

          {/* Energy Data Sources and Layers */}
          <Source id="energy-data" type="geojson" data={energyLocationsGeoJSON}>
            <Layer {...heatmapLayer} />
            <Layer {...energyPointsLayer} />
            {scenarioEffectsActive && <Layer {...scenarioEffectsLayer} />}
          </Source>

          {/* Location Popup */}
          {showPopup && selectedLocation && (
            <Popup
              longitude={selectedLocation.coordinates[0]}
              latitude={selectedLocation.coordinates[1]}
              onClose={() => setShowPopup(false)}
              closeButton={true}
              closeOnClick={false}
              className="custom-popup"
            >
              <div className="p-4">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-bold text-lg text-gray-800">
                    {selectedLocation.name}
                  </h3>
                  {selectedLocation.scenario_affected && (
                    <span className="bg-yellow-500 text-yellow-900 px-2 py-1 rounded text-xs font-bold animate-pulse">
                      SCENARIO ACTIVE
                    </span>
                  )}
                </div>

                {selectedLocation.scenario_affected && (
                  <div className="bg-yellow-50 border-l-4 border-yellow-400 p-3 mb-3">
                    <div className="text-sm text-yellow-800">
                      <strong>Scenario Effect:</strong> {selectedLocation.scenario_effect}
                    </div>
                  </div>
                )}

                <div className="space-y-3 text-sm">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">Type:</span>
                    <span className="font-semibold text-gray-800">{selectedLocation.type || 'Unknown'}</span>
                  </div>

                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">Region:</span>
                    <span className="font-semibold text-gray-800">{selectedLocation.region || 'West Texas'}</span>
                  </div>

                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">Capacity:</span>
                    <span className="font-semibold text-gray-800">{selectedLocation.capacity_mw || 100} MW</span>
                  </div>

                  <hr className="border-gray-200" />

                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">Current Price:</span>
                    <span className="font-bold text-lg" style={{
                      color: selectedLocation.price_mwh > 100 ? '#ef4444' :
                        selectedLocation.price_mwh > 50 ? '#f97316' :
                          selectedLocation.price_mwh > 25 ? '#eab308' : '#22c55e'
                    }}>
                      {formatPrice(selectedLocation.price_mwh)}
                    </span>
                  </div>

                  {selectedLocation.price_change !== undefined && selectedLocation.price_change !== null && (
                    <div className="flex justify-between items-center">
                      <span className="text-gray-600">Price Change:</span>
                      <div className="flex items-center space-x-1">
                        <span className="text-lg">{getTrendIcon(selectedLocation.trend || 'stable')}</span>
                        <span
                          className="font-semibold text-sm"
                          style={{ color: getTrendColor(selectedLocation.trend || 'stable') }}
                        >
                          {formatPriceChange(selectedLocation.price_change || 0, selectedLocation.price_change_percent || 0)}
                        </span>
                      </div>
                    </div>
                  )}

                  {selectedLocation.price_history && (
                    <div>
                      <div className="flex justify-between items-center mb-2">
                        <span className="text-gray-600">Price Trend:</span>
                        <div style={{ color: getTrendColor(selectedLocation.trend || 'stable') }}>
                          <MiniChart data={selectedLocation.price_history} />
                        </div>
                      </div>
                      {Array.isArray(selectedLocation.price_history) && selectedLocation.price_history.length > 0 && (
                        <div className="text-xs text-gray-500">
                          Last {selectedLocation.price_history.length} data points
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </Popup>
          )}
        </Map>

        {/* Scenario Status Indicator - Top Right */}
        {scenarioEffectsActive && (
          <div className="absolute top-4 right-[25rem] z-50">
            <div className="bg-yellow-600 text-white px-4 py-2 rounded-lg shadow-lg border border-yellow-500">
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
                <span className="text-sm font-bold">SCENARIO SIMULATION ACTIVE</span>
              </div>
              <div className="text-xs opacity-90 mt-1">
                Simulation running indefinitely
              </div>
            </div>
          </div>
        )}

        {/* AI Scenario Chat Interface - Bottom */}
        <div className="absolute bottom-4 left-4 right-[25rem] z-40">
          <div className="bg-gray-800 bg-opacity-95 backdrop-blur-sm rounded-lg shadow-2xl border border-gray-700">
            <div className="p-4">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-blue-500 rounded-full animate-pulse"></div>
                  <span className="text-white font-semibold text-sm">Simulate Anything...</span>
                </div>
                {scenarioEffectsActive && (
                  <span className="text-yellow-400 text-xs font-bold">
                    ⚡ SIMULATION RUNNING
                  </span>
                )}
              </div>

              <form onSubmit={handleScenarioSubmit} className="flex space-x-3">
                <input
                  type="text"
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  placeholder="Try: 'What would happen if a hurricane hits the Gulf Coast?'"
                  className="flex-1 bg-gray-700 text-white px-4 py-3 rounded-lg border border-gray-600 focus:border-blue-500 focus:outline-none placeholder-gray-400"
                  disabled={isProcessingScenario}
                />
                <button
                  type="submit"
                  disabled={isProcessingScenario || !chatInput.trim()}
                  className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white px-6 py-3 rounded-lg font-semibold transition-colors duration-200 flex items-center space-x-2"
                >
                  {isProcessingScenario ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                      <span>Analyzing...</span>
                    </>
                  ) : (
                    <>
                      <span>🔮</span>
                      <span>Analyze</span>
                    </>
                  )}
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
