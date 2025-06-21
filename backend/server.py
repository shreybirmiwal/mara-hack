from flask import Flask, jsonify, request
from flask_cors import CORS
from gridstatusio import GridStatusClient
import pandas as pd
from datetime import datetime, timedelta
import logging
import time
from openai import OpenAI
import json
import random
import re

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize GridStatus client
import os
from dotenv import load_dotenv

load_dotenv()
GRIDSTATUS_API_KEY = os.getenv('GRIDSTATUS_API_KEY')
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')

if not GRIDSTATUS_API_KEY:
    logger.warning("GRIDSTATUS_API_KEY not found in environment variables. Using mock data.")
    client = None
else:
    client = GridStatusClient(GRIDSTATUS_API_KEY)

# Initialize OpenRouter client
if not OPENROUTER_API_KEY:
    logger.warning("OPENROUTER_API_KEY not found in environment variables. AI scenarios will not work.")
    ai_client = None
else:
    ai_client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
    )

# Price history storage (in production, this would be a database)
_price_history = {
    'data': [],  # List of {timestamp, location_data, scenario_name}
    'max_history': 50,  # Keep last 50 data points
    'base_prices': {},  # Store original base prices for proper comparison
    'current_scenario_data': None  # Store the most recent scenario-affected data
}

# Static base prices for each location type (not fetched from API)
BASE_PRICES = {
    'Solar': 25.0,
    'Wind': 30.0,
    'Traditional': 45.0,
    'Battery Storage': 60.0,
    'Peaker': 85.0,
    'Load Center': 40.0,
    'Load Zone': 35.0,
    'Hydro': 20.0,
    'Nuclear': 35.0,
    'Unknown': 40.0
}

# Geographic regions and major cities for scenario location detection
GEOGRAPHIC_REGIONS = {
    'houston': {'lat': 29.7604, 'lng': -95.3698, 'radius_km': 150, 'keywords': ['houston', 'gulf coast', 'southeast texas', 'refineries', 'coast', 'galveston', 'baytown', 'pasadena', 'katy', 'sugar land', 'woodlands']},
    'dallas': {'lat': 32.7767, 'lng': -96.7970, 'radius_km': 120, 'keywords': ['dallas', 'fort worth', 'north texas', 'dfw', 'arlington', 'plano', 'garland', 'irving', 'mesquite', 'richardson', 'carrollton']},
    'san_antonio': {'lat': 29.4241, 'lng': -98.4936, 'radius_km': 100, 'keywords': ['san antonio', 'south texas', 'alamo city', 'bexar county', 'new braunfels', 'seguin', 'schertz']},
    'austin': {'lat': 30.2672, 'lng': -97.7431, 'radius_km': 80, 'keywords': ['austin', 'central texas', 'capital', 'round rock', 'cedar park', 'pflugerville', 'georgetown', 'leander']},
    'lubbock': {'lat': 33.5779, 'lng': -101.8552, 'radius_km': 200, 'keywords': ['lubbock', 'west texas', 'panhandle', 'levelland', 'plainview', 'south plains']},
    'el_paso': {'lat': 31.7619, 'lng': -106.4850, 'radius_km': 150, 'keywords': ['el paso', 'far west texas', 'west texas', 'border', 'las cruces', 'juarez']},
    'corpus_christi': {'lat': 27.8006, 'lng': -97.3964, 'radius_km': 100, 'keywords': ['corpus christi', 'coast', 'coastal texas', 'coastal bend', 'padre island', 'rockport']},
    'amarillo': {'lat': 35.2220, 'lng': -101.8313, 'radius_km': 150, 'keywords': ['amarillo', 'panhandle', 'northern texas', 'canyon', 'borger']},
    'beaumont': {'lat': 30.0860, 'lng': -94.1018, 'radius_km': 80, 'keywords': ['beaumont', 'golden triangle', 'refinery', 'port arthur', 'orange', 'vidor']},
    'midland': {'lat': 31.9974, 'lng': -102.0779, 'radius_km': 120, 'keywords': ['midland', 'permian basin', 'oil country', 'odessa', 'big spring', 'andrews']},
    'brownsville': {'lat': 25.9018, 'lng': -97.4975, 'radius_km': 100, 'keywords': ['brownsville', 'rio grande valley', 'border', 'mcallen', 'harlingen', 'edinburg', 'laredo']},
    'tyler': {'lat': 32.3513, 'lng': -95.3011, 'radius_km': 100, 'keywords': ['tyler', 'east texas', 'longview', 'marshall', 'carthage', 'piney woods']},
    'waco': {'lat': 31.5493, 'lng': -97.1467, 'radius_km': 80, 'keywords': ['waco', 'central texas', 'killeen', 'temple', 'belton']},
    'abilene': {'lat': 32.4487, 'lng': -99.7331, 'radius_km': 100, 'keywords': ['abilene', 'west central texas', 'sweetwater', 'big country']},
    'galveston': {'lat': 29.3013, 'lng': -94.7977, 'radius_km': 50, 'keywords': ['galveston', 'island', 'gulf', 'port', 'hurricane', 'storm surge']},
    'permian_basin': {'lat': 31.8457, 'lng': -102.3676, 'radius_km': 200, 'keywords': ['permian', 'basin', 'oil field', 'fracking', 'drilling', 'petroleum']},
    'panhandle': {'lat': 35.0000, 'lng': -101.5000, 'radius_km': 300, 'keywords': ['panhandle', 'northern plains', 'wind country', 'wheat belt']},
    'east_texas': {'lat': 32.0000, 'lng': -94.5000, 'radius_km': 200, 'keywords': ['east texas', 'piney woods', 'forestry', 'timber', 'nacogdoches']},
    'south_texas': {'lat': 27.5000, 'lng': -98.5000, 'radius_km': 250, 'keywords': ['south texas', 'rio grande', 'valley', 'border region']},
    'central_texas': {'lat': 30.5000, 'lng': -97.5000, 'radius_km': 150, 'keywords': ['central texas', 'hill country', 'heart of texas']},
    'west_texas': {'lat': 31.5000, 'lng': -102.0000, 'radius_km': 300, 'keywords': ['west texas', 'desert', 'big bend', 'trans pecos']}
}

