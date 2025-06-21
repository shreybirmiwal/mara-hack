from flask import Flask, jsonify, request
from flask_cors import CORS
from gridstatusio import GridStatusClient
import pandas as pd
from datetime import datetime, timedelta
import logging
import time
from openai import OpenAI
import json

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

# Cache for API responses
_cache = {
    'energy_data': None,
    'energy_stats': None,
    'last_fetch_time': None,
    'cache_duration': 300  # 5 minutes cache
}

# Price history storage (in production, this would be a database)
_price_history = {
    'data': [],  # List of {timestamp, location_data}
    'max_history': 50  # Keep last 50 data points
}

# Texas location data for ERCOT nodes (approximate coordinates)
LOCATION_DATA = {
    # Major Cities & Load Centers
    'HB_HOUSTON': {'lat': 29.7604, 'lng': -95.3698, 'name': 'Houston Hub', 'type': 'Load Center', 'capacity_mw': 2500, 'region': 'Southeast Texas'},
    'HB_NORTH': {'lat': 32.7767, 'lng': -96.7970, 'name': 'North Hub (Dallas)', 'type': 'Load Center', 'capacity_mw': 3000, 'region': 'North Texas'},
    'HB_SOUTH': {'lat': 29.4241, 'lng': -98.4936, 'name': 'South Hub (San Antonio)', 'type': 'Load Center', 'capacity_mw': 2000, 'region': 'South Texas'},
    'HB_WEST': {'lat': 31.5804, 'lng': -99.5805, 'name': 'West Hub', 'type': 'Load Center', 'capacity_mw': 1500, 'region': 'West Texas'},
    
    # Solar Installations
    'ZIER_SLR_ALL': {'lat': 32.7767, 'lng': -96.7970, 'name': 'Dallas Solar', 'type': 'Solar', 'capacity_mw': 180, 'region': 'North Texas'},
    'LAMESASLR_G': {'lat': 32.7373, 'lng': -101.9507, 'name': 'Lamesa Solar', 'type': 'Solar', 'capacity_mw': 200, 'region': 'West Texas'},
    'PECOS_SOLAR': {'lat': 31.4226, 'lng': -103.4933, 'name': 'Pecos Solar', 'type': 'Solar', 'capacity_mw': 250, 'region': 'West Texas'},
    'AUSTIN_SOLAR': {'lat': 30.2672, 'lng': -97.7431, 'name': 'Austin Solar', 'type': 'Solar', 'capacity_mw': 150, 'region': 'Central Texas'},
    
    # Wind Farms
    'YNG_WND_ALL': {'lat': 33.5779, 'lng': -101.8552, 'name': 'Lubbock Wind', 'type': 'Wind', 'capacity_mw': 400, 'region': 'West Texas'},
    'WND_WHITNEY': {'lat': 32.0543, 'lng': -97.3614, 'name': 'Fort Worth Wind', 'type': 'Wind', 'capacity_mw': 300, 'region': 'North Texas'},
    'WNDTS2_UNIT1': {'lat': 33.5779, 'lng': -101.8552, 'name': 'West Texas Wind', 'type': 'Wind', 'capacity_mw': 500, 'region': 'West Texas'},
    'QALSW_ALL': {'lat': 32.5007, 'lng': -99.7412, 'name': 'Sweetwater Wind', 'type': 'Wind', 'capacity_mw': 350, 'region': 'West Texas'},
    'GUNMTN_NODE': {'lat': 31.2593, 'lng': -104.5230, 'name': 'Gun Mountain Wind', 'type': 'Wind', 'capacity_mw': 280, 'region': 'West Texas'},
    'PANHNDLE_WND': {'lat': 35.2220, 'lng': -101.8313, 'name': 'Panhandle Wind', 'type': 'Wind', 'capacity_mw': 600, 'region': 'Panhandle'},
    
    # Traditional Power Plants
    'X443ESRN': {'lat': 31.3069, 'lng': -94.7319, 'name': 'East Texas Gas', 'type': 'Traditional', 'capacity_mw': 800, 'region': 'East Texas'},
    'WR_RN': {'lat': 31.5804, 'lng': -99.5805, 'name': 'West Texas Gas', 'type': 'Traditional', 'capacity_mw': 600, 'region': 'West Texas'},
    'WOODWRD2_RN': {'lat': 32.1543, 'lng': -95.8467, 'name': 'Woodward Gas', 'type': 'Traditional', 'capacity_mw': 750, 'region': 'East Texas'},
    'QALSW_CC1': {'lat': 32.5007, 'lng': -99.7412, 'name': 'Sweetwater CC', 'type': 'Traditional', 'capacity_mw': 900, 'region': 'West Texas'},
    'WLTC_ESR_RN': {'lat': 29.7604, 'lng': -95.3698, 'name': 'Houston Gas', 'type': 'Traditional', 'capacity_mw': 1200, 'region': 'Southeast Texas'},
    
    # Battery Storage
    'WRSBES_BESS1': {'lat': 29.7604, 'lng': -95.3698, 'name': 'Houston Battery', 'type': 'Battery Storage', 'capacity_mw': 100, 'region': 'Southeast Texas'},
    'WOV_BESS_RN': {'lat': 30.2672, 'lng': -97.7431, 'name': 'Austin Battery', 'type': 'Battery Storage', 'capacity_mw': 80, 'region': 'Central Texas'},
    'ALP_BESS_RN': {'lat': 30.3572, 'lng': -103.6404, 'name': 'Alpine Battery', 'type': 'Battery Storage', 'capacity_mw': 50, 'region': 'West Texas'},
    'WZRD_ESS_RN': {'lat': 30.2672, 'lng': -97.7431, 'name': 'Central Texas Battery', 'type': 'Battery Storage', 'capacity_mw': 120, 'region': 'Central Texas'},
    
    # Peaker Plants
    'W_PECO_UNIT1': {'lat': 28.8056, 'lng': -96.9778, 'name': 'Victoria Peaker', 'type': 'Peaker', 'capacity_mw': 200, 'region': 'South Texas'},
    'BROWNSVL_PK': {'lat': 25.9018, 'lng': -97.4975, 'name': 'Brownsville Peaker', 'type': 'Peaker', 'capacity_mw': 150, 'region': 'South Texas'},
    
    # Additional Load Zones
    'LCRA_ZONE': {'lat': 30.5085, 'lng': -97.8419, 'name': 'LCRA Zone', 'type': 'Load Zone', 'capacity_mw': 1000, 'region': 'Central Texas'},
    'ERCOT_ZONE1': {'lat': 29.7604, 'lng': -95.3698, 'name': 'Coast Zone', 'type': 'Load Zone', 'capacity_mw': 2000, 'region': 'Southeast Texas'},
    'ERCOT_ZONE2': {'lat': 31.7619, 'lng': -106.4850, 'name': 'Far West Zone', 'type': 'Load Zone', 'capacity_mw': 800, 'region': 'West Texas'},
    'ERCOT_ZONE3': {'lat': 32.7767, 'lng': -96.7970, 'name': 'North Central Zone', 'type': 'Load Zone', 'capacity_mw': 2500, 'region': 'North Texas'},
    'ERCOT_ZONE4': {'lat': 29.4241, 'lng': -98.4936, 'name': 'South Central Zone', 'type': 'Load Zone', 'capacity_mw': 1800, 'region': 'South Texas'}
}

