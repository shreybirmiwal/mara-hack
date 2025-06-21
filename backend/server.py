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

# Texas location data for ERCOT nodes (approximate coordinates)
LOCATION_DATA = {
    # Major Cities & Load Centers
    'HB_HOUSTON': {'lat': 29.7604, 'lng': -95.3698, 'name': 'Houston Hub', 'type': 'Load Center'},
    'HB_NORTH': {'lat': 32.7767, 'lng': -96.7970, 'name': 'North Hub (Dallas)', 'type': 'Load Center'},
    'HB_SOUTH': {'lat': 29.4241, 'lng': -98.4936, 'name': 'South Hub (San Antonio)', 'type': 'Load Center'},
    'HB_WEST': {'lat': 31.5804, 'lng': -99.5805, 'name': 'West Hub', 'type': 'Load Center'},
    
    # Solar Installations
    'ZIER_SLR_ALL': {'lat': 32.7767, 'lng': -96.7970, 'name': 'Dallas Solar', 'type': 'Solar'},
    'LAMESASLR_G': {'lat': 32.7373, 'lng': -101.9507, 'name': 'Lamesa Solar', 'type': 'Solar'},
    'PECOS_SOLAR': {'lat': 31.4226, 'lng': -103.4933, 'name': 'Pecos Solar', 'type': 'Solar'},
    'AUSTIN_SOLAR': {'lat': 30.2672, 'lng': -97.7431, 'name': 'Austin Solar', 'type': 'Solar'},
    
    # Wind Farms
    'YNG_WND_ALL': {'lat': 33.5779, 'lng': -101.8552, 'name': 'Lubbock Wind', 'type': 'Wind'},
    'WND_WHITNEY': {'lat': 32.0543, 'lng': -97.3614, 'name': 'Fort Worth Wind', 'type': 'Wind'},
    'WNDTS2_UNIT1': {'lat': 33.5779, 'lng': -101.8552, 'name': 'West Texas Wind', 'type': 'Wind'},
    'QALSW_ALL': {'lat': 32.5007, 'lng': -99.7412, 'name': 'Sweetwater Wind', 'type': 'Wind'},
    'GUNMTN_NODE': {'lat': 31.2593, 'lng': -104.5230, 'name': 'Gun Mountain Wind', 'type': 'Wind'},
    'PANHNDLE_WND': {'lat': 35.2220, 'lng': -101.8313, 'name': 'Panhandle Wind', 'type': 'Wind'},
    
    # Traditional Power Plants
    'X443ESRN': {'lat': 31.3069, 'lng': -94.7319, 'name': 'East Texas Gas', 'type': 'Traditional'},
    'WR_RN': {'lat': 31.5804, 'lng': -99.5805, 'name': 'West Texas Gas', 'type': 'Traditional'},
    'WOODWRD2_RN': {'lat': 32.1543, 'lng': -95.8467, 'name': 'Woodward Gas', 'type': 'Traditional'},
    'QALSW_CC1': {'lat': 32.5007, 'lng': -99.7412, 'name': 'Sweetwater CC', 'type': 'Traditional'},
    'WLTC_ESR_RN': {'lat': 29.7604, 'lng': -95.3698, 'name': 'Houston Gas', 'type': 'Traditional'},
    
    # Battery Storage
    'WRSBES_BESS1': {'lat': 29.7604, 'lng': -95.3698, 'name': 'Houston Battery', 'type': 'Battery Storage'},
    'WOV_BESS_RN': {'lat': 30.2672, 'lng': -97.7431, 'name': 'Austin Battery', 'type': 'Battery Storage'},
    'ALP_BESS_RN': {'lat': 30.3572, 'lng': -103.6404, 'name': 'Alpine Battery', 'type': 'Battery Storage'},
    'WZRD_ESS_RN': {'lat': 30.2672, 'lng': -97.7431, 'name': 'Central Texas Battery', 'type': 'Battery Storage'},
    
    # Peaker Plants
    'W_PECO_UNIT1': {'lat': 28.8056, 'lng': -96.9778, 'name': 'Victoria Peaker', 'type': 'Peaker'},
    'BROWNSVL_PK': {'lat': 25.9018, 'lng': -97.4975, 'name': 'Brownsville Peaker', 'type': 'Peaker'},
    
    # Additional Load Zones
    'LCRA_ZONE': {'lat': 30.5085, 'lng': -97.8419, 'name': 'LCRA Zone', 'type': 'Load Zone'},
    'ERCOT_ZONE1': {'lat': 29.7604, 'lng': -95.3698, 'name': 'Coast Zone', 'type': 'Load Zone'},
    'ERCOT_ZONE2': {'lat': 31.7619, 'lng': -106.4850, 'name': 'Far West Zone', 'type': 'Load Zone'},
    'ERCOT_ZONE3': {'lat': 32.7767, 'lng': -96.7970, 'name': 'North Central Zone', 'type': 'Load Zone'},
    'ERCOT_ZONE4': {'lat': 29.4241, 'lng': -98.4936, 'name': 'South Central Zone', 'type': 'Load Zone'}
}

