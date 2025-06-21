import React, { useState, useCallback } from 'react';
import Map, { Marker, Popup } from 'react-map-gl';
import 'mapbox-gl/dist/mapbox-gl.css';

const MAPBOX_TOKEN = process.env.REACT_APP_MAPBOX_TOKEN || 'pk.eyJ1Ijoic2hyZXliIiwiYSI6ImNtYzZxMGMzbTE2NmwybXB0c21wODc3am8ifQ.CvTe9eKqRgGaEgGRp3ApTw';

const MapComponent = ({ siteData }) => {
  const [selectedSite, setSelectedSite] = useState(null);
  const [hoverInfo, setHoverInfo] = useState(null);

  const [viewState, setViewState] = useState({
    longitude: -95.7129,
    latitude: 37.0902,
    zoom: 4
  });

  // Get profit category for marker color
  const getProfitCategory = useCallback((profit) => {
    if (profit <= 0) return 'profit-zero';
    if (profit < 500000) return 'profit-low';
    if (profit < 1500000) return 'profit-medium';
    return 'profit-high';
  }, []);

  // Format numbers with commas
  const formatNumber = useCallback((num) => {
    return num.toLocaleString();
  }, []);

  // Format currency
  const formatCurrency = useCallback((num) => {
    return `$${num.toLocaleString()}`;
  }, []);

  // Handle marker hover
  const onMarkerHover = useCallback((site) => {
    setHoverInfo({
      site: site
    });
  }, []);

  // Handle marker leave
  const onMarkerLeave = useCallback(() => {
    setHoverInfo(null);
  }, []);

  // Handle marker click
  const onMarkerClick = useCallback((site) => {
    setSelectedSite(site.id === selectedSite ? null : site.id);
  }, [selectedSite]);

  // Render efficiency meter
  const EfficiencyMeter = ({ label, value, type }) => {
    const percentage = Math.round(value * 100);
    return (
      <div className="efficiency-bar">
        <div className="efficiency-label">{label}:</div>
        <div className="efficiency-meter">
          <div 
            className="efficiency-fill" 
            style={{ width: `${percentage}%` }}
          ></div>
        </div>
        <div className="efficiency-value">{percentage}%</div>
      </div>
    );
  };

  // Render machine allocation grid
  const MachineGrid = ({ allocation, limits }) => {
    const machines = [
      { key: 'air_miners', label: 'Air', icon: '🌬️' },
      { key: 'hydro_miners', label: 'Hydro', icon: '💧' },
      { key: 'immersion_miners', label: 'Immersion', icon: '🌊' },
      { key: 'gpu_compute', label: 'GPU', icon: '🖥️' },
      { key: 'asic_compute', label: 'ASIC', icon: '⚡' }
    ];

    return (
      <div className="machine-grid">
        {machines.map(machine => {
          const count = allocation[machine.key] || 0;
          const limit = limits[machine.key] || 0;
          return (
            <div key={machine.key} className="machine-item">
              <span className="machine-type">
                {machine.icon} {machine.label}
              </span>
              <span className={`machine-count ${count === 0 ? 'zero' : ''}`}>
                {count}/{limit}
              </span>
            </div>
          );
        })}
      </div>
    );
  };

  return (
    <div className="map-container" style={{ minHeight: '400px' }}>
      <Map
        {...viewState}
        onMove={evt => setViewState(evt.viewState)}
        mapboxAccessToken={MAPBOX_TOKEN}
        style={{ width: '100%', height: '100%', minHeight: '400px' }}
        mapStyle="mapbox://styles/mapbox/dark-v11"
        interactiveLayerIds={[]}
        onLoad={() => console.log('Map loaded successfully')}
        onError={(err) => console.error('Map error:', err)}
      >
        {siteData.sites.map((site) => (
          <Marker
            key={site.id}
            longitude={site.coordinates.lng}
            latitude={site.coordinates.lat}
            anchor="center"
          >
            <div
              className={`marker ${getProfitCategory(site.optimization.net_profit)}`}
              onMouseEnter={() => onMarkerHover(site)}
              onMouseLeave={onMarkerLeave}
              onClick={() => onMarkerClick(site)}
            />
          </Marker>
        ))}

        {/* Popup for clicked site */}
        {selectedSite && (() => {
          const site = siteData.sites.find(s => s.id === selectedSite);
          if (!site) return null;
          
          return (
            <Popup
              longitude={site.coordinates.lng}
              latitude={site.coordinates.lat}
              anchor="top"
              onClose={() => setSelectedSite(null)}
              closeOnClick={false}
              focusAfterOpen={false}
            >
              <div className="tooltip">
                <div className="tooltip-header">{site.name}</div>
                <div className="tooltip-location">{site.location}</div>
                
                <div className="tooltip-section">
                  <div className="profit-info">
                    <div className="profit-main">
                      Net Profit: {formatCurrency(site.optimization.net_profit)}
                    </div>
                    <div className="profit-details">
                      Revenue: {formatCurrency(site.optimization.total_revenue)} | 
                      Cost: {formatCurrency(site.optimization.total_cost)}
                    </div>
                  </div>
                </div>

                <div className="tooltip-section">
                  <div className="electricity-info">
                    <div className="electricity-cost">
                      Electricity: ${site.electricity_cost_per_mwh}/MWh ({site.electricity_multiplier}x)
                    </div>
                  </div>
                </div>

                <div className="tooltip-section">
                  <div className="tooltip-section-title">🏭 Machine Allocation</div>
                  <MachineGrid 
                    allocation={site.machine_allocation} 
                    limits={site.inventory_limits}
                  />
                </div>

                <div className="tooltip-section">
                  <div className="tooltip-section-title">📊 Geographic Efficiency</div>
                  <div className="efficiency-bars">
                    <EfficiencyMeter 
                      label="Water" 
                      value={site.water_availability} 
                    />
                    <EfficiencyMeter 
                      label="Climate" 
                      value={site.climate_factor} 
                    />
                    <EfficiencyMeter 
                      label="Infrastructure" 
                      value={site.infrastructure} 
                    />
                  </div>
                </div>
              </div>
            </Popup>
          );
        })()}

        {/* Hover Tooltip */}
        {hoverInfo && hoverInfo.site && (
          <Popup
            longitude={hoverInfo.site.coordinates.lng}
            latitude={hoverInfo.site.coordinates.lat}
            anchor="bottom"
            closeButton={false}
            closeOnClick={false}
            focusAfterOpen={false}
            offset={[0, -10]}
          >
            <div className="tooltip">
              <div className="tooltip-header">{hoverInfo.site.name}</div>
              <div className="tooltip-location">{hoverInfo.site.location}</div>
              
              <div className="tooltip-section">
                <div className="profit-info">
                  <div className="profit-main">
                    {formatCurrency(hoverInfo.site.optimization.net_profit)}
                  </div>
                  <div className="profit-details">
                    Power: {formatNumber(hoverInfo.site.optimization.power_used)}/1,000,000
                  </div>
                </div>
              </div>

              <div className="tooltip-section">
                <div className="electricity-info">
                  <div className="electricity-cost">
                    ${hoverInfo.site.electricity_cost_per_mwh}/MWh
                  </div>
                </div>
              </div>

              <div className="tooltip-section">
                <div className="tooltip-section-title">🏭 Active Machines</div>
                <div style={{ fontSize: '12px', color: '#ccc' }}>
                  {Object.entries(hoverInfo.site.machine_allocation)
                    .filter(([_, count]) => count > 0)
                    .map(([type, count]) => (
                      <div key={type}>
                        {type.replace('_', ' ')}: {count}
                      </div>
                    ))
                  }
                  {Object.values(hoverInfo.site.machine_allocation).every(count => count === 0) && (
                    <div style={{ color: '#666' }}>No machines deployed</div>
                  )}
                </div>
              </div>
            </div>
          </Popup>
        )}
      </Map>

      {/* Legend */}
      <div className="legend">
        <div className="legend-title">Profitability</div>
        <div className="legend-item">
          <div className="legend-color profit-high"></div>
          High (&gt;$1.5M)
        </div>
        <div className="legend-item">
          <div className="legend-color profit-medium"></div>
          Medium ($500K-$1.5M)
        </div>
        <div className="legend-item">
          <div className="legend-color profit-low"></div>
          Low (&lt;$500K)
        </div>
        <div className="legend-item">
          <div className="legend-color profit-zero"></div>
          Unprofitable
        </div>
      </div>
    </div>
  );
};

export default MapComponent; 