def is_cache_valid():
    """Check if cache is still valid"""
    if _cache['last_fetch_time'] is None:
        return False
    
    time_diff = time.time() - _cache['last_fetch_time']
    return time_diff < _cache['cache_duration']

def add_to_price_history(data):
    """Add current data to price history"""
    timestamp = datetime.now().isoformat()
    _price_history['data'].append({
        'timestamp': timestamp,
        'locations': data
    })
    
    # Keep only the last max_history entries
    if len(_price_history['data']) > _price_history['max_history']:
        _price_history['data'] = _price_history['data'][-_price_history['max_history']:]

def calculate_price_changes(current_data):
    """Calculate price changes from previous data points"""
    if len(_price_history['data']) < 2:
        # Not enough history, return current data with zero changes
        for item in current_data:
            item['price_change'] = 0
            item['price_change_percent'] = 0
            item['trend'] = 'stable'
            item['price_history'] = [item['price_mwh']]  # Just current price
        return current_data
    
    # Get previous data point
    previous_data = _price_history['data'][-2]['locations']
    previous_by_code = {item['location_code']: item for item in previous_data}
    
    # Get last 10 data points for trend analysis
    recent_history = _price_history['data'][-10:]
    
    for item in current_data:
        location_code = item['location_code']
        current_price = item['price_mwh']
        
        # Calculate change from previous
        if location_code in previous_by_code:
            previous_price = previous_by_code[location_code]['price_mwh']
            price_change = current_price - previous_price
            price_change_percent = (price_change / previous_price * 100) if previous_price != 0 else 0
        else:
            price_change = 0
            price_change_percent = 0
        
        # Determine trend
        if price_change_percent > 5:
            trend = 'rising'
        elif price_change_percent < -5:
            trend = 'falling'
        else:
            trend = 'stable'
        
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
        
        # Add calculated fields
        item['price_change'] = round(price_change, 2)
        item['price_change_percent'] = round(price_change_percent, 1)
        item['trend'] = trend
        item['price_history'] = price_history
        
        # Add capacity_mw and region for frontend compatibility
        location_info = LOCATION_DATA.get(location_code, {})
        item['capacity_mw'] = location_info.get('capacity_mw', 100)
        item['region'] = location_info.get('region', 'West Texas')
    
    return current_data

