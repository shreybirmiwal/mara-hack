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

  // Chat and scenario states
  const [chatInput, setChatInput] = useState('');
  const [isProcessingScenario, setIsProcessingScenario] = useState(false);
  const [notification, setNotification] = useState(null); // Single notification

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
        ['>', ['get', 'price_mwh'], 100], '#ef4444',
        ['>', ['get', 'price_mwh'], 50], '#f97316',
        ['>', ['get', 'price_mwh'], 25], '#eab308',
        ['>', ['get', 'price_mwh'], 0], '#22c55e',
        '#6b7280'
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

      if (response.data.success && response.data.notification) {
        // Show single notification with news-style formatting
        const newNotification = {
          id: Date.now(),
          ...response.data.notification,
          timestamp: new Date()
        };

        setNotification(newNotification);
        setChatInput('');

        // Auto-dismiss after 15 seconds
        setTimeout(() => {
          setNotification(null);
        }, 15000);
      }
    } catch (error) {
      console.error('Error processing scenario:', error);
      setError('Failed to process scenario. Please try again.');
    } finally {
      setIsProcessingScenario(false);
    }
  };

  // Remove notification
  const removeNotification = () => {
    setNotification(null);
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
      {/* Breaking News Style Notification - Top Left */}
      {notification && (
        <div className="absolute top-4 left-4 z-50 max-w-md animate-slide-down">
          <div className="bg-red-600 text-white px-4 py-2 shadow-2xl border-l-4 border-red-800">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
                <span className="text-xs font-bold tracking-wider">
                  {notification.timestamp.toLocaleTimeString()} | BREAKING ENERGY ALERT
                </span>
              </div>
              <button
                onClick={removeNotification}
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
      )}

      {/* Map Container */}
      <div className="relative h-full">
        <Map
          ref={mapRef}
          {...viewState}
          onMove={evt => setViewState(evt.viewState)}
          mapStyle="mapbox://styles/mapbox/outdoors-v12"
          mapboxAccessToken={MAPBOX_TOKEN}
          onClick={onMapClick}
          interactiveLayerIds={['energy-points']}
          terrain={{ source: 'mapbox-dem', exaggeration: 1.5 }}
        >
          {/* Terrain Source */}
          <Source
            id="mapbox-dem"
            type="raster-dem"
            url="mapbox://mapbox.mapbox-terrain-dem-v1"
            tileSize={512}
            maxzoom={14}
          />

          {/* Energy Data Sources and Layers */}
          <Source id="energy-data" type="geojson" data={energyLocationsGeoJSON}>
            <Layer {...heatmapLayer} />
            <Layer {...energyPointsLayer} />
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
              <div className="p-3 min-w-64">
                <h3 className="font-bold text-lg text-gray-800 mb-2">
                  {selectedLocation.name}
                </h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Type:</span>
                    <span className="font-semibold text-gray-800">{selectedLocation.type}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Price:</span>
                    <span className="font-bold text-lg" style={{
                      color: selectedLocation.price_mwh > 100 ? '#ef4444' :
                        selectedLocation.price_mwh > 50 ? '#f97316' :
                          selectedLocation.price_mwh > 25 ? '#eab308' : '#22c55e'
                    }}>
                      {formatPrice(selectedLocation.price_mwh)}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Region:</span>
                    <span className="font-semibold text-gray-800">{selectedLocation.region}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Capacity:</span>
                    <span className="font-semibold text-gray-800">{selectedLocation.capacity_mw} MW</span>
                  </div>
                </div>
              </div>
            </Popup>
          )}
        </Map>

        {/* AI Scenario Chat Interface - Bottom */}
        <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 w-full max-w-2xl px-4">
          <form onSubmit={handleScenarioSubmit} className="bg-gray-800/90 backdrop-blur-sm rounded-lg shadow-2xl border border-gray-700">
            <div className="p-4">
              <div className="flex space-x-3">
                <div className="flex-1">
                  <input
                    type="text"
                    value={chatInput}
                    onChange={(e) => setChatInput(e.target.value)}
                    placeholder="Ask about energy scenarios... (e.g., 'What if a hurricane hits the Gulf Coast?')"
                    className="w-full bg-gray-700 text-white placeholder-gray-400 border border-gray-600 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    disabled={isProcessingScenario}
                  />
                </div>
                <button
                  type="submit"
                  disabled={isProcessingScenario || !chatInput.trim()}
                  className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white px-6 py-3 rounded-lg font-medium transition-colors duration-200 flex items-center space-x-2"
                >
                  {isProcessingScenario ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                      <span>Analyzing...</span>
                    </>
                  ) : (
                    <>
                      <span>🤖</span>
                      <span>Analyze</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          </form>
        </div>

        {/* Status Info - Top Right */}
        <div className="absolute top-4 right-4 bg-gray-800/90 backdrop-blur-sm text-white p-3 rounded-lg shadow-lg text-sm">
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-400 rounded-full"></div>
            <span>Live Energy Data</span>
          </div>
          {lastUpdated && (
            <div className="text-gray-300 text-xs mt-1">
              Updated: {lastUpdated}
            </div>
          )}
        </div>

        {/* Error Display */}
        {error && (
          <div className="absolute top-20 left-1/2 transform -translate-x-1/2 bg-red-600 text-white px-6 py-3 rounded-lg shadow-lg max-w-md text-center">
            <p className="font-medium">{error}</p>
            <button
              onClick={() => setError(null)}
              className="mt-2 text-sm underline hover:no-underline"
            >
              Dismiss
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