def calculate_distance_km(lat1, lng1, lat2, lng2):
    """Calculate distance between two lat/lng points in kilometers"""
    import math
    
    # Convert to radians
    lat1, lng1, lat2, lng2 = map(math.radians, [lat1, lng1, lat2, lng2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Earth's radius in kilometers
    earth_radius_km = 6371
    return earth_radius_km * c

def find_affected_locations_by_geography(scenario, all_locations):
    """
    Find locations that should be affected based on geographic proximity to mentioned locations
    """
    scenario_lower = scenario.lower()
    affected_locations = []
    matched_regions = []
    
    # Check if any geographic regions are mentioned
    for region_name, region_info in GEOGRAPHIC_REGIONS.items():
        for keyword in region_info['keywords']:
            if keyword in scenario_lower:
                logger.info(f"Geographic match found: '{keyword}' in scenario '{scenario}' -> region '{region_name}'")
                matched_regions.append((region_name, region_info))
                break  # Found a match for this region, no need to check other keywords
    
    # Process all matched regions
    for region_name, region_info in matched_regions:
        region_lat = region_info['lat']
        region_lng = region_info['lng']
        radius_km = region_info['radius_km']
        
        for location in all_locations:
            distance = calculate_distance_km(
                region_lat, region_lng,
                location['lat'], location['lng']
            )
            
            if distance <= radius_km:
                # Check if this location is already added from another region
                existing_location = next((loc for loc in affected_locations if loc['location_code'] == location['location_code']), None)
                if not existing_location:
                    location_copy = location.copy()
                    location_copy['distance_from_impact'] = round(distance, 1)
                    location_copy['impact_region'] = region_name
                    affected_locations.append(location_copy)
                    logger.info(f"Found affected location: {location.get('name', 'Unknown')} at {distance:.1f}km from {region_name}")
                elif distance < existing_location['distance_from_impact']:
                    # Update with closer distance
                    existing_location['distance_from_impact'] = round(distance, 1)
                    existing_location['impact_region'] = region_name
    
    # Sort by distance (closest locations most affected)
    if affected_locations:
        affected_locations.sort(key=lambda x: x['distance_from_impact'])
        logger.info(f"Geographic selection complete: {len(affected_locations)} locations found")
    else:
        logger.info(f"No geographic matches found for scenario: {scenario}")
    
    return affected_locations

# Texas location data for ERCOT nodes (approximate coordinates)
LOCATION_DATA = {
    # Major Cities & Load Centers
    'HB_HOUSTON': {'lat': 29.7604, 'lng': -95.3698, 'name': 'Houston Hub', 'type': 'Load Center', 'capacity_mw': 2500, 'region': 'Southeast Texas'},
    'HB_NORTH': {'lat': 32.7767, 'lng': -96.7970, 'name': 'North Hub (Dallas)', 'type': 'Load Center', 'capacity_mw': 3000, 'region': 'North Texas'},
    'HB_SOUTH': {'lat': 29.4241, 'lng': -98.4936, 'name': 'South Hub (San Antonio)', 'type': 'Load Center', 'capacity_mw': 2000, 'region': 'South Texas'},
    'HB_WEST': {'lat': 31.5804, 'lng': -99.5805, 'name': 'West Hub', 'type': 'Load Center', 'capacity_mw': 1500, 'region': 'West Texas'},
    
    # Solar Installations
    'ZIER_SLR_ALL': {'lat': 32.7867, 'lng': -96.8070, 'name': 'Dallas Solar', 'type': 'Solar', 'capacity_mw': 180, 'region': 'North Texas'},
    'LAMESASLR_G': {'lat': 32.7373, 'lng': -101.9507, 'name': 'Lamesa Solar', 'type': 'Solar', 'capacity_mw': 200, 'region': 'West Texas'},
    'PECOS_SOLAR': {'lat': 31.4226, 'lng': -103.4933, 'name': 'Pecos Solar', 'type': 'Solar', 'capacity_mw': 250, 'region': 'West Texas'},
    'AUSTIN_SOLAR': {'lat': 30.2672, 'lng': -97.7431, 'name': 'Austin Solar', 'type': 'Solar', 'capacity_mw': 150, 'region': 'Central Texas'},
    
    # Wind Farms
    'YNG_WND_ALL': {'lat': 33.5779, 'lng': -101.8552, 'name': 'Lubbock Wind', 'type': 'Wind', 'capacity_mw': 400, 'region': 'West Texas'},
    'WND_WHITNEY': {'lat': 32.7567, 'lng': -97.3614, 'name': 'Fort Worth Wind', 'type': 'Wind', 'capacity_mw': 300, 'region': 'North Texas'},
    'WNDTS2_UNIT1': {'lat': 33.5779, 'lng': -101.8552, 'name': 'West Texas Wind', 'type': 'Wind', 'capacity_mw': 500, 'region': 'West Texas'},
    'QALSW_ALL': {'lat': 32.5007, 'lng': -99.7412, 'name': 'Sweetwater Wind', 'type': 'Wind', 'capacity_mw': 350, 'region': 'West Texas'},
    'GUNMTN_NODE': {'lat': 31.2593, 'lng': -104.5230, 'name': 'Gun Mountain Wind', 'type': 'Wind', 'capacity_mw': 280, 'region': 'West Texas'},
    'PANHNDLE_WND': {'lat': 35.2220, 'lng': -101.8313, 'name': 'Panhandle Wind', 'type': 'Wind', 'capacity_mw': 600, 'region': 'Panhandle'},
    
    # Traditional Power Plants
    'X443ESRN': {'lat': 31.3069, 'lng': -94.7319, 'name': 'East Texas Gas', 'type': 'Traditional', 'capacity_mw': 800, 'region': 'East Texas'},
    'WR_RN': {'lat': 31.5804, 'lng': -99.5805, 'name': 'West Texas Gas', 'type': 'Traditional', 'capacity_mw': 600, 'region': 'West Texas'},
    'WOODWRD2_RN': {'lat': 32.1543, 'lng': -95.8467, 'name': 'Woodward Gas', 'type': 'Traditional', 'capacity_mw': 750, 'region': 'East Texas'},
    'QALSW_CC1': {'lat': 32.5007, 'lng': -99.7412, 'name': 'Sweetwater CC', 'type': 'Traditional', 'capacity_mw': 900, 'region': 'West Texas'},
    'WLTC_ESR_RN': {'lat': 29.7704, 'lng': -95.3798, 'name': 'Houston Gas', 'type': 'Traditional', 'capacity_mw': 1200, 'region': 'Southeast Texas'},
    
    # Battery Storage
    'WRSBES_BESS1': {'lat': 29.7504, 'lng': -95.3598, 'name': 'Houston Battery', 'type': 'Battery Storage', 'capacity_mw': 100, 'region': 'Southeast Texas'},
    'WOV_BESS_RN': {'lat': 30.2672, 'lng': -97.7431, 'name': 'Austin Battery', 'type': 'Battery Storage', 'capacity_mw': 80, 'region': 'Central Texas'},
    'ALP_BESS_RN': {'lat': 30.3572, 'lng': -103.6404, 'name': 'Alpine Battery', 'type': 'Battery Storage', 'capacity_mw': 50, 'region': 'West Texas'},
    'WZRD_ESS_RN': {'lat': 30.2672, 'lng': -97.7431, 'name': 'Central Texas Battery', 'type': 'Battery Storage', 'capacity_mw': 120, 'region': 'Central Texas'},
    
    # Peaker Plants
    'W_PECO_UNIT1': {'lat': 28.8056, 'lng': -96.9778, 'name': 'Victoria Peaker', 'type': 'Peaker', 'capacity_mw': 200, 'region': 'South Texas'},
    'BROWNSVL_PK': {'lat': 25.9018, 'lng': -97.4975, 'name': 'Brownsville Peaker', 'type': 'Peaker', 'capacity_mw': 150, 'region': 'South Texas'},
    
    # Additional Load Zones
    'LCRA_ZONE': {'lat': 30.5085, 'lng': -97.8419, 'name': 'LCRA Zone', 'type': 'Load Zone', 'capacity_mw': 1000, 'region': 'Central Texas'},
    'ERCOT_ZONE1': {'lat': 29.7404, 'lng': -95.3898, 'name': 'Coast Zone', 'type': 'Load Zone', 'capacity_mw': 2000, 'region': 'Southeast Texas'},
    'ERCOT_ZONE2': {'lat': 31.7619, 'lng': -106.4850, 'name': 'Far West Zone', 'type': 'Load Zone', 'capacity_mw': 800, 'region': 'West Texas'},
    'ERCOT_ZONE3': {'lat': 32.7667, 'lng': -96.7870, 'name': 'North Central Zone', 'type': 'Load Zone', 'capacity_mw': 2500, 'region': 'North Texas'},
    'ERCOT_ZONE4': {'lat': 29.4241, 'lng': -98.4936, 'name': 'South Central Zone', 'type': 'Load Zone', 'capacity_mw': 1800, 'region': 'South Texas'}
}

def initialize_base_prices():
    """Initialize base prices for all locations if not already done"""
    if not _price_history['base_prices']:
        for location_code, location_info in LOCATION_DATA.items():
            # Use static base price for location type
            base_price = BASE_PRICES.get(location_info['type'], BASE_PRICES['Unknown'])
            
            # Add small random variation (±5%) for realism, but keep it consistent
            location_seed = hash(location_code)
            random.seed(location_seed)
            variation = random.uniform(-0.05, 0.05)
            final_price = round(base_price * (1 + variation), 2)
            
            _price_history['base_prices'][location_code] = final_price

def add_to_price_history(data, scenario_name=None):
    """Add current data to price history"""
    timestamp = datetime.now().isoformat()
    _price_history['data'].append({
        'timestamp': timestamp,
        'locations': data,
        'scenario': scenario_name or 'base_data'
    })
    
    # Keep only the last max_history entries
    if len(_price_history['data']) > _price_history['max_history']:
        _price_history['data'] = _price_history['data'][-_price_history['max_history']:]

def calculate_unified_price_changes(current_data):
    """
    Unified price change calculation that properly handles:
    1. Base price comparisons
    2. Scenario effects
    3. Consistent trend calculations
    4. Proper percentage math
    """
    # Ensure base prices are initialized
    initialize_base_prices()
    
    # Get the most recent previous data point for trend analysis
    previous_data = None
    if len(_price_history['data']) >= 1:
        previous_data = _price_history['data'][-1]['locations']
        previous_by_code = {item['location_code']: item for item in previous_data}
    
    # Get last 10 data points for price history
    recent_history = _price_history['data'][-10:] if len(_price_history['data']) >= 10 else _price_history['data']
    
    for item in current_data:
        location_code = item['location_code']
        current_price = item['price_mwh']
        base_price = _price_history['base_prices'].get(location_code, current_price)
        
        # Calculate changes from base price (for scenario effects)
        base_change = current_price - base_price
        base_change_percent = (base_change / base_price * 100) if base_price != 0 else 0
        
        # Calculate changes from previous data point (for trends)
        previous_change = 0
        previous_change_percent = 0
        if previous_data and location_code in previous_by_code:
            previous_price = previous_by_code[location_code]['price_mwh']
            previous_change = current_price - previous_price
            previous_change_percent = (previous_change / previous_price * 100) if previous_price != 0 else 0
        
        # Determine which change to display based on scenario status
        if item.get('scenario_affected', False):
            # For scenario-affected locations, show change from base price
            display_change = base_change
            display_change_percent = base_change_percent
        else:
            # For non-affected locations, show change from previous or zero if first time
            display_change = previous_change
            display_change_percent = previous_change_percent
        
        # Determine trend based on the displayed change
        if abs(display_change_percent) < 0.1:  # Less than 0.1% change
            trend = 'stable'
        elif display_change_percent > 0:
            trend = 'rising'
        else:
            trend = 'falling'
        
        # Build price history for this location
        price_history = []
        for hist_point in recent_history:
            location_hist = next((loc for loc in hist_point['locations'] if loc['location_code'] == location_code), None)
            if location_hist:
                price_history.append(location_hist['price_mwh'])
        
        # Add current price if not already there
        if not price_history or price_history[-1] != current_price:
            price_history.append(current_price)
        
        # Limit to last 10 points
        price_history = price_history[-10:]
        
        # Add calculated fields with proper values
        item['price_change'] = round(display_change, 2)
        item['price_change_percent'] = round(display_change_percent, 1)
        item['trend'] = trend
        item['price_history'] = price_history
        item['base_price'] = base_price
        item['base_change'] = round(base_change, 2)
        item['base_change_percent'] = round(base_change_percent, 1)
        
        # Add capacity_mw and region for frontend compatibility
        location_info = LOCATION_DATA.get(location_code, {})
        item['capacity_mw'] = location_info.get('capacity_mw', 100)
        item['region'] = location_info.get('region', 'West Texas')
    
    return current_data

def get_static_base_data():
    """Get static base data without fetching from API"""
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    processed_data = []
    for location_code, location_info in LOCATION_DATA.items():
        # Use static base price for location type
        base_price = BASE_PRICES.get(location_info['type'], BASE_PRICES['Unknown'])
        
        # Add small random variation (±5%) for realism, but keep it consistent
        location_seed = hash(location_code)
        random.seed(location_seed)
        variation = random.uniform(-0.05, 0.05)
        final_price = round(base_price * (1 + variation), 2)
        
        processed_data.append({
            'location_code': location_code,
            'name': location_info['name'],
            'lat': location_info['lat'],
            'lng': location_info['lng'],
            'type': location_info['type'],
            'capacity_mw': location_info.get('capacity_mw', 100),
            'region': location_info.get('region', 'West Texas'),
            'price_mwh': final_price,
            'timestamp': current_time,
            'price_category': 'high' if final_price > 50 else 'medium' if final_price > 25 else 'low'
        })
    
    # Sort by price for better visualization
    processed_data.sort(key=lambda x: x['price_mwh'], reverse=True)
    
    return processed_data

def fetch_fresh_data():
    """Get current data - either scenario-affected data or base data"""
    try:
        logger.info("Fetching current energy data")
        
        # Initialize base prices if not done
        initialize_base_prices()
        
        # If we have current scenario data, return that instead of base data
        if _price_history['current_scenario_data'] is not None:
            logger.info("Returning current scenario-affected data")
            # Apply fresh unified calculations to ensure consistency
            scenario_data = _price_history['current_scenario_data'].copy()
            processed_data = calculate_unified_price_changes(scenario_data)
            return processed_data
        
        # Otherwise return base data
        logger.info("Returning base data (no active scenario)")
        processed_data = get_static_base_data()
        processed_data = calculate_unified_price_changes(processed_data)
        
        logger.info(f"Loaded {len(processed_data)} locations")
        return processed_data
        
    except Exception as e:
        logger.error(f"Error getting fresh data: {str(e)}")
        return []

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'OK', 'message': 'Backend is running'})

