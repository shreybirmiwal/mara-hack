from flask import Flask, jsonify, request
from flask_cors import CORS
from gridstatusio import GridStatusClient
import pandas as pd
from datetime import datetime, timedelta
import logging

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize GridStatus client
client = GridStatusClient("5871cfc0f3194b91a96fbfaef0df067a")

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
    'WLTC_ESR_RN': {'lat': 29.7604, 'lng': -95.3698, 'name': 'Houston Area', 'type': 'Traditional'}
}

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'OK', 'message': 'Backend is running'})

@app.route('/api/hello', methods=['GET'])
def hello():
    return jsonify({'message': 'Hello from MARA Energy Backend!'})

@app.route('/api/energy-data', methods=['GET'])
def get_energy_data():
    """Fetch real-time energy pricing data from ERCOT"""
    try:
        logger.info("Fetching energy data from GridStatus API...")
        
        # Get date range (last 3 days for recent data)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=3)
        
        # Fetch data from GridStatus API
        df = client.get_dataset(
            dataset="ercot_spp_real_time_15_min",
            start=start_date.strftime("%Y-%m-%d"),
            end=end_date.strftime("%Y-%m-%d"),
            timezone="market",
        )
        
        logger.info(f"Retrieved {len(df)} records from GridStatus API")
        
        # Process and enrich data with location information
        processed_data = []
        
        # Get latest data for each location
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
        
        logger.info(f"Processed {len(processed_data)} locations")
        
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
        logger.error(f"Error fetching energy data: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to fetch energy data'
        }), 500

@app.route('/api/energy-stats', methods=['GET'])
def get_energy_stats():
    """Get summary statistics for energy data"""
    try:
        # Get date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)  # Last week for trends
        
        df = client.get_dataset(
            dataset="ercot_spp_real_time_15_min",
            start=start_date.strftime("%Y-%m-%d"),
            end=end_date.strftime("%Y-%m-%d"),
            timezone="market",
        )
        
        # Calculate statistics
        stats = {
            'total_records': len(df),
            'locations_count': df['location'].nunique(),
            'avg_price': round(df['spp'].mean(), 2) if 'spp' in df.columns else 0,
            'max_price': round(df['spp'].max(), 2) if 'spp' in df.columns else 0,
            'min_price': round(df['spp'].min(), 2) if 'spp' in df.columns else 0,
            'data_range': {
                'start': start_date.strftime('%Y-%m-%d'),
                'end': end_date.strftime('%Y-%m-%d')
            }
        }
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Error getting energy stats: {str(e)}")
        return jsonify({
            'error': str(e),
            'message': 'Failed to get energy statistics'
        }), 500

if __name__ == '__main__':
    print("🚀 MARA Energy Backend Starting...")
    print("📡 Server running on http://localhost:5001")
    print("⚡ GridStatus API integration enabled")
    app.run(host='0.0.0.0', port=5001, debug=True) 