def is_cache_valid():
    """Check if cache is still valid"""
    if _cache['last_fetch_time'] is None:
        return False
    
    time_diff = time.time() - _cache['last_fetch_time']
    return time_diff < _cache['cache_duration']

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
                    'location_name': location_info['name'],
                    'lat': location_info['lat'],
                    'lng': location_info['lng'],
                    'type': location_info['type'],
                    'price_mwh': round(price, 2),
                    'timestamp': row['interval_end_local'].strftime('%Y-%m-%d %H:%M:%S') if pd.notna(row.get('interval_end_local')) else None,
                    'price_category': 'high' if price > 50 else 'medium' if price > 25 else 'low'
                })
        else:
            # If no API data, use mock data for demonstration
            logger.warning("No API data available, using mock data")
            import random
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
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
                
                processed_data.append({
                    'location_code': location_code,
                    'location_name': location_info['name'],
                    'lat': location_info['lat'],
                    'lng': location_info['lng'],
                    'type': location_info['type'],
                    'price_mwh': round(base_price, 2),
                    'timestamp': current_time,
                    'price_category': 'high' if base_price > 50 else 'medium' if base_price > 25 else 'low'
                })
        
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
    """Analyze a scenario using AI and return notifications"""
    try:
        data = request.get_json()
        scenario = data.get('scenario', '').strip()
        current_data = data.get('current_data', [])
        
        if not scenario:
            return jsonify({
                'success': False,
                'error': 'Scenario description is required'
            }), 400
            
        if not ai_client:
            return jsonify({
                'success': False,
                'error': 'AI service not configured. Please set OPENROUTER_API_KEY environment variable.'
            }), 503
        
        # Prepare context about current energy situation
        energy_context = {
            'total_locations': len(current_data),
            'avg_price': round(sum([d['price_mwh'] for d in current_data]) / len(current_data), 2) if current_data else 0,
            'max_price': max([d['price_mwh'] for d in current_data]) if current_data else 0,
            'min_price': min([d['price_mwh'] for d in current_data]) if current_data else 0,
            'location_types': list(set([d['type'] for d in current_data])) if current_data else [],
            'high_price_locations': [d for d in current_data if d['price_mwh'] > 75] if current_data else []
        }
        
        # Create AI prompt
        system_prompt = """You are an expert energy market analyst specializing in Texas ERCOT grid operations. 
        You analyze scenarios and predict their impact on energy prices and grid stability.
        
        Your job is to analyze hypothetical scenarios and generate realistic notifications about their impacts.
        
        Return your response as a JSON object with a 'notifications' array. Each notification should have:
        - title: Short descriptive title (max 50 chars)
        - message: Detailed explanation (max 150 chars)  
        - type: one of 'alert', 'warning', 'info', 'success'
        - impact: Brief impact description (max 80 chars)
        
        Generate 2-4 notifications that would realistically occur from this scenario.
        Focus on specific impacts to different regions, facility types, and market prices.
        Be realistic but engaging."""
        
        user_prompt = f"""
        Current West Texas Energy Market Status:
        - Total locations monitored: {energy_context['total_locations']}
        - Average price: ${energy_context['avg_price']:.2f}/MWh
        - Price range: ${energy_context['min_price']:.2f} - ${energy_context['max_price']:.2f}/MWh
        - Energy types: {', '.join(energy_context['location_types'])}
        - High-price locations: {len(energy_context['high_price_locations'])} locations above $75/MWh
        
        Scenario to analyze: "{scenario}"
        
        Generate realistic notifications about what would happen to the Texas energy grid and prices.
        """
        
        # Call AI API
        try:
            completion = ai_client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": "https://mara-energy.local",
                    "X-Title": "MARA Energy Scenario Analysis",
                },
                model="meta-llama/llama-3.3-70b-instruct",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            ai_response = completion.choices[0].message.content
            logger.info(f"AI Response: {ai_response}")
            
            # Try to parse JSON response
            try:
                parsed_response = json.loads(ai_response)
                notifications = parsed_response.get('notifications', [])
            except json.JSONDecodeError:
                # If AI didn't return valid JSON, create fallback notifications
                logger.warning("AI response was not valid JSON, creating fallback notifications")
                notifications = [
                    {
                        "title": "Scenario Analysis Complete",
                        "message": "AI analysis indicates potential market impacts from the described scenario.",
                        "type": "info",
                        "impact": "Market volatility expected"
                    },
                    {
                        "title": "Price Impact Expected",
                        "message": f"Scenario '{scenario[:50]}...' could affect regional pricing patterns.",
                        "type": "warning", 
                        "impact": "Monitor grid stability"
                    }
                ]
            
            # Validate and clean notifications
            cleaned_notifications = []
            for notification in notifications[:4]:  # Max 4 notifications
                if isinstance(notification, dict):
                    cleaned_notification = {
                        'title': str(notification.get('title', 'Alert'))[:50],
                        'message': str(notification.get('message', 'Impact detected'))[:150],
                        'type': notification.get('type', 'info') if notification.get('type') in ['alert', 'warning', 'info', 'success'] else 'info',
                        'impact': str(notification.get('impact', 'Impact analysis'))[:80]
                    }
                    cleaned_notifications.append(cleaned_notification)
            
            if not cleaned_notifications:
                # Fallback if no valid notifications
                cleaned_notifications = [{
                    'title': 'Scenario Processed',
                    'message': 'Your scenario has been analyzed. Market impacts are being evaluated.',
                    'type': 'info',
                    'impact': 'Analysis complete'
                }]
            
            return jsonify({
                'success': True,
                'notifications': cleaned_notifications,
                'scenario': scenario,
                'analysis_timestamp': datetime.now().isoformat()
            })
            
        except Exception as ai_error:
            logger.error(f"AI API error: {str(ai_error)}")
            # Return fallback notifications if AI fails
            fallback_notifications = [
                {
                    'title': 'Analysis in Progress',
                    'message': 'Scenario impact assessment is being processed by our systems.',
                    'type': 'info',
                    'impact': 'Monitoring grid response'
                },
                {
                    'title': 'Market Alert',
                    'message': f'Potential impacts detected from: {scenario[:50]}{"..." if len(scenario) > 50 else ""}',
                    'type': 'warning',
                    'impact': 'Regional price volatility possible'
                }
            ]
            
            return jsonify({
                'success': True,
                'notifications': fallback_notifications,
                'scenario': scenario,
                'analysis_timestamp': datetime.now().isoformat(),
                'note': 'Using fallback analysis due to AI service limitations'
            })
        
    except Exception as e:
        logger.error(f"Error in scenario analysis: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to analyze scenario'
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