@app.route('/api/hello', methods=['GET'])
def hello():
    return jsonify({'message': 'Hello from MARA Energy Backend!'})

@app.route('/api/energy-data', methods=['GET'])
def get_energy_data():
    """Fetch real-time energy pricing data from ERCOT (no caching)"""
    try:
        processed_data = fetch_fresh_data()
        
        return jsonify({
            'success': True,
            'data': processed_data,
            'total_locations': len(processed_data),
            'timestamp': datetime.now().isoformat(),
            'price_range': {
                'min': min([d['price_mwh'] for d in processed_data]) if processed_data else 0,
                'max': max([d['price_mwh'] for d in processed_data]) if processed_data else 0,
                'avg': round(sum([d['price_mwh'] for d in processed_data]) / len(processed_data), 2) if processed_data else 0
            }
        })
        
    except Exception as e:
        logger.error(f"Error in get_energy_data: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to get energy data'
        }), 500

@app.route('/api/energy-stats', methods=['GET'])
def get_energy_stats():
    """Get summary statistics for energy data (no caching)"""
    try:
        processed_data = fetch_fresh_data()
        
        if processed_data:
            prices = [d['price_mwh'] for d in processed_data]
            stats = {
                'total_records': len(processed_data),
                'locations_count': len(processed_data),
                'avg_price': round(sum(prices) / len(prices), 2),
                'max_price': round(max(prices), 2),
                'min_price': round(min(prices), 2),
                'data_timestamp': datetime.now().isoformat()
            }
        else:
            stats = {
                'total_records': 0,
                'locations_count': 0,
                'avg_price': 0,
                'max_price': 0,
                'min_price': 0,
                'data_timestamp': datetime.now().isoformat()
            }
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Error getting energy stats: {str(e)}")
        return jsonify({
            'error': str(e),
            'message': 'Failed to get energy statistics'
        }), 500