def fetch_and_cache_data():
    """Fetch data from API and cache it"""
    try:
        # If no API client, use mock data
        if client is None:
            logger.info("No API client available, using mock data")
            df = pd.DataFrame()  # Empty dataframe to trigger mock data generation
        else:
            logger.info("Fetching fresh data from GridStatus API...")
            
            # Get just today's date for the most recent data point
            today = datetime.now().strftime("%Y-%m-%d")
            
            # Fetch data from GridStatus API with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    df = client.get_dataset(
                        dataset="ercot_spp_real_time_15_min",
                        start=today,
                        end=today,
                        timezone="market",
                    )
                    break
                except Exception as e:
                    logger.warning(f"API attempt {attempt + 1} failed: {str(e)}")
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)  # Exponential backoff
                    else:
                        # If all retries fail, use mock data
                        logger.error("All API attempts failed, using mock data")
                        df = pd.DataFrame()
                        break
            
            if not df.empty:
                logger.info(f"Retrieved {len(df)} records from GridStatus API")
        
        # Process and enrich data with location information
        processed_data = []
        
        # Get the most recent data point for each location
        if not df.empty:
            # Get the latest timestamp across all data
            latest_timestamp = df['interval_end_local'].max()
            logger.info(f"Latest data timestamp: {latest_timestamp}")
            
            # Filter to only the most recent data points
            latest_data = df[df['interval_end_local'] == latest_timestamp]
            
            for _, row in latest_data.iterrows():
                location_code = row['location']
                
                # Get location info or use defaults
                location_info = LOCATION_DATA.get(location_code, {
                    'lat': 31.9686, 'lng': -99.9018, 'name': location_code, 'type': 'Unknown'
                })
                
                # Convert pricing data (assuming it's in $/MWh)
                price = float(row.get('spp', 0)) if pd.notna(row.get('spp')) else 0
                
                processed_data.append({
                    'location_code': location_code,
                    'name': location_info['name'],  # Changed from location_name to name
                    'lat': location_info['lat'],
                    'lng': location_info['lng'],
                    'type': location_info['type'],
                    'capacity_mw': location_info.get('capacity_mw', 100),
                    'region': location_info.get('region', 'West Texas'),
                    'price_mwh': round(price, 2),
                    'timestamp': row['interval_end_local'].strftime('%Y-%m-%d %H:%M:%S') if pd.notna(row.get('interval_end_local')) else None,
                    'price_category': 'high' if price > 50 else 'medium' if price > 25 else 'low'
                })
        else:
            # If no API data, use mock data for demonstration
            logger.warning("No API data available, using mock data")
            import random
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Add some realistic variation to mock data if we have history
            base_variation = 0
            if len(_price_history['data']) > 0:
                # Add some market movement
                base_variation = random.uniform(-10, 10)
            
            for location_code, location_info in LOCATION_DATA.items():
                # Generate realistic mock prices based on location type
                if location_info['type'] == 'Solar':
                    base_price = random.uniform(15, 45)
                elif location_info['type'] == 'Wind':
                    base_price = random.uniform(20, 60)
                elif location_info['type'] == 'Traditional':
                    base_price = random.uniform(35, 85)
                elif location_info['type'] == 'Battery Storage':
                    base_price = random.uniform(40, 120)
                elif location_info['type'] == 'Peaker':
                    base_price = random.uniform(80, 200)
                else:
                    base_price = random.uniform(25, 75)
                
                # Apply market variation
                final_price = max(0, base_price + base_variation + random.uniform(-5, 5))
                
                processed_data.append({
                    'location_code': location_code,
                    'name': location_info['name'],  # Changed from location_name to name
                    'lat': location_info['lat'],
                    'lng': location_info['lng'],
                    'type': location_info['type'],
                    'capacity_mw': location_info.get('capacity_mw', 100),
                    'region': location_info.get('region', 'West Texas'),
                    'price_mwh': round(final_price, 2),
                    'timestamp': current_time,
                    'price_category': 'high' if final_price > 50 else 'medium' if final_price > 25 else 'low'
                })
        
        # Calculate price changes and add to history
        processed_data = calculate_price_changes(processed_data)
        add_to_price_history(processed_data)
        
        # Sort by price for better visualization
        processed_data.sort(key=lambda x: x['price_mwh'], reverse=True)
        
        # Calculate statistics from the single moment
        if processed_data:
            prices = [d['price_mwh'] for d in processed_data]
            stats = {
                'total_records': len(processed_data),
                'locations_count': len(processed_data),
                'avg_price': round(sum(prices) / len(prices), 2),
                'max_price': round(max(prices), 2),
                'min_price': round(min(prices), 2),
                'data_timestamp': processed_data[0]['timestamp'] if processed_data else None,
                'data_range': {
                    'start': today,
                    'end': today
                }
            }
        else:
            stats = {
                'total_records': 0,
                'locations_count': 0,
                'avg_price': 0,
                'max_price': 0,
                'min_price': 0,
                'data_timestamp': None,
                'data_range': {
                    'start': today,
                    'end': today
                }
            }
        
        # Update cache
        _cache['energy_data'] = processed_data
        _cache['energy_stats'] = stats
        _cache['last_fetch_time'] = time.time()
        
        logger.info(f"Cached {len(processed_data)} locations for timestamp: {stats.get('data_timestamp', 'N/A')}")
        return True
        
    except Exception as e:
        logger.error(f"Error fetching and caching data: {str(e)}")
        return False

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'OK', 'message': 'Backend is running'})

