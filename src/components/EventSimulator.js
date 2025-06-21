import React, { useState, useCallback } from 'react';

const EventSimulator = ({ siteData, onDataUpdate }) => {
  const [isSimulating, setIsSimulating] = useState(false);
  const [activeEvent, setActiveEvent] = useState(null);
  const [eventResults, setEventResults] = useState(null);
  const [originalData, setOriginalData] = useState(null);

  const eventTypes = [
    {
      id: 'heatwave',
      name: 'Heat Wave',
      description: 'Extreme temperatures causing thermal throttling and grid curtailment',
      impact: 'Severe',
      color: '#ef4444'
    },
    {
      id: 'coldsnap',
      name: 'Cold Snap',
      description: 'Extreme cold improving cooling efficiency but risking grid instability',
      impact: 'Moderate',
      color: '#3b82f6'
    },
    {
      id: 'drought',
      name: 'Drought',
      description: 'Water scarcity reducing hydro mining capacity',
      impact: 'High',
      color: '#f59e0b'
    },
    {
      id: 'flooding',
      name: 'Heavy Rainfall',
      description: 'Increased water availability boosting hydro operations',
      impact: 'Positive',
      color: '#10b981'
    },
    {
      id: 'wildfire',
      name: 'Wildfire',
      description: 'Fire risk causing forced shutdowns and grid instability',
      impact: 'Severe',
      color: '#dc2626'
    },
    {
      id: 'tornado',
      name: 'Tornado',
      description: 'Severe weather causing infrastructure damage',
      impact: 'Severe',
      color: '#7c3aed'
    },
    {
      id: 'blizzard',
      name: 'Blizzard',
      description: 'Heavy snow and ice causing power line failures',
      impact: 'High',
      color: '#6b7280'
    }
  ];

  const getRegionalVulnerability = (siteId, eventType) => {
    const vulnerabilities = {
      'RockdaleTX': {
        heatwave: 0.9, coldsnap: 0.2, drought: 0.7, flooding: 0.4, wildfire: 0.6, tornado: 0.8, blizzard: 0.1
      },
      'CheyenneWY': {
        heatwave: 0.3, coldsnap: 0.8, drought: 0.9, flooding: 0.2, wildfire: 0.7, tornado: 0.4, blizzard: 0.9
      },
      'ButteMT': {
        heatwave: 0.4, coldsnap: 0.7, drought: 0.6, flooding: 0.3, wildfire: 0.8, tornado: 0.2, blizzard: 0.8
      },
      'MassenaDE': {
        heatwave: 0.5, coldsnap: 0.6, drought: 0.3, flooding: 0.6, wildfire: 0.3, tornado: 0.3, blizzard: 0.7
      },
      'AtlantaGA': {
        heatwave: 0.8, coldsnap: 0.3, drought: 0.5, flooding: 0.7, wildfire: 0.4, tornado: 0.7, blizzard: 0.2
      },
      'MemphisTN': {
        heatwave: 0.7, coldsnap: 0.4, drought: 0.4, flooding: 0.5, wildfire: 0.3, tornado: 0.8, blizzard: 0.3
      },
      'TulsaOK': {
        heatwave: 0.8, coldsnap: 0.5, drought: 0.6, flooding: 0.4, wildfire: 0.5, tornado: 0.9, blizzard: 0.4
      },
      'KearneNE': {
        heatwave: 0.6, coldsnap: 0.7, drought: 0.7, flooding: 0.3, wildfire: 0.4, tornado: 0.7, blizzard: 0.6
      },
      'ColumbusOH': {
        heatwave: 0.6, coldsnap: 0.6, drought: 0.4, flooding: 0.4, wildfire: 0.2, tornado: 0.5, blizzard: 0.7
      },
      'BoiseID': {
        heatwave: 0.5, coldsnap: 0.6, drought: 0.5, flooding: 0.4, wildfire: 0.8, tornado: 0.1, blizzard: 0.6
      }
    };
    
    return vulnerabilities[siteId]?.[eventType] || 0.5;
  };

  const simulateEvent = useCallback(async (eventType) => {
    setIsSimulating(true);
    setActiveEvent(eventType);
    
    // Store original data for restoration
    if (!originalData) {
      setOriginalData(JSON.parse(JSON.stringify(siteData)));
    }

    try {
      // Simulate AI analysis
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Calculate event impacts
      const impactedSites = siteData.sites.map(site => {
        const vulnerability = getRegionalVulnerability(site.id, eventType.id);
        const impactMultiplier = calculateImpactMultiplier(eventType.id, vulnerability);
        
        return {
          ...site,
          optimization: {
            ...site.optimization,
            net_profit: Math.max(0, site.optimization.net_profit * impactMultiplier),
            total_revenue: site.optimization.total_revenue * impactMultiplier,
            efficiency: Math.max(0.1, site.optimization.efficiency * impactMultiplier)
          },
          machine_allocation: adjustMachineAllocation(site.machine_allocation, eventType.id, vulnerability),
          event_impact: {
            type: eventType.name,
            severity: vulnerability,
            multiplier: impactMultiplier
          }
        };
      });

      const newSiteData = {
        ...siteData,
        sites: impactedSites,
        total_profit: impactedSites.reduce((sum, site) => sum + site.optimization.net_profit, 0),
        event_active: true,
        event_type: eventType.name
      };

      const results = {
        eventType: eventType.name,
        totalImpact: ((newSiteData.total_profit - siteData.total_profit) / siteData.total_profit * 100).toFixed(1),
        affectedSites: impactedSites.filter(site => site.event_impact.severity > 0.3).length,
        severityMap: impactedSites.reduce((acc, site) => {
          acc[site.id] = site.event_impact.severity;
          return acc;
        }, {})
      };

      setEventResults(results);
      onDataUpdate(newSiteData);
      
    } catch (error) {
      console.error('Event simulation failed:', error);
    } finally {
      setIsSimulating(false);
    }
  }, [siteData, originalData, onDataUpdate]);

  const calculateImpactMultiplier = (eventType, vulnerability) => {
    const baseImpacts = {
      heatwave: 0.3,    // 70% reduction
      coldsnap: 0.85,   // 15% reduction (some benefit from cooling)
      drought: 0.4,     // 60% reduction
      flooding: 1.2,    // 20% increase
      wildfire: 0.1,    // 90% reduction
      tornado: 0.05,    // 95% reduction
      blizzard: 0.2     // 80% reduction
    };
    
    const baseImpact = baseImpacts[eventType] || 0.7;
    return Math.max(0.05, Math.min(1.5, baseImpact + (1 - vulnerability) * 0.3));
  };

  const adjustMachineAllocation = (allocation, eventType, vulnerability) => {
    const adjustments = {
      heatwave: { air_miners: 0.3, hydro_miners: 0.8, immersion_miners: 0.9 },
      coldsnap: { air_miners: 1.2, hydro_miners: 0.7, immersion_miners: 0.8 },
      drought: { hydro_miners: 0.2, immersion_miners: 0.4 },
      flooding: { hydro_miners: 1.3, immersion_miners: 1.2 },
      wildfire: { air_miners: 0.1, hydro_miners: 0.1, immersion_miners: 0.1 },
      tornado: { air_miners: 0.05, hydro_miners: 0.05, immersion_miners: 0.05 },
      blizzard: { air_miners: 0.3, hydro_miners: 0.4, immersion_miners: 0.5 }
    };

    const eventAdjustments = adjustments[eventType] || {};
    const adjusted = { ...allocation };

    Object.keys(eventAdjustments).forEach(machineType => {
      if (adjusted[machineType] !== undefined) {
        adjusted[machineType] = Math.floor(adjusted[machineType] * eventAdjustments[machineType] * (1 - vulnerability * 0.5));
      }
    });

    return adjusted;
  };

  const restoreNormalConditions = useCallback(() => {
    if (originalData) {
      onDataUpdate(originalData);
      setActiveEvent(null);
      setEventResults(null);
      setOriginalData(null);
    }
  }, [originalData, onDataUpdate]);

  return (
    <div className="event-simulator">
      <div className="simulator-header">
        <h3 className="simulator-title">Natural Event Simulation</h3>
        <p className="simulator-subtitle">AI-powered disaster impact modeling</p>
      </div>

      {activeEvent && (
        <div className="active-event-banner">
          <div className="event-status">
            <div className="status-indicator active"></div>
            <span>Active Event: {activeEvent.name}</span>
          </div>
          <button 
            className="restore-button" 
            onClick={restoreNormalConditions}
            disabled={isSimulating}
          >
            Restore Normal
          </button>
        </div>
      )}

      {eventResults && (
        <div className="event-results">
          <div className="results-header">Impact Analysis</div>
          <div className="results-grid">
            <div className="result-item">
              <div className="result-label">Total Impact</div>
              <div className={`result-value ${parseFloat(eventResults.totalImpact) >= 0 ? 'positive' : 'negative'}`}>
                {eventResults.totalImpact}%
              </div>
            </div>
            <div className="result-item">
              <div className="result-label">Affected Sites</div>
              <div className="result-value">{eventResults.affectedSites}/10</div>
            </div>
          </div>
        </div>
      )}

      <div className="event-types">
        <div className="section-label">Select Event Type</div>
        <div className="event-grid">
          {eventTypes.map(event => (
            <button
              key={event.id}
              className={`event-card ${activeEvent?.id === event.id ? 'active' : ''}`}
              onClick={() => simulateEvent(event)}
              disabled={isSimulating}
            >
              <div className="event-header">
                <div className="event-name">{event.name}</div>
                <div 
                  className="event-impact"
                  style={{ color: event.color }}
                >
                  {event.impact}
                </div>
              </div>
              <div className="event-description">{event.description}</div>
            </button>
          ))}
        </div>
      </div>

      {isSimulating && (
        <div className="simulation-status">
          <div className="loading-indicator"></div>
          <div className="loading-text">
            <div>Pulling historic weather data...</div>
            <div>Analyzing regional vulnerabilities...</div>
            <div>Computing infrastructure impacts...</div>
          </div>
        </div>
      )}
    </div>
  );
};

export default EventSimulator; 