def apply_scenario_effects(scenario, current_data):
    """
    Apply realistic scenario effects to the energy data with proper price tracking
    """
    import re
    
    # Ensure base prices are initialized
    initialize_base_prices()
    
    # Make a deep copy of the data to modify
    modified_data = [item.copy() for item in current_data]
    effects_applied = []
    
    scenario_lower = scenario.lower()
    
    # Define scenario patterns and their effects
    scenario_effects = {
        # Weather events
        'hailstorm|hail': {
            'affects': ['Solar'],
            'price_multiplier': lambda: random.uniform(2.5, 4.0),
            'effect_desc': 'Solar panels damaged, massive price spikes'
        },
        'hurricane|storm|flooding': {
            'affects': ['Traditional', 'Load Center', 'Load Zone'],
            'price_multiplier': lambda: random.uniform(3.0, 5.0),
            'effect_desc': 'Major infrastructure disrupted, emergency pricing'
        },
        'tornado|twister': {
            'affects': ['Wind', 'Traditional'],
            'price_multiplier': lambda: random.uniform(2.0, 3.5),
            'effect_desc': 'Wind turbines and power plants damaged'
        },
        'ice storm|freeze|winter': {
            'affects': ['Traditional', 'Wind'],
            'price_multiplier': lambda: random.uniform(4.0, 6.0),
            'effect_desc': 'Power plants frozen, turbines iced over'
        },
        'heat wave|extreme heat': {
            'affects': ['Traditional', 'Load Center'],
            'price_multiplier': lambda: random.uniform(1.5, 2.5),
            'effect_desc': 'AC demand surges, thermal plants stressed'
        },
        'drought': {
            'affects': ['Traditional'],
            'price_multiplier': lambda: random.uniform(1.8, 2.8),
            'effect_desc': 'Cooling water shortage for power plants'
        },
        'wildfire|fire': {
            'affects': ['Solar', 'Wind', 'Traditional'],
            'price_multiplier': lambda: random.uniform(2.2, 3.8),
            'effect_desc': 'Transmission lines down, plants evacuated'
        },
        
        # Grid/Infrastructure issues  
        'cyberattack|cyber|hack': {
            'affects': ['Load Center', 'Traditional'],
            'price_multiplier': lambda: random.uniform(3.5, 5.5),
            'effect_desc': 'Grid control systems compromised'
        },
        'transformer|substation|transmission': {
            'affects': ['Load Zone', 'Load Center'],
            'price_multiplier': lambda: random.uniform(2.8, 4.2),
            'effect_desc': 'Critical transmission infrastructure failed'
        },
        'blackout|outage|grid failure': {
            'affects': ['Load Center', 'Traditional'],
            'price_multiplier': lambda: random.uniform(4.0, 7.0),
            'effect_desc': 'Cascading grid failures, emergency response'
        },
        
        # Economic/Market events
        'gas shortage|natural gas': {
            'affects': ['Traditional', 'Peaker'],
            'price_multiplier': lambda: random.uniform(3.0, 5.0),
            'effect_desc': 'Natural gas supply disrupted, backup power activated'
        },
        'oil spill|pipeline': {
            'affects': ['Traditional'],
            'price_multiplier': lambda: random.uniform(1.8, 2.5),
            'effect_desc': 'Energy transport disrupted'
        },
        
        # Positive scenarios (reduce prices)
        'perfect weather|ideal conditions': {
            'affects': ['Wind', 'Solar'],
            'price_multiplier': lambda: random.uniform(0.2, 0.6),
            'effect_desc': 'Optimal renewable generation, prices plummet'
        },
        'new solar|solar expansion': {
            'affects': ['Solar', 'Load Center'],
            'price_multiplier': lambda: random.uniform(0.3, 0.7),
            'effect_desc': 'Massive solar capacity online, surplus power'
        },
        'wind boom|high wind': {
            'affects': ['Wind'],
            'price_multiplier': lambda: random.uniform(0.1, 0.4),
            'effect_desc': 'Record wind generation flooding market'
        },
        
        # Weird/Fun scenarios
        'alien|ufo|extraterrestrial': {
            'affects': ['Load Center', 'Traditional'],
            'price_multiplier': lambda: random.uniform(5.0, 10.0),
            'effect_desc': 'Mysterious energy drain across major cities'
        },
        'zombie|apocalypse': {
            'affects': ['Load Center', 'Traditional'],
            'price_multiplier': lambda: random.uniform(0.1, 0.3),
            'effect_desc': 'Demand collapsed, only essential systems running'
        },
        'bitcoin|crypto|mining': {
            'affects': ['Load Center', 'Traditional'],
            'price_multiplier': lambda: random.uniform(2.0, 3.5),
            'effect_desc': 'Massive crypto mining operations demand surge'
        },
        'tesla|electric car': {
            'affects': ['Load Center', 'Battery Storage'],
            'price_multiplier': lambda: random.uniform(1.5, 2.2),
            'effect_desc': 'Mass EV charging spikes grid demand'
        },
        'earthquake|seismic': {
            'affects': ['Traditional', 'Load Center'],
            'price_multiplier': lambda: random.uniform(2.5, 4.0),
            'effect_desc': 'Seismic damage to power infrastructure'
        },
        'tsunami': {
            'affects': ['Traditional', 'Load Center'],
            'price_multiplier': lambda: random.uniform(4.0, 8.0),
            'effect_desc': 'Coastal power plants flooded, emergency grid activation'
        }
    }
    
    # Find matching scenario effects
    matched_effects = []
    for pattern, effect_info in scenario_effects.items():
        if re.search(pattern, scenario_lower):
            matched_effects.append(effect_info)
    
    # If no specific match, create a generic high-impact effect
    if not matched_effects:
        matched_effects = [{
            'affects': ['Traditional', 'Load Center'],
            'price_multiplier': lambda: random.uniform(1.5, 3.0),
            'effect_desc': 'Market disruption affecting energy prices'
        }]
    
    # Apply effects to matching locations
    for effect_info in matched_effects:
        affected_types = effect_info['affects']
        
        # First try geographic selection
        geographically_affected = find_affected_locations_by_geography(scenario, modified_data)
        
        if geographically_affected:
            # Use geographic selection - filter by type if specified
            if affected_types:
                locations_to_affect = [loc for loc in geographically_affected if loc['type'] in affected_types]
            else:
                locations_to_affect = geographically_affected[:15]  # Limit to top 15 closest
                
            # Apply distance-based intensity (closer locations get higher multipliers)
            for i, location in enumerate(locations_to_affect):
                # Base multiplier
                base_multiplier = effect_info['price_multiplier']()
                
                # Distance-based intensity (closer = more intense)
                distance_factor = 1.0 - (location.get('distance_from_impact', 0) / 200.0)  # Normalize to 200km max
                distance_factor = max(0.3, min(1.0, distance_factor))  # Keep between 0.3 and 1.0
                
                # Apply individual multiplier for this location
                individual_multiplier = base_multiplier * distance_factor
                
                # Add some randomness so not all locations have exactly the same multiplier
                random_factor = random.uniform(0.85, 1.15)
                final_multiplier = individual_multiplier * random_factor
                
                location['scenario_multiplier'] = final_multiplier
        else:
            # Fall back to type-based selection with individual multipliers
            affected_locations = [item for item in modified_data if item['type'] in affected_types]
            
            # Affect 60-80% of matching locations
            num_to_affect = max(1, int(len(affected_locations) * random.uniform(0.6, 0.8)))
            locations_to_affect = random.sample(affected_locations, min(num_to_affect, len(affected_locations)))
            
            # Give each location its own individual multiplier
            for location in locations_to_affect:
                individual_multiplier = effect_info['price_multiplier']()
                # Add randomness so they're not all the same
                random_factor = random.uniform(0.8, 1.2)
                final_multiplier = individual_multiplier * random_factor
                location['scenario_multiplier'] = final_multiplier
        
        for location in locations_to_affect:
            location_code = location['location_code']
            
            # Get the original base price for this location
            base_price = _price_history['base_prices'].get(location_code, location['price_mwh'])
            
            # Use the individual multiplier calculated above
            individual_multiplier = location.get('scenario_multiplier', effect_info['price_multiplier']())
            
            # Apply the scenario multiplier to the BASE price, not current price
            new_price = round(base_price * individual_multiplier, 2)
            new_price = max(0.01, new_price)  # Ensure price stays positive
            
            # Store the old price for effects summary
            old_price = location['price_mwh']
            location['price_mwh'] = new_price
            
            # Update price category
            if location['price_mwh'] > 100:
                location['price_category'] = 'critical'
            elif location['price_mwh'] > 50:
                location['price_category'] = 'high'
            elif location['price_mwh'] > 25:
                location['price_category'] = 'medium'
            else:
                location['price_category'] = 'low'
            
            # Add scenario effect indicator
            location['scenario_affected'] = True
            location['scenario_effect'] = effect_info['effect_desc']
            
            # Add geographic info if available
            if 'distance_from_impact' in location:
                location['distance_from_impact_km'] = round(location['distance_from_impact'], 1)
                location['impact_region'] = location.get('impact_region', 'unknown')
            
            # Calculate the ACTUAL change percent from base price for reporting
            actual_change_percent = ((new_price - base_price) / base_price * 100) if base_price != 0 else 0
            
            effects_applied.append({
                'location': location['name'],
                'location_code': location_code,
                'old_price': old_price,
                'new_price': new_price,
                'base_price': base_price,
                'multiplier_used': round(individual_multiplier, 3),
                'change_percent': round(actual_change_percent, 1),
                'distance_km': location.get('distance_from_impact', None),
                'effect': effect_info['effect_desc']
            })
    
    return modified_data, effects_applied