@app.route('/api/hello', methods=['GET'])
def hello():
    return jsonify({'message': 'Hello from MARA Energy Backend!'})

@app.route('/api/energy-data', methods=['GET'])
def get_energy_data():
    """Fetch real-time energy pricing data from ERCOT (with caching)"""
    try:
        # Check if we need to fetch fresh data
        if not is_cache_valid():
            success = fetch_and_cache_data()
            if not success and _cache['energy_data'] is None:
                return jsonify({
                    'success': False,
                    'error': 'Failed to fetch data and no cached data available',
                    'message': 'API temporarily unavailable'
                }), 503
        
        processed_data = _cache['energy_data'] or []
        
        return jsonify({
            'success': True,
            'data': processed_data,
            'total_locations': len(processed_data),
            'timestamp': datetime.now().isoformat(),
            'cached': is_cache_valid(),
            'cache_age_seconds': int(time.time() - _cache['last_fetch_time']) if _cache['last_fetch_time'] else 0,
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
    """Get summary statistics for energy data (with caching)"""
    try:
        # Use cached stats if available
        if is_cache_valid() and _cache['energy_stats']:
            return jsonify(_cache['energy_stats'])
        
        # If no valid cache, try to fetch fresh data
        if not is_cache_valid():
            success = fetch_and_cache_data()
            if not success and _cache['energy_stats'] is None:
                return jsonify({
                    'error': 'API temporarily unavailable',
                    'message': 'Failed to get energy statistics'
                }), 503
        
        return jsonify(_cache['energy_stats'] or {})
        
    except Exception as e:
        logger.error(f"Error getting energy stats: {str(e)}")
        return jsonify({
            'error': str(e),
            'message': 'Failed to get energy statistics'
        }), 500

@app.route('/api/cache-info', methods=['GET'])
def get_cache_info():
    """Get information about the current cache status"""
    return jsonify({
        'cache_valid': is_cache_valid(),
        'last_fetch_time': datetime.fromtimestamp(_cache['last_fetch_time']).isoformat() if _cache['last_fetch_time'] else None,
        'cache_age_seconds': int(time.time() - _cache['last_fetch_time']) if _cache['last_fetch_time'] else None,
        'cache_duration': _cache['cache_duration'],
        'has_energy_data': _cache['energy_data'] is not None,
        'has_energy_stats': _cache['energy_stats'] is not None,
        'data_count': len(_cache['energy_data']) if _cache['energy_data'] else 0
    })

@app.route('/api/scenario-analysis', methods=['POST'])
def analyze_scenario():
    """
    Analyze a hypothetical scenario and generate realistic energy market notifications
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
            
        if not OPENROUTER_API_KEY:
            # Return a mock notification for demo purposes
            mock_notification = {
                'message': f"West Texas wind farms see 250% surge in production due to {scenario.lower()}",
                'type': 'alert',
                'region': 'West Texas',
                'impact': 'High'
            }
            return jsonify({
                'success': True,
                'notification': mock_notification
            })
        
        # Initialize OpenAI client for OpenRouter
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENROUTER_API_KEY,
        )
        
        # Create a comprehensive prompt for realistic scenario analysis
        prompt = f"""You are an energy market analyst specializing in Texas ERCOT grid operations. 

SCENARIO: {scenario}

CURRENT ENERGY DATA CONTEXT:
{json.dumps(current_data[:10], indent=2) if current_data else "No current data available"}

Generate ONE realistic breaking news alert about how this scenario would impact West Texas energy markets. 

REQUIREMENTS:
- Write like a professional energy news ticker/alert
- Include specific percentage changes, locations, or infrastructure impacts
- Focus on realistic consequences (wind farms, solar installations, transmission lines, pricing)
- Keep it under 100 characters for a news ticker format
- Be authoritative and specific
- Don't use phrases like "could" or "might" - state impacts as if they're happening

EXAMPLES OF GOOD ALERTS:
- "West Texas wind farms see 250% surge in production due to increased wind"
- "ERCOT issues grid emergency as 3 major transmission lines fail in Permian Basin"
- "Solar installations in Lubbock offline after hailstorm, prices spike 40%"

Return ONLY the alert message, nothing else."""

        # Call the AI model
        response = client.chat.completions.create(
            model="meta-llama/llama-3.3-70b-instruct",
            messages=[
                {
                    "role": "system", 
                    "content": "You are a professional energy market news analyst. Generate realistic, specific breaking news alerts about energy market impacts."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=150,
            temperature=0.7
        )
        
        ai_message = response.choices[0].message.content.strip()
        
        # Clean up the message (remove quotes if present)
        if ai_message.startswith('"') and ai_message.endswith('"'):
            ai_message = ai_message[1:-1]
            
        # Create the notification
        notification = {
            'message': ai_message,
            'type': 'alert',
            'region': 'West Texas',
            'impact': 'High'
        }
        
        return jsonify({
            'success': True,
            'notification': notification
        })
        
    except Exception as e:
        logger.error(f"Error in scenario analysis: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Analysis failed: {str(e)}'
        }), 500

if __name__ == '__main__':
    print("🚀 MARA Energy Backend Starting...")
    print("📡 Server running on http://localhost:5001")
    print("⚡ GridStatus API integration enabled")
    print("💾 Data caching enabled (5 minute intervals)")
    
    # Pre-populate cache on startup
    logger.info("Pre-populating cache on startup...")
    fetch_and_cache_data()
    
    app.run(host='0.0.0.0', port=5001, debug=True) 