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
  const [marketStats, setMarketStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [showPopup, setShowPopup] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [cacheInfo, setCacheInfo] = useState(null);

  // Map state
  const [viewState, setViewState] = useState({
    longitude: -99.9018,
    latitude: 31.9686,
    zoom: 6.5,
    pitch: 45,
    bearing: 0
  });

  const mapRef = useRef();

  // West Texas regions for visualization
  const westTexasRegions = {
    "type": "FeatureCollection",
    "features": [
      {
        "type": "Feature",
        "properties": {
          "name": "Permian Basin",
          "type": "Oil & Gas Region",
          "description": "Major oil and natural gas producing region"
        },
        "geometry": {
          "type": "Polygon",
          "coordinates": [[
            [-103.5, 32.5], [-101.5, 32.5], [-101.5, 30.5], [-103.5, 30.5], [-103.5, 32.5]
          ]]
        }
      },
      {
        "type": "Feature",
        "properties": {
          "name": "Wind Corridor",
          "type": "Renewable Energy Zone",
          "description": "High wind energy potential area"
        },
        "geometry": {
          "type": "Polygon",
          "coordinates": [[
            [-102.0, 33.5], [-99.5, 33.5], [-99.5, 31.5], [-102.0, 31.5], [-102.0, 33.5]
          ]]
        }
      }
    ]
  };

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [energyResponse, statsResponse] = await Promise.all([
        axios.get('http://localhost:5001/api/energy-data'),
        axios.get('http://localhost:5001/api/energy-stats')
      ]);

      if (energyResponse.data.success) {
        setEnergyData(energyResponse.data.data || []);
        setLastUpdated(new Date().toLocaleTimeString());
        setCacheInfo({
          cached: energyResponse.data.cached,
          cacheAge: energyResponse.data.cache_age_seconds
        });
      }

      if (statsResponse.data.success) {
        setMarketStats(statsResponse.data.stats || {});
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
  const regionLayer = {
    id: 'regions',
    type: 'fill',
    paint: {
      'fill-color': [
        'match',
        ['get', 'type'],
        'Oil & Gas Region', '#8B4513',
        'Renewable Energy Zone', '#228B22',
        '#666666'
      ],
      'fill-opacity': 0.1
    }
  };

  const regionBorderLayer = {
    id: 'region-borders',
    type: 'line',
    paint: {
      'line-color': [
        'match',
        ['get', 'type'],
        'Oil & Gas Region', '#8B4513',
        'Renewable Energy Zone', '#228B22',
        '#666666'
      ],
      'line-width': 2,
      'line-opacity': 0.8
    }
  };

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

  const getTopExpensiveLocations = () => {
    return energyData
      .sort((a, b) => b.price_mwh - a.price_mwh)
      .slice(0, 5);
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
              Real-time ERCOT energy pricing data • Interactive topographical visualization
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

            {/* West Texas regions */}
            <Source id="regions" type="geojson" data={westTexasRegions}>
              <Layer {...regionLayer} />
              <Layer {...regionBorderLayer} />
            </Source>

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
        </div>

        {/* Sidebar */}
        <div className="w-80 bg-gray-800 overflow-y-auto">
          {/* Market Overview */}
          <div className="p-4 border-b border-gray-700">
            <h2 className="text-lg font-bold text-blue-400 mb-3">Market Snapshot</h2>
            {marketStats ? (
              <div className="space-y-3">
                <div className="bg-gray-700 rounded-lg p-3">
                  <div className="text-xs text-gray-400 uppercase tracking-wide">Current Moment</div>
                  <div className="text-lg font-bold text-white">
                    {marketStats.data_timestamp ?
                      new Date(marketStats.data_timestamp).toLocaleString() : 'N/A'}
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div className="bg-gray-700 rounded-lg p-3">
                    <div className="text-xs text-gray-400 uppercase tracking-wide">Locations</div>
                    <div className="text-xl font-bold text-white">{marketStats.locations_count || 0}</div>
                  </div>
                  <div className="bg-gray-700 rounded-lg p-3">
                    <div className="text-xs text-gray-400 uppercase tracking-wide">Avg Price</div>
                    <div className="text-xl font-bold text-blue-400">
                      {formatPrice(marketStats.avg_price)}
                    </div>
                  </div>
                  <div className="bg-red-900 bg-opacity-50 rounded-lg p-3">
                    <div className="text-xs text-gray-400 uppercase tracking-wide">Max Price</div>
                    <div className="text-xl font-bold text-red-400">
                      {formatPrice(marketStats.max_price)}
                    </div>
                  </div>
                  <div className="bg-green-900 bg-opacity-50 rounded-lg p-3">
                    <div className="text-xs text-gray-400 uppercase tracking-wide">Min Price</div>
                    <div className="text-xl font-bold text-green-400">
                      {formatPrice(marketStats.min_price)}
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-gray-400">Loading market data...</div>
            )}
          </div>

          {/* Top Expensive Locations */}
          <div className="p-4 border-b border-gray-700">
            <h3 className="text-md font-bold text-red-400 mb-3">Top 5 Highest Prices</h3>
            <div className="space-y-2">
              {getTopExpensiveLocations().map((location, index) => (
                <div
                  key={location.location_code}
                  className="bg-gray-700 rounded-lg p-3 cursor-pointer hover:bg-gray-600 transition-colors"
                  onClick={() => {
                    setSelectedLocation({
                      ...location,
                      coordinates: [location.lng, location.lat]
                    });
                    setShowPopup(true);
                    setViewState(prev => ({
                      ...prev,
                      longitude: location.lng,
                      latitude: location.lat,
                      zoom: 9
                    }));
                  }}
                >
                  <div className="flex justify-between items-center">
                    <div>
                      <div className="font-medium text-white text-sm">
                        #{index + 1} {location.location_name}
                      </div>
                      <div className="text-xs text-gray-400">{location.type}</div>
                    </div>
                    <div className="text-right">
                      <div className="font-bold text-red-400">
                        {formatPrice(location.price_mwh)}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Instructions */}
          <div className="p-4">
            <h3 className="text-md font-bold text-gray-400 mb-3">How to Use</h3>
            <div className="space-y-2 text-sm text-gray-300">
              <div>• <strong>Click</strong> energy points for detailed info</div>
              <div>• <strong>Drag</strong> to pan around the map</div>
              <div>• <strong>Scroll</strong> to zoom in/out</div>
              <div>• <strong>Heatmap</strong> shows price intensity</div>
              <div>• <strong>Regions</strong> show energy zones</div>
              <div>• Data updates every 5 minutes</div>
            </div>
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