@app.route('/api/scenario-analysis', methods=['POST'])
def analyze_scenario():
    """
    Analyze a hypothetical scenario and generate multiple realistic energy market notifications
    with actual visual effects on the energy grid
    """
    try:
        data = request.get_json()
        scenario = data.get('scenario', '').strip()
        current_data = data.get('current_data', [])
        
        if not scenario:
            return jsonify({
                'success': False,
                'error': 'No scenario provided'
            }), 400
        
        # Apply scenario effects to the data first
        modified_data, effects_applied = apply_scenario_effects(scenario, current_data)
        
        # Now apply the unified price change calculations to get proper trends and percentages
        modified_data = calculate_unified_price_changes(modified_data)
        
        # Store the scenario-affected data as current data
        _price_history['current_scenario_data'] = [item.copy() for item in modified_data]
        
        # Add the modified data to price history AFTER calculations are complete
        add_to_price_history(modified_data, scenario)
        
        # Check if we have a valid AI client for generating notifications
        if not OPENROUTER_API_KEY or ai_client is None:
            # Return basic effects without AI-generated notifications
            return jsonify({
                'success': True,
                'notifications': [{
                    'message': f"Scenario '{scenario}' applied to {len(effects_applied)} locations",
                    'type': 'info',
                    'region': 'Texas Grid',
                    'impact': 'Medium'
                }],
                'modified_data': modified_data,
                'effects_summary': effects_applied[:5]  # Show first 5 effects
            })
            
        logger.info(f"Processing AI scenario analysis: {scenario}")
        
        # Create a more detailed and varied prompt for multiple notifications
        effects_summary = json.dumps(effects_applied[:8], indent=2) if effects_applied else "Effects being calculated..."
        
        prompt = f"""Generate 3-4 breaking news alerts for Texas energy market about: {scenario}

RULES:
- Each alert must be a complete, standalone news headline
- NO meta-commentary, explanations, or introductory text
- NO "Here are the alerts" or "Let me know" type messages
- Each alert should be 60-120 characters
- Include specific Texas locations: Houston, Dallas, San Antonio, Austin, Lubbock
- Include realistic numbers and percentages
- Focus on immediate market impact

EXAMPLES:
"Houston energy prices spike 340% as hurricane disrupts Gulf Coast refineries"
"ERCOT issues emergency alert: Dallas metro faces possible rolling blackouts"
"West Texas wind farms offline, electricity prices jump 85% statewide"

Return ONLY a clean JSON array like: ["Alert 1", "Alert 2", "Alert 3"]"""

        # Call the AI model with higher temperature for more variation
        try:
            response = ai_client.chat.completions.create(
                model="meta-llama/llama-3.1-8b-instruct:free",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a Texas energy market news reporter. Generate ONLY clean breaking news headlines. NO explanations, NO meta-commentary, NO introductions. Return ONLY a JSON array of news alerts."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=200,
                temperature=0.3,  # Lower temperature for cleaner, more focused responses
                extra_headers={
                    "HTTP-Referer": "http://localhost:3000",
                    "X-Title": "MARA Energy Analysis"
                }
            )
        except Exception as ai_error:
            if "401" in str(ai_error) or "auth" in str(ai_error).lower():
                return jsonify({
                    'success': False,
                    'error': 'OpenRouter API key is invalid or expired.',
                    'instructions': 'Please get a new API key at https://openrouter.ai/keys and update your .env file',
                    'details': str(ai_error)
                }), 401
            else:
                raise ai_error
        
        ai_response = response.choices[0].message.content.strip()
        
        # Parse AI response and clean up alerts
        notifications = []
        
        def is_valid_alert(text):
            """Check if text is a valid news alert"""
            if not text or len(text) < 20 or len(text) > 200:
                return False
            
            # Filter out meta-commentary
            invalid_phrases = [
                'here are', 'let me know', 'would you like', 'i can generate',
                'breaking news alerts', 'about the impact', 'generate more',
                'following alerts', 'these alerts'
            ]
            
            text_lower = text.lower()
            for phrase in invalid_phrases:
                if phrase in text_lower:
                    return False
                    
            return True
        
        try:
            # Try to parse as JSON first
            parsed_response = json.loads(ai_response)
            if isinstance(parsed_response, list):
                for item in parsed_response:
                    if isinstance(item, str) and is_valid_alert(item):
                        notifications.append({
                            'message': item.strip(),
                            'type': 'alert',
                            'region': 'Texas',
                            'impact': 'High'
                        })
                    elif isinstance(item, dict) and 'message' in item and is_valid_alert(item['message']):
                        notifications.append({
                            'message': item['message'].strip(),
                            'type': 'alert',
                            'region': 'Texas',
                            'impact': 'High'
                        })
        except:
            # Fallback: extract clean lines from text
            lines = [line.strip() for line in ai_response.split('\n') if line.strip()]
            
            for line in lines:
                # Clean up the line
                clean_line = line.strip('"').strip("'").strip('-').strip('*').strip(':').strip()
                
                # Remove any JSON formatting artifacts
                clean_line = clean_line.replace('[', '').replace(']', '').replace('{', '').replace('}', '')
                
                if is_valid_alert(clean_line):
                    notifications.append({
                        'message': clean_line,
                        'type': 'alert',
                        'region': 'Texas',
                        'impact': 'High'
                    })
                    
                # Limit to 4 alerts max
                if len(notifications) >= 4:
                    break
        
        # Ensure we have at least one clean notification
        if not notifications:
            # Generate a descriptive fallback alert based on scenario
            if 'hurricane' in scenario.lower() or 'storm' in scenario.lower():
                fallback_msg = "Hurricane in West Texas causes massive price increases across ERCOT grid"
            elif 'heat' in scenario.lower():
                fallback_msg = "Extreme heat wave in Texas drives electricity prices to record highs"
            elif 'freeze' in scenario.lower() or 'winter' in scenario.lower() or 'ice' in scenario.lower():
                fallback_msg = "Winter freeze in Texas causes widespread power plant outages and price spikes"
            elif 'wind' in scenario.lower():
                fallback_msg = "High winds shut down West Texas wind farms, electricity prices surge 200%"
            elif 'solar' in scenario.lower() or 'hail' in scenario.lower():
                fallback_msg = "Solar panel damage across Texas causes renewable energy shortage and price jumps"
            elif 'cyber' in scenario.lower() or 'hack' in scenario.lower():
                fallback_msg = "Cyberattack on Texas grid infrastructure triggers emergency pricing protocols"
            elif 'earthquake' in scenario.lower():
                fallback_msg = "Earthquake in West Texas damages power plants, causing statewide price volatility"
            elif 'fire' in scenario.lower():
                fallback_msg = "Wildfire near Houston refineries disrupts energy supply, prices skyrocket"
            else:
                fallback_msg = f"'{scenario}' event in Texas causes widespread energy market disruption and price spikes"
                
            notifications = [{
                'message': fallback_msg,
                'type': 'alert',
                'region': 'Texas',
                'impact': 'High'
            }]
        
        return jsonify({
            'success': True,
            'notifications': notifications,
            'modified_data': modified_data,
            'effects_summary': effects_applied[:8],  # Show first 8 effects
            'total_affected_locations': len(effects_applied)
        })
        
    except Exception as e:
        logger.error(f"Error in scenario analysis: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Analysis failed: {str(e)}'
        }), 500

