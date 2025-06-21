import random
import requests
import json
from flask import Flask, jsonify, request
from flask_cors import CORS
from dataclasses import dataclass
from typing import List, Dict, Any
import time

app = Flask(__name__)
CORS(app)

# MARA API configuration
MARA_API_BASE = "https://mara-hackathon-api.onrender.com"

@dataclass
class Site:
    id: int
    name: str
    lat: float
    lng: float
    api_key: str = None
    power: int = 0
    machines: Dict[str, Any] = None
    revenue_data: Dict[str, Any] = None
    created_at: str = None

class SiteManager:
    def __init__(self):
        self.sites: List[Site] = []
        self.current_prices = {}
        self.inventory = {}
        
    def generate_sf_coordinates(self) -> tuple:
        """Generate random coordinates within San Francisco bounds"""
        # San Francisco bounding box
        sf_bounds = {
            'lat_min': 37.7049,
            'lat_max': 37.8324,
            'lng_min': -122.5277,
            'lng_max': -122.3570
        }
        
        lat = random.uniform(sf_bounds['lat_min'], sf_bounds['lat_max'])
        lng = random.uniform(sf_bounds['lng_min'], sf_bounds['lng_max'])
        
        return lat, lng
    
    def create_site_with_mara_api(self, site_name: str) -> Dict[str, Any]:
        """Create a site using the MARA API"""
        try:
            response = requests.post(
                f"{MARA_API_BASE}/sites",
                json={"name": site_name},
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to create site {site_name}: {response.status_code}")
                return None
        except Exception as e:
            print(f"Error creating site {site_name}: {e}")
            return None
    
    def get_site_machines(self, api_key: str) -> Dict[str, Any]:
        """Get machine allocation for a site"""
        try:
            response = requests.get(
                f"{MARA_API_BASE}/machines",
                headers={"X-Api-Key": api_key},
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Error getting machines for site: {e}")
            return None
    
    def allocate_random_machines(self, api_key: str, max_power: int) -> bool:
        """Allocate random machines to a site within power constraints"""
        try:
            # Get inventory to understand machine types
            if not self.inventory:
                self.fetch_inventory()
            
            # Calculate random allocation within power limits
            machines = {
                "air_miners": 0,
                "hydro_miners": 0,
                "immersion_miners": 0,
                "gpu_compute": 0,
                "asic_compute": 0
            }
            
            # Randomly allocate machines while staying within power limits
            remaining_power = max_power
            
            # Add some randomness to machine allocation
            machine_types = [
                ("air_miners", 3500),
                ("hydro_miners", 5000), 
                ("immersion_miners", 10000),
                ("gpu_compute", 5000),
                ("asic_compute", 15000)
            ]
            
            for machine_type, power_per_unit in machine_types:
                if remaining_power > power_per_unit:
                    max_units = min(remaining_power // power_per_unit, random.randint(0, 20))
                    units = random.randint(0, max_units)
                    machines[machine_type] = units
                    remaining_power -= units * power_per_unit
            
            # Make API call to allocate machines
            response = requests.put(
                f"{MARA_API_BASE}/machines",
                headers={"X-Api-Key": api_key},
                json=machines,
                timeout=10
            )
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"Error allocating machines: {e}")
            return False
    
    def fetch_prices(self):
        """Fetch current prices from MARA API"""
        try:
            response = requests.get(f"{MARA_API_BASE}/prices", timeout=10)
            if response.status_code == 200:
                self.current_prices = response.json()
        except Exception as e:
            print(f"Error fetching prices: {e}")
    
    def fetch_inventory(self):
        """Fetch inventory from MARA API"""
        try:
            response = requests.get(f"{MARA_API_BASE}/inventory", timeout=10)
            if response.status_code == 200:
                self.inventory = response.json()
        except Exception as e:
            print(f"Error fetching inventory: {e}")
    
    def generate_sites(self, count: int = 50):
        """Generate the specified number of sites"""
        print(f"Generating {count} sites...")
        
        for i in range(count):
            lat, lng = self.generate_sf_coordinates()
            site_name = f"MaraSite_{i+1:02d}"
            
            # Create site with MARA API
            site_data = self.create_site_with_mara_api(site_name)
            
            if site_data:
                site = Site(
                    id=i+1,
                    name=site_data.get('name', site_name),
                    lat=lat,
                    lng=lng,
                    api_key=site_data.get('api_key'),
                    power=site_data.get('power', 0)
                )
                
                # Allocate random machines to the site
                if site.api_key and site.power > 0:
                    self.allocate_random_machines(site.api_key, site.power)
                    
                    # Get machine data after allocation
                    machine_data = self.get_site_machines(site.api_key)
                    if machine_data:
                        site.machines = machine_data
                
                self.sites.append(site)
                print(f"Created site {i+1}/{count}: {site_name}")
                
                # Small delay to avoid overwhelming the API
                time.sleep(0.1)
            else:
                # Create a site without API data as fallback
                site = Site(
                    id=i+1,
                    name=site_name,
                    lat=lat,
                    lng=lng,
                    power=random.randint(500000, 2000000)
                )
                self.sites.append(site)
                print(f"Created fallback site {i+1}/{count}: {site_name}")
        
        print(f"Successfully generated {len(self.sites)} sites")

# Initialize site manager
site_manager = SiteManager()

@app.route('/api/sites', methods=['GET'])
def get_sites():
    """Return all sites with their data"""
    sites_data = []
    for site in site_manager.sites:
        site_dict = {
            'id': site.id,
            'name': site.name,
            'lat': site.lat,
            'lng': site.lng,
            'power': site.power,
            'machines': site.machines,
            'api_key': site.api_key[:10] + '...' if site.api_key else None  # Truncate for security
        }
        sites_data.append(site_dict)
    
    return jsonify(sites_data)

@app.route('/api/sites/<int:site_id>', methods=['GET'])
def get_site(site_id):
    """Get detailed information for a specific site"""
    site = next((s for s in site_manager.sites if s.id == site_id), None)
    if not site:
        return jsonify({'error': 'Site not found'}), 404
    
    # Fetch fresh machine data if we have an API key
    if site.api_key:
        machine_data = site_manager.get_site_machines(site.api_key)
        if machine_data:
            site.machines = machine_data
    
    site_dict = {
        'id': site.id,
        'name': site.name,
        'lat': site.lat,
        'lng': site.lng,
        'power': site.power,
        'machines': site.machines,
        'api_key': site.api_key[:10] + '...' if site.api_key else None
    }
    
    return jsonify(site_dict)

@app.route('/api/prices', methods=['GET'])
def get_prices():
    """Get current market prices"""
    site_manager.fetch_prices()
    return jsonify(site_manager.current_prices)

@app.route('/api/inventory', methods=['GET'])
def get_inventory():
    """Get current inventory"""
    site_manager.fetch_inventory()
    return jsonify(site_manager.inventory)

@app.route('/api/generate-sites', methods=['POST'])
def generate_sites():
    """Generate new sites (for testing)"""
    count = request.json.get('count', 50) if request.json else 50
    site_manager.sites.clear()  # Clear existing sites
    site_manager.generate_sites(count)
    return jsonify({'message': f'Generated {len(site_manager.sites)} sites'})

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get overall statistics"""
    total_sites = len(site_manager.sites)
    total_power = sum(site.power for site in site_manager.sites)
    active_sites = sum(1 for site in site_manager.sites if site.api_key)
    
    return jsonify({
        'total_sites': total_sites,
        'active_sites': active_sites,
        'total_power': total_power,
        'api_connected': active_sites > 0
    })

if __name__ == '__main__':
    print("Starting MARA Site Manager...")
    
    # Generate initial sites
    site_manager.generate_sites(5)
    
    # Fetch initial market data
    site_manager.fetch_prices()
    site_manager.fetch_inventory()
    
    print("Server ready!")
    app.run(debug=True)
