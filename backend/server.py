from flask import Flask, jsonify, request
from flask_cors import CORS
from gridstatusio import GridStatusClient
import pandas as pd
from datetime import datetime, timedelta
import logging
import time

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize GridStatus client
client = GridStatusClient("5871cfc0f3194b91a96fbfaef0df067a")

# Cache for API responses
_cache = {
    'energy_data': None,
    'energy_stats': None,
    'last_fetch_time': None,
    'cache_duration': 300  # 5 minutes cache
}

# Texas location data for ERCOT nodes (approximate coordinates)
LOCATION_DATA = {
    'ZIER_SLR_ALL': {'lat': 32.7767, 'lng': -96.7970, 'name': 'Dallas Area', 'type': 'Solar'},
    'YNG_WND_ALL': {'lat': 33.5779, 'lng': -101.8552, 'name': 'Lubbock Area', 'type': 'Wind'},
    'X443ESRN': {'lat': 31.3069, 'lng': -94.7319, 'name': 'East Texas', 'type': 'Traditional'},
    'WZRD_ESS_RN': {'lat': 30.2672, 'lng': -97.7431, 'name': 'Austin Area', 'type': 'Storage'},
    'WRSBES_BESS1': {'lat': 29.7604, 'lng': -95.3698, 'name': 'Houston Area', 'type': 'Battery Storage'},
    'WR_RN': {'lat': 31.5804, 'lng': -99.5805, 'name': 'West Texas', 'type': 'Traditional'},
    'W_PECO_UNIT1': {'lat': 28.8056, 'lng': -96.9778, 'name': 'Victoria Area', 'type': 'Peaker'},
    'WOV_BESS_RN': {'lat': 30.2672, 'lng': -97.7431, 'name': 'Central Texas', 'type': 'Battery Storage'},
    'WOODWRD2_RN': {'lat': 32.1543, 'lng': -95.8467, 'name': 'East Texas', 'type': 'Traditional'},
    'WOODWRD1_RN': {'lat': 32.1543, 'lng': -95.8467, 'name': 'East Texas', 'type': 'Traditional'},
    'WND_WHITNEY': {'lat': 32.0543, 'lng': -97.3614, 'name': 'Fort Worth Area', 'type': 'Wind'},
    'WNDTS2_UNIT1': {'lat': 33.5779, 'lng': -101.8552, 'name': 'West Texas', 'type': 'Wind'},
    'WLTC_ESR_RN': {'lat': 29.7604, 'lng': -95.3698, 'name': 'Houston Area', 'type': 'Traditional'},
    'GUNMTN_NODE': {'lat': 31.2593, 'lng': -104.5230, 'name': 'Gun Mountain', 'type': 'Wind'},
    'ALP_BESS_RN': {'lat': 30.3572, 'lng': -103.6404, 'name': 'Alpine Battery', 'type': 'Battery Storage'},
    'LAMESASLR_G': {'lat': 32.7373, 'lng': -101.9507, 'name': 'Lamesa Solar', 'type': 'Solar'},
    'QALSW_ALL': {'lat': 32.5007, 'lng': -99.7412, 'name': 'Sweetwater Area', 'type': 'Wind'},
    'QALSW_CC1': {'lat': 32.5007, 'lng': -99.7412, 'name': 'Sweetwater CC1', 'type': 'Traditional'}
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
        logger.info("Fetching fresh data from GridStatus API...")
        
        # Get date range (last 2 days for recent data - reduced to avoid rate limits)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=2)
        
        # Fetch data from GridStatus API with retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                df = client.get_dataset(
                    dataset="ercot_spp_real_time_15_min",
                    start=start_date.strftime("%Y-%m-%d"),
                    end=end_date.strftime("%Y-%m-%d"),
                    timezone="market",
                )
                break
            except Exception as e:
                logger.warning(f"API attempt {attempt + 1} failed: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise e
        
        logger.info(f"Retrieved {len(df)} records from GridStatus API")
        
        # Process and enrich data with location information
        processed_data = []
        
        # Get latest data for each location
        if not df.empty:
            latest_data = df.groupby('location').last().reset_index()
            
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
        
        # Sort by price for better visualization
        processed_data.sort(key=lambda x: x['price_mwh'], reverse=True)
        
        # Calculate statistics
        stats = {
            'total_records': len(df),
            'locations_count': df['location'].nunique() if not df.empty else 0,
            'avg_price': round(df['spp'].mean(), 2) if not df.empty and 'spp' in df.columns else 0,
            'max_price': round(df['spp'].max(), 2) if not df.empty and 'spp' in df.columns else 0,
            'min_price': round(df['spp'].min(), 2) if not df.empty and 'spp' in df.columns else 0,
            'data_range': {
                'start': start_date.strftime('%Y-%m-%d'),
                'end': end_date.strftime('%Y-%m-%d')
            }
        }
        
        # Update cache
        _cache['energy_data'] = processed_data
        _cache['energy_stats'] = stats
        _cache['last_fetch_time'] = time.time()
        
        logger.info(f"Cached {len(processed_data)} locations")
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

if __name__ == '__main__':
    print("🚀 MARA Energy Backend Starting...")
    print("📡 Server running on http://localhost:5001")
    print("⚡ GridStatus API integration enabled")
    print("💾 Data caching enabled (5 minute intervals)")
    
    # Pre-populate cache on startup
    logger.info("Pre-populating cache on startup...")
    fetch_and_cache_data()
    
    app.run(host='0.0.0.0', port=5001, debug=True) 