@app.route('/api/reset-to-baseline', methods=['POST'])
def reset_to_baseline():
    """Reset all prices back to baseline and clear scenario history"""
    try:
        # Clear price history and current scenario data
        _price_history['data'].clear()
        _price_history['current_scenario_data'] = None
        
        # Get fresh base data
        base_data = get_static_base_data()
        
        # Initialize base prices and apply unified calculations
        initialize_base_prices()
        processed_data = calculate_unified_price_changes(base_data)
        
        # Add base data to history
        add_to_price_history(processed_data, 'baseline_reset')
        
        logger.info("System reset to baseline prices - cleared scenario data")
        
        return jsonify({
            'success': True,
            'message': 'System reset to baseline prices',
            'data': processed_data,
            'total_locations': len(processed_data)
        })
        
    except Exception as e:
        logger.error(f"Error resetting to baseline: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Reset failed: {str(e)}'
        }), 500

@app.route('/api/test-geographic-scenario', methods=['POST'])
def test_geographic_scenario():
    """Test endpoint for geographic scenario effects without AI"""
    try:
        data = request.get_json()
        scenario = data.get('scenario', 'hurricane hits Houston')
        
        # Get current data
        current_data = fetch_fresh_data()
        
        # Apply scenario effects
        modified_data, effects_applied = apply_scenario_effects(scenario, current_data)
        
        # Apply unified calculations
        modified_data = calculate_unified_price_changes(modified_data)
        
        # Store as current scenario data
        _price_history['current_scenario_data'] = [item.copy() for item in modified_data]
        
        # Add to history
        add_to_price_history(modified_data, scenario)
        
        # Check if geographic detection worked
        geographic_detected = any(effect.get('distance_km') is not None for effect in effects_applied)
        detected_regions = list(set([effect.get('distance_km') for effect in effects_applied if 'distance_km' in effect and effect['distance_km'] is not None]))
        
        return jsonify({
            'success': True,
            'scenario': scenario,
            'geographic_detection': geographic_detected,
            'total_affected': len(effects_applied),
            'effects_summary': effects_applied[:10],  # First 10 effects
            'geographic_analysis': {
                'geographic_locations': len([e for e in effects_applied if e.get('distance_km') is not None]),
                'unique_percentages': len(set([e['change_percent'] for e in effects_applied])),
                'distance_range': {
                    'min': min([e.get('distance_km', 999) for e in effects_applied if e.get('distance_km') is not None], default=0),
                    'max': max([e.get('distance_km', 0) for e in effects_applied if e.get('distance_km') is not None], default=0)
                },
                'regions_detected': [effect.get('impact_region') for effect in effects_applied if 'impact_region' in effect]
            }
        })
        
    except Exception as e:
        logger.error(f"Error in test geographic scenario: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/debug-prices', methods=['GET'])
def debug_prices():
    """Debug endpoint to check price calculation consistency"""
    try:
        # Get current data
        current_data = fetch_fresh_data()
        
        # Get base prices
        initialize_base_prices()
        base_prices = _price_history['base_prices'].copy()
        
        # Get price history
        history_info = {
            'total_entries': len(_price_history['data']),
            'scenarios': [entry.get('scenario', 'unknown') for entry in _price_history['data'][-5:]]
        }
        
        # Sample location analysis
        sample_locations = current_data[:3] if current_data else []
        location_analysis = []
        
        for loc in sample_locations:
            location_code = loc['location_code']
            analysis = {
                'location_code': location_code,
                'name': loc['name'],
                'type': loc['type'],
                'current_price': loc['price_mwh'],
                'base_price': base_prices.get(location_code, 'not_found'),
                'price_change': loc.get('price_change', 0),
                'price_change_percent': loc.get('price_change_percent', 0),
                'trend': loc.get('trend', 'unknown'),
                'scenario_affected': loc.get('scenario_affected', False),
                'base_change': loc.get('base_change', 0),
                'base_change_percent': loc.get('base_change_percent', 0)
            }
            location_analysis.append(analysis)
        
        return jsonify({
            'success': True,
            'base_prices_initialized': len(base_prices),
            'current_locations': len(current_data),
            'history_info': history_info,
            'sample_analysis': location_analysis,
            'calculation_logic': {
                'description': 'Unified price change calculation',
                'scenario_affected_logic': 'Shows change from base price',
                'non_affected_logic': 'Shows change from previous data point'
            }
        })
        
    except Exception as e:
        logger.error(f"Error in debug prices: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("🚀 MARA Energy Backend Starting...")
    print("📡 Server running on http://localhost:5001")
    print("⚡ GridStatus API integration enabled")
    print("🔄 No caching - fresh data every request")
    
    # Test data fetch on startup
    logger.info("Testing data fetch on startup...")
    test_data = fetch_fresh_data()
    logger.info(f"✅ Startup test successful - {len(test_data)} locations loaded")
    
    app.run(host='0.0.0.0', port=5001, debug=True) 