import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';

const DisasterSimulator = ({ siteData, onSiteDataUpdate }) => {
  const [messages, setMessages] = useState([
    {
      type: 'system',
      content: 'Natural Disaster Simulation System Online',
      timestamp: Date.now()
    },
    {
      type: 'assistant',
      content: 'I can simulate natural disasters and their effects on your mining operations. Try asking me to simulate events like "heat wave in Texas" or "drought in Idaho".',
      timestamp: Date.now()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSimulating, setIsSimulating] = useState(false);
  const [originalData, setOriginalData] = useState(null);
  const messagesEndRef = useRef(null);
  const chatContainerRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Disaster effect definitions
  const disasterEffects = {
    'heat_wave': {
      name: 'Heat Wave',
      description: 'Extreme temperatures causing thermal throttling and grid curtailment',
      effects: {
        power_reduction: 0.3,
        efficiency_reduction: 0.25,
        affected_machines: ['air_miners', 'gpu_compute'],
        electricity_multiplier: 1.4
      }
    },
    'cold_snap': {
      name: 'Cold Snap',
      description: 'Severe cold improving cooling but risking grid instability',
      effects: {
        power_reduction: 0.15,
        efficiency_boost: 0.1,
        affected_machines: ['air_miners'],
        electricity_multiplier: 1.2
      }
    },
    'drought': {
      name: 'Drought',
      description: 'Water shortage severely impacting hydro-cooled operations',
      effects: {
        power_reduction: 0.6,
        efficiency_reduction: 0.4,
        affected_machines: ['hydro_miners', 'immersion_miners'],
        electricity_multiplier: 1.1
      }
    },
    'heavy_rainfall': {
      name: 'Heavy Rainfall',
      description: 'Abundant water boosting hydro capacity and cooling efficiency',
      effects: {
        power_boost: 0.2,
        efficiency_boost: 0.15,
        affected_machines: ['hydro_miners', 'immersion_miners'],
        electricity_multiplier: 0.9
      }
    },
    'wildfire': {
      name: 'Wildfire',
      description: 'Smoke and grid instability forcing emergency shutdowns',
      effects: {
        power_reduction: 0.8,
        efficiency_reduction: 0.6,
        affected_machines: ['air_miners', 'hydro_miners', 'gpu_compute'],
        electricity_multiplier: 1.6
      }
    },
    'flooding': {
      name: 'Flooding',
      description: 'Physical infrastructure damage and power outages',
      effects: {
        power_reduction: 0.9,
        efficiency_reduction: 0.8,
        affected_machines: ['all'],
        electricity_multiplier: 2.0
      }
    },
    'tornado': {
      name: 'Tornado',
      description: 'Catastrophic infrastructure damage requiring emergency shutdown',
      effects: {
        power_reduction: 1.0,
        efficiency_reduction: 1.0,
        affected_machines: ['all'],
        electricity_multiplier: 3.0
      }
    },
    'blizzard': {
      name: 'Blizzard',
      description: 'Power line failures despite improved cooling conditions',
      effects: {
        power_reduction: 0.4,
        efficiency_reduction: 0.2,
        affected_machines: ['air_miners', 'gpu_compute'],
        electricity_multiplier: 1.3
      }
    }
  };

  // Location-specific disaster susceptibility
  const locationRisks = {
    'RockdaleTX': ['heat_wave', 'tornado', 'flooding'],
    'CheyenneWY': ['cold_snap', 'blizzard', 'wildfire'],
    'ButteMT': ['wildfire', 'cold_snap', 'drought'],
    'MassaNY': ['cold_snap', 'blizzard', 'flooding'],
    'AtlantaGA': ['heat_wave', 'tornado', 'flooding'],
    'NashvilleTN': ['tornado', 'flooding', 'heat_wave'],
    'OklahomaCityOK': ['tornado', 'heat_wave', 'drought'],
    'BoiseID': ['wildfire', 'drought', 'heavy_rainfall'],
    'KearnyNE': ['tornado', 'blizzard', 'drought'],
    'ColumbusOH': ['cold_snap', 'tornado', 'flooding']
  };

  const detectDisasterFromMessage = (message) => {
    const lowercaseMessage = message.toLowerCase();
    
    // Detect disaster type
    let disasterType = null;
    if (lowercaseMessage.includes('heat') || lowercaseMessage.includes('hot') || lowercaseMessage.includes('temperature')) {
      disasterType = 'heat_wave';
    } else if (lowercaseMessage.includes('cold') || lowercaseMessage.includes('freeze') || lowercaseMessage.includes('frost')) {
      disasterType = 'cold_snap';
    } else if (lowercaseMessage.includes('drought') || lowercaseMessage.includes('dry')) {
      disasterType = 'drought';
    } else if (lowercaseMessage.includes('rain') || lowercaseMessage.includes('flood') && !lowercaseMessage.includes('wildfire')) {
      disasterType = lowercaseMessage.includes('flood') ? 'flooding' : 'heavy_rainfall';
    } else if (lowercaseMessage.includes('fire') || lowercaseMessage.includes('wildfire')) {
      disasterType = 'wildfire';
    } else if (lowercaseMessage.includes('tornado') || lowercaseMessage.includes('twister')) {
      disasterType = 'tornado';
    } else if (lowercaseMessage.includes('blizzard') || lowercaseMessage.includes('snow')) {
      disasterType = 'blizzard';
    }

    // Detect affected locations
    const affectedLocations = [];
    Object.keys(locationRisks).forEach(siteId => {
      const site = siteData.sites.find(s => s.id === siteId);
      if (site) {
        const locationName = site.location.toLowerCase();
        const stateName = site.location.split(', ')[1]?.toLowerCase();
        if (lowercaseMessage.includes(locationName) || 
            lowercaseMessage.includes(stateName) ||
            lowercaseMessage.includes(site.name.toLowerCase())) {
          affectedLocations.push(siteId);
        }
      }
    });

    // If no specific location mentioned, find susceptible locations
    if (affectedLocations.length === 0 && disasterType) {
      Object.entries(locationRisks).forEach(([siteId, risks]) => {
        if (risks.includes(disasterType)) {
          affectedLocations.push(siteId);
        }
      });
    }

    return { disasterType, affectedLocations };
  };

  const simulateDisaster = async (disasterType, affectedLocations) => {
    if (!originalData) {
      setOriginalData(JSON.parse(JSON.stringify(siteData)));
    }

    const disaster = disasterEffects[disasterType];
    const updatedSiteData = JSON.parse(JSON.stringify(siteData));

    let totalImpactedProfit = 0;
    let impactedSites = [];

    affectedLocations.forEach(siteId => {
      const siteIndex = updatedSiteData.sites.findIndex(s => s.id === siteId);
      if (siteIndex !== -1) {
        const site = updatedSiteData.sites[siteIndex];
        const originalProfit = site.optimization.net_profit;

        // Apply disaster effects
        if (disaster.effects.power_reduction) {
          const reductionFactor = 1 - disaster.effects.power_reduction;
          site.optimization.net_profit *= reductionFactor;
          site.optimization.total_revenue *= reductionFactor;
          site.optimization.power_used *= reductionFactor;
        }

        if (disaster.effects.power_boost) {
          const boostFactor = 1 + disaster.effects.power_boost;
          site.optimization.net_profit *= boostFactor;
          site.optimization.total_revenue *= boostFactor;
          site.optimization.power_used = Math.min(site.optimization.power_used * boostFactor, 1000000);
        }

        // Adjust machine allocations
        if (disaster.effects.affected_machines.includes('all')) {
          Object.keys(site.machine_allocation).forEach(machineType => {
            site.machine_allocation[machineType] = 0;
          });
        } else {
          disaster.effects.affected_machines.forEach(machineType => {
            if (site.machine_allocation[machineType]) {
              const reductionFactor = disaster.effects.power_reduction || (1 - disaster.effects.power_boost || 0);
              site.machine_allocation[machineType] = Math.floor(
                site.machine_allocation[machineType] * (1 - reductionFactor)
              );
            }
          });
        }

        // Adjust electricity costs
        site.electricity_cost_per_mwh *= disaster.effects.electricity_multiplier;
        site.electricity_multiplier *= disaster.effects.electricity_multiplier;

        const impactAmount = originalProfit - site.optimization.net_profit;
        totalImpactedProfit += impactAmount;
        impactedSites.push({
          name: site.name,
          location: site.location,
          originalProfit,
          newProfit: site.optimization.net_profit,
          impact: impactAmount
        });
      }
    });

    // Recalculate total profit
    updatedSiteData.total_profit = updatedSiteData.sites.reduce(
      (sum, site) => sum + site.optimization.net_profit, 0
    );

    onSiteDataUpdate(updatedSiteData);
    setIsSimulating(true);

    return { totalImpactedProfit, impactedSites, disaster };
  };

  const restoreNormalOperations = () => {
    if (originalData) {
      onSiteDataUpdate(originalData);
      setOriginalData(null);
      setIsSimulating(false);
      
      setMessages(prev => [...prev, {
        type: 'system',
        content: 'Operations restored to normal baseline conditions.',
        timestamp: Date.now()
      }]);
    }
  };

  const callOpenRouterAPI = async (userMessage, simulationContext = null) => {
    const apiKey = process.env.REACT_APP_OPENROUTER_API_KEY;
    
    const systemPrompt = `You are a sophisticated natural disaster simulation system for mining operations. You analyze the effects of various natural disasters on mining facilities across different US locations.

Available disaster types:
- Heat waves: Reduce efficiency, cause thermal throttling
- Cold snaps: Can improve cooling but risk grid instability  
- Droughts: Severely impact hydro-cooled operations
- Heavy rainfall: Boost hydro capacity
- Wildfires: Force emergency shutdowns
- Flooding: Cause physical infrastructure damage
- Tornadoes: Catastrophic damage requiring shutdowns
- Blizzards: Power line failures despite cooling benefits

Respond professionally and mention analyzing historic weather patterns when simulating events.

${simulationContext ? `Current simulation: ${JSON.stringify(simulationContext)}` : ''}`;

    try {
      const response = await axios.post(
        'https://openrouter.ai/api/v1/chat/completions',
        {
          model: 'anthropic/claude-3.5-sonnet',
          messages: [
            { role: 'system', content: systemPrompt },
            { role: 'user', content: userMessage }
          ],
          max_tokens: 300,
          temperature: 0.7
        },
        {
          headers: {
            'Authorization': `Bearer ${apiKey}`,
            'Content-Type': 'application/json'
          }
        }
      );

      return response.data.choices[0].message.content;
    } catch (error) {
      console.error('OpenRouter API Error:', error);
      return "I'm experiencing connection issues with the analysis system. Please try again in a moment.";
    }
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = inputMessage.trim();
    setInputMessage('');
    setIsLoading(true);

    // Add user message
    setMessages(prev => [...prev, {
      type: 'user',
      content: userMessage,
      timestamp: Date.now()
    }]);

    // Check for restore command
    if (userMessage.toLowerCase().includes('restore') || 
        userMessage.toLowerCase().includes('normal') ||
        userMessage.toLowerCase().includes('reset')) {
      restoreNormalOperations();
      setIsLoading(false);
      return;
    }

    // Detect disaster simulation request
    const { disasterType, affectedLocations } = detectDisasterFromMessage(userMessage);

    try {
      let simulationResults = null;
      
      if (disasterType && affectedLocations.length > 0) {
        // Add simulation status message
        setMessages(prev => [...prev, {
          type: 'system',
          content: `Pulling historic weather data for ${disasterEffects[disasterType].name} events...`,
          timestamp: Date.now()
        }]);

        // Simulate the disaster
        simulationResults = await simulateDisaster(disasterType, affectedLocations);
      }

      // Get AI response
      const aiResponse = await callOpenRouterAPI(userMessage, simulationResults);

      // Add AI response
      setMessages(prev => [...prev, {
        type: 'assistant',
        content: aiResponse,
        timestamp: Date.now()
      }]);

      // Add simulation results if applicable
      if (simulationResults) {
        const { totalImpactedProfit, impactedSites, disaster } = simulationResults;
        
        const impactSummary = `Simulation Results:
Event: ${disaster.name}
Total Profit Impact: $${Math.abs(totalImpactedProfit).toLocaleString()}
Sites Affected: ${impactedSites.length}

Most Affected Sites:
${impactedSites
  .sort((a, b) => Math.abs(b.impact) - Math.abs(a.impact))
  .slice(0, 3)
  .map(site => `${site.name}: $${Math.abs(site.impact).toLocaleString()} impact`)
  .join('\n')}

Type "restore normal operations" to return to baseline.`;

        setMessages(prev => [...prev, {
          type: 'simulation',
          content: impactSummary,
          timestamp: Date.now()
        }]);
      }

    } catch (error) {
      setMessages(prev => [...prev, {
        type: 'error',
        content: 'Simulation system encountered an error. Please try again.',
        timestamp: Date.now()
      }]);
    }

    setIsLoading(false);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="disaster-simulator">
      <div className="simulator-header">
        <div className="simulator-title">Disaster Simulation</div>
        <div className="simulator-status">
          {isSimulating ? (
            <div className="status-active">
              <div className="status-dot active"></div>
              <span>Simulation Active</span>
            </div>
          ) : (
            <div className="status-normal">
              <div className="status-dot normal"></div>
              <span>Normal Operations</span>
            </div>
          )}
        </div>
      </div>

      <div className="chat-container" ref={chatContainerRef}>
        <div className="messages">
          {messages.map((message, index) => (
            <div key={index} className={`message ${message.type}`}>
              <div className="message-content">
                {message.content}
              </div>
              <div className="message-time">
                {new Date(message.timestamp).toLocaleTimeString()}
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="message assistant loading">
              <div className="message-content">
                <div className="loading-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      <div className="chat-input-container">
        <textarea
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask me to simulate disasters like 'heat wave in Texas' or 'drought in Idaho'..."
          rows={2}
          disabled={isLoading}
          className="chat-input"
        />
        <button 
          onClick={handleSendMessage} 
          disabled={isLoading || !inputMessage.trim()}
          className="send-button"
        >
          {isLoading ? '...' : 'Send'}
        </button>
      </div>

      {isSimulating && (
        <div className="restore-panel">
          <button onClick={restoreNormalOperations} className="restore-button">
            Restore Normal Operations
          </button>
        </div>
      )}
    </div>
  );
};

export default DisasterSimulator; 