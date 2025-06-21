import random
import requests
import json
from flask import Flask, jsonify, request
from flask_cors import CORS
from dataclasses import dataclass
from typing import List, Dict, Any
import time
import threading
from datetime import datetime

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
        self.active_events = {}  # Track active weather/disaster events
        
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
    
    def get_location_modifiers(self, lat: float, lng: float) -> Dict[str, float]:
        """Calculate location-based modifiers for machine performance"""
        modifiers = {
            "energy_cost_modifier": 1.0,
            "cooling_efficiency": 1.0,
            "hydro_efficiency": 1.0,
            "network_latency": 1.0
        }
        
        # San Francisco micro-climate zones with dramatic differences
        # Financial District (very expensive energy, poor cooling, excellent network)
        if 37.7849 < lat < 37.7949 and -122.4094 < lng < -122.3994:
            modifiers["energy_cost_modifier"] = 1.5   # +50% energy cost (premium location)
            modifiers["cooling_efficiency"] = 0.7     # -30% cooling (dense urban heat)
            modifiers["network_latency"] = 0.6        # +67% compute performance (fiber backbone)
            
        # Near Ocean/Sunset (cheap energy, excellent cooling, poor network)
        elif lat < 37.7600 and lng < -122.4800:
            modifiers["energy_cost_modifier"] = 0.6   # -40% energy cost (residential rates)
            modifiers["cooling_efficiency"] = 1.4     # +40% cooling (ocean breeze)
            modifiers["network_latency"] = 1.6        # -38% compute performance (far from data centers)
            modifiers["hydro_efficiency"] = 1.3       # +30% hydro (near ocean)
            
        # SOMA (moderate energy, good network, average cooling)
        elif 37.7700 < lat < 37.7800 and -122.4200 < lng < -122.4100:
            modifiers["energy_cost_modifier"] = 1.1   # +10% energy cost
            modifiers["network_latency"] = 0.8        # +25% compute performance
            modifiers["cooling_efficiency"] = 1.0     # neutral cooling
            
        # Mission District (very cheap energy, hot climate, poor hydro)
        elif 37.7500 < lat < 37.7700 and -122.4300 < lng < -122.4100:
            modifiers["energy_cost_modifier"] = 0.7   # -30% energy cost
            modifiers["cooling_efficiency"] = 0.8     # -20% cooling (warmer, denser)
            modifiers["hydro_efficiency"] = 1.5       # +50% hydro (good water infrastructure)
            
        # Near Water/Embarcadero (very expensive, excellent cooling and hydro)
        elif lng > -122.3900:
            modifiers["energy_cost_modifier"] = 1.6   # +60% energy cost (waterfront premium)
            modifiers["cooling_efficiency"] = 1.5     # +50% cooling (water cooling)
            modifiers["hydro_efficiency"] = 1.8       # +80% hydro (direct water access)
            
        # Hills (Richmond, Nob Hill) - cheap energy, good cooling, poor hydro
        elif lat > 37.7850:
            modifiers["energy_cost_modifier"] = 0.8   # -20% energy cost
            modifiers["cooling_efficiency"] = 1.2     # +20% cooling (elevation/wind)
            modifiers["hydro_efficiency"] = 0.5       # -50% hydro (water pressure issues)
        
        # Add some randomness for micro-variations (+/- 5%)
        for key in modifiers:
            variation = random.uniform(0.95, 1.05)
            modifiers[key] *= variation
            
        return modifiers

    def calculate_machine_profitability(self, lat: float = None, lng: float = None) -> Dict[str, float]:
        """Calculate profit per hour for each machine type based on current prices and location"""
        # Use default prices if API prices not available
        if self.current_prices:
            latest_price = self.current_prices[0] if self.current_prices else {}
            base_energy_price = latest_price.get('energy_price', 0.65)  # $/MWh
            hash_price = latest_price.get('hash_price', 8.5)           # $/TH/s
            token_price = latest_price.get('token_price', 3.0)         # $/token
        else:
            # Default market prices for testing/fallback
            base_energy_price = 0.65  # $/MWh
            hash_price = 8.5          # $/TH/s  
            token_price = 0.001       # $/token (much more realistic pricing)
        
        # Apply location modifiers if coordinates provided
        location_modifiers = self.get_location_modifiers(lat, lng) if lat and lng else {
            "energy_cost_modifier": 1.0, "cooling_efficiency": 1.0, 
            "hydro_efficiency": 1.0, "network_latency": 1.0
        }
        
        # Apply event modifiers if there are active events
        if lat and lng and self.active_events:
            location_modifiers = self.apply_event_modifiers(lat, lng, location_modifiers)
        
        # Adjust prices based on location
        energy_price = base_energy_price * location_modifiers["energy_cost_modifier"]
        
        # Machine specifications: (base_power_watts, output_per_hour, revenue_type)
        machine_specs = {
            "air_miners": (3500, 1.0, "hash"),      # 1 TH/s hash rate
            "hydro_miners": (5000, 5.0, "hash"),    # 5 TH/s hash rate  
            "immersion_miners": (10000, 10.0, "hash"), # 10 TH/s hash rate
            "gpu_compute": (5000, 1000, "token"),   # 1000 tokens/hour
            "asic_compute": (15000, 50000, "token") # 50000 tokens/hour
        }
        
        profitability = {}
        
        for machine_type, (base_power, base_output, revenue_type) in machine_specs.items():
            # Apply location-specific modifiers
            if "hydro" in machine_type:
                output = base_output * location_modifiers["hydro_efficiency"]
                power_watts = base_power / location_modifiers["cooling_efficiency"]  # Better cooling = less power
            elif "compute" in machine_type:
                output = base_output * location_modifiers["network_latency"]
                power_watts = base_power / location_modifiers["cooling_efficiency"]
            else:  # air/immersion miners
                output = base_output
                power_watts = base_power / location_modifiers["cooling_efficiency"]
            
            # Calculate energy cost per hour
            energy_cost_per_hour = (power_watts / 1_000_000) * energy_price
            
            # Calculate revenue per hour
            if revenue_type == "hash":
                revenue_per_hour = output * hash_price
            else:  # token
                revenue_per_hour = output * token_price
            
            # Net profit per hour
            profit_per_hour = revenue_per_hour - energy_cost_per_hour
            profitability[machine_type] = profit_per_hour
            
            if lat and lng:  # Only print detailed info when optimizing specific sites
                print(f"{machine_type}: ${profit_per_hour:.2f}/hr (Revenue: ${revenue_per_hour:.2f}, Cost: ${energy_cost_per_hour:.2f}) [Location adjusted]")
        
        return profitability

    def get_detailed_profitability(self, lat: float, lng: float) -> Dict[str, Any]:
        """Get detailed profitability breakdown for each machine type at a specific location"""
        # Get current prices
        if self.current_prices:
            latest_price = self.current_prices[0] if self.current_prices else {}
            base_energy_price = latest_price.get('energy_price', 0.65)  # $/MWh
            hash_price = latest_price.get('hash_price', 8.5)           # $/TH/s
            token_price = latest_price.get('token_price', 3.0)         # $/token
        else:
            # Default market prices for testing/fallback
            base_energy_price = 0.65  # $/MWh
            hash_price = 8.5          # $/TH/s  
            token_price = 0.001       # $/token (much more realistic pricing)
        
        # Get location modifiers
        location_modifiers = self.get_location_modifiers(lat, lng)
        
        # Apply event modifiers if there are active events
        if self.active_events:
            location_modifiers = self.apply_event_modifiers(lat, lng, location_modifiers)
        
        # Adjust energy price based on location
        energy_price = base_energy_price * location_modifiers["energy_cost_modifier"]
        
        # Machine specifications: (power_watts, output_per_hour, revenue_type, description)
        machine_specs = {
            "air_miners": (3500, 1.0, "hash", "Air-cooled Bitcoin miners"),
            "hydro_miners": (5000, 5.0, "hash", "Water-cooled Bitcoin miners"),
            "immersion_miners": (10000, 10.0, "hash", "Immersion-cooled Bitcoin miners"),
            "gpu_compute": (5000, 1000, "token", "GPU-based AI compute"),
            "asic_compute": (15000, 50000, "token", "ASIC-based AI compute")
        }
        
        detailed_analysis = {}
        
        for machine_type, (base_power, base_output, revenue_type, description) in machine_specs.items():
            # Apply location-specific modifiers to performance
            if "hydro" in machine_type:
                actual_output = base_output * location_modifiers["hydro_efficiency"]
                actual_power = base_power / location_modifiers["cooling_efficiency"]
            elif "compute" in machine_type:
                actual_output = base_output * location_modifiers["network_latency"]
                actual_power = base_power / location_modifiers["cooling_efficiency"]
            else:  # air/immersion miners
                actual_output = base_output
                actual_power = base_power / location_modifiers["cooling_efficiency"]
            
            # Calculate costs and revenue per hour
            energy_cost_per_hour = (actual_power / 1_000_000) * energy_price  # Convert W to MW
            
            if revenue_type == "hash":
                revenue_per_hour = actual_output * hash_price
                unit = "TH/s"
            else:  # token
                revenue_per_hour = actual_output * token_price
                unit = "tokens/hr"
            
            profit_per_hour = revenue_per_hour - energy_cost_per_hour
            
            detailed_analysis[machine_type] = {
                "description": description,
                "base_output": base_output,
                "actual_output": round(actual_output, 2),
                "unit": unit,
                "base_power": base_power,
                "actual_power": round(actual_power, 0),
                "energy_cost_per_hour": round(energy_cost_per_hour, 4),
                "revenue_per_hour": round(revenue_per_hour, 4),
                "profit_per_hour": round(profit_per_hour, 4),
                "revenue_type": revenue_type
            }
        
        # Calculate optimal allocation given power constraint
        optimal_allocation = self.calculate_optimal_allocation(detailed_analysis, 1000000)  # 1MW power budget
        
        return {
            "location_modifiers": location_modifiers,
            "market_prices": {
                "energy_price": energy_price,
                "hash_price": hash_price,
                "token_price": token_price
            },
            "machines": detailed_analysis,
            "optimal_allocation": optimal_allocation
        }

    def calculate_optimal_allocation(self, machine_analysis: Dict[str, Any], power_budget: int) -> Dict[str, Any]:
        """Calculate optimal machine allocation given power budget to maximize profit"""
        # Sort machines by profit per hour (descending)
        sorted_machines = sorted(
            machine_analysis.items(), 
            key=lambda x: x[1]["profit_per_hour"], 
            reverse=True
        )
        
        allocation = {}
        remaining_power = power_budget
        total_profit = 0
        
        for machine_type, machine_data in sorted_machines:
            if machine_data["profit_per_hour"] <= 0:
                allocation[machine_type] = 0
                continue
                
            power_per_unit = machine_data["actual_power"]
            max_units = int(remaining_power // power_per_unit)
            
            if max_units > 0:
                # Use a more sophisticated allocation strategy
                # Allocate based on profit density but don't put all eggs in one basket
                if machine_type == sorted_machines[0][0]:  # Most profitable
                    units = min(max_units, max(1, int(max_units * 0.7)))  # Up to 70%
                else:
                    profit_ratio = machine_data["profit_per_hour"] / sorted_machines[0][1]["profit_per_hour"]
                    allocation_factor = max(0.1, min(0.5, profit_ratio))
                    units = min(max_units, max(1, int(max_units * allocation_factor)))
                
                allocation[machine_type] = units
                power_used = units * power_per_unit
                remaining_power -= power_used
                total_profit += units * machine_data["profit_per_hour"]
            else:
                allocation[machine_type] = 0
        
        return {
            "allocation": allocation,
            "total_power_used": power_budget - remaining_power,
            "remaining_power": remaining_power,
            "total_profit_per_hour": round(total_profit, 2),
            "power_budget": power_budget
        }

    def apply_event_modifiers(self, lat: float, lng: float, base_modifiers: Dict[str, float]) -> Dict[str, float]:
        """Apply disaster/weather event modifiers to location modifiers"""
        modified = base_modifiers.copy()
        
        for event_id, event_data in self.active_events.items():
            event_lat, event_lng = event_data['lat'], event_data['lng']
            event_type = event_data['type']
            event_radius = event_data.get('radius', 0.01)  # Default ~1km radius
            
            # Calculate distance from event
            distance = ((lat - event_lat) ** 2 + (lng - event_lng) ** 2) ** 0.5
            
            if distance <= event_radius:
                intensity = max(0.1, 1 - (distance / event_radius))  # Closer = more intense
                
                if event_type == "flood":
                    modified["hydro_efficiency"] *= (0.3 * intensity)  # Hydro miners heavily affected
                    modified["cooling_efficiency"] *= (0.8 * intensity)  # Cooling issues
                    modified["energy_cost_modifier"] *= (1 + 0.5 * intensity)  # Higher energy costs
                elif event_type == "heatwave":
                    modified["cooling_efficiency"] *= (0.7 * intensity)  # Need more cooling
                    modified["energy_cost_modifier"] *= (1 + 0.3 * intensity)  # Higher cooling costs
                elif event_type == "power_outage":
                    modified["energy_cost_modifier"] *= (2.0 * intensity)  # Backup power expensive
                    modified["network_latency"] *= (0.5 * intensity)  # Poor connectivity
                elif event_type == "earthquake":
                    # All efficiency reduced
                    for key in modified:
                        if "efficiency" in key:
                            modified[key] *= (0.6 * intensity)
                    
                print(f"  📍 Event '{event_type}' affecting site (intensity: {intensity:.2f})")
        
        return modified

    def simulate_event(self, event_description: str) -> Dict[str, Any]:
        """Parse natural language event description and apply effects"""
        event_description = event_description.lower()
        
        # Simple keyword-based parsing (in real app, you'd use an LLM)
        event_data = {}
        
        # Parse event type
        if "flood" in event_description:
            event_data['type'] = "flood"
            event_data['radius'] = 0.02  # Larger radius for floods
        elif "heat" in event_description or "hot" in event_description:
            event_data['type'] = "heatwave"
            event_data['radius'] = 0.05  # Heat affects large areas
        elif "power" in event_description and "outage" in event_description:
            event_data['type'] = "power_outage"
            event_data['radius'] = 0.015
        elif "earthquake" in event_description or "quake" in event_description:
            event_data['type'] = "earthquake"
            event_data['radius'] = 0.03
        else:
            return {"error": "Could not understand event type"}
        
        # Parse location (simple keyword matching)
        if "downtown" in event_description or "financial" in event_description:
            event_data['lat'] = 37.7899
            event_data['lng'] = -122.4044
            location_name = "Financial District"
        elif "mission" in event_description:
            event_data['lat'] = 37.7599
            event_data['lng'] = -122.4148
            location_name = "Mission District"
        elif "sunset" in event_description or "ocean" in event_description:
            event_data['lat'] = 37.7469
            event_data['lng'] = -122.4684
            location_name = "Sunset District"
        elif "soma" in event_description:
            event_data['lat'] = 37.7749
            event_data['lng'] = -122.4194
            location_name = "SOMA"
        else:
            # Default to city center
            event_data['lat'] = 37.7749
            event_data['lng'] = -122.4194
            location_name = "San Francisco"
        
        # Generate event ID and store
        import uuid
        event_id = str(uuid.uuid4())[:8]
        self.active_events[event_id] = event_data
        
        # Trigger immediate re-optimization of affected sites
        affected_sites = []
        for site in self.sites:
            if site.api_key and site.power > 0:
                distance = ((site.lat - event_data['lat']) ** 2 + (site.lng - event_data['lng']) ** 2) ** 0.5
                if distance <= event_data['radius']:
                    affected_sites.append(site.name)
                    # Re-optimize this site
                    self.optimize_machine_allocation(site.api_key, site.power, site.lat, site.lng)
                    # Update site data
                    machine_data = self.get_site_machines(site.api_key)
                    if machine_data:
                        site.machines = machine_data
        
        return {
            "event_id": event_id,
            "event_type": event_data['type'],
            "location": location_name,
            "affected_sites": affected_sites,
            "message": f"Applied {event_data['type']} event in {location_name}. {len(affected_sites)} sites affected."
        }

    def clear_event(self, event_id: str) -> bool:
        """Remove an active event and re-optimize affected sites"""
        if event_id in self.active_events:
            del self.active_events[event_id]
            # Re-optimize all sites to remove event effects
            self.auto_optimize_all_sites()
            return True
        return False

    def optimize_machine_allocation(self, api_key: str, max_power: int, lat: float = None, lng: float = None) -> bool:
        """Optimally allocate machines to maximize profit based on location"""
        try:
            # Get current profitability with location adjustments
            profitability = self.calculate_machine_profitability(lat, lng)
            if not profitability:
                print("No profitability data available, using random allocation")
                return self.allocate_random_machines(api_key, max_power)
            
            # Sort machine types by profitability (highest first)
            sorted_machines = sorted(profitability.items(), key=lambda x: x[1], reverse=True)
            
            # Machine power requirements
            machine_power = {
                "air_miners": 3500,
                "hydro_miners": 5000,
                "immersion_miners": 10000,
                "gpu_compute": 5000,
                "asic_compute": 15000
            }
            
            # Start with empty allocation
            optimal_allocation = {
                "air_miners": 0,
                "hydro_miners": 0,
                "immersion_miners": 0,
                "gpu_compute": 0,
                "asic_compute": 0
            }
            
            remaining_power = max_power
            
            print(f"Optimizing allocation for {max_power}W capacity...")
            
            # Allocate machines starting with most profitable
            # Use profitability ratios to determine allocation percentages
            total_profit = sum(max(0, p) for _, p in sorted_machines)
            
            for machine_type, profit_per_hour in sorted_machines:
                if profit_per_hour <= 0:
                    continue  # Skip unprofitable machines
                
                power_per_unit = machine_power[machine_type]
                max_units = remaining_power // power_per_unit
                
                if max_units > 0:
                    # Allocate based on profitability ratio with some minimum/maximum bounds
                    profit_ratio = profit_per_hour / total_profit if total_profit > 0 else 0
                    
                    # Scale allocation based on profitability, but with reasonable bounds
                    if machine_type == sorted_machines[0][0]:  # Most profitable
                        allocation_factor = min(0.9, max(0.4, 0.3 + profit_ratio * 1.5))
                    else:
                        allocation_factor = min(0.7, max(0.1, profit_ratio * 2.0))
                    
                    units_to_allocate = min(max_units, max(1, int(max_units * allocation_factor)))
                    
                    optimal_allocation[machine_type] = units_to_allocate
                    remaining_power -= units_to_allocate * power_per_unit
                    
                    print(f"Allocated {units_to_allocate} {machine_type} (${profit_per_hour:.2f}/hr each, {allocation_factor:.1%} of capacity)")
            
            # Make API call to set optimal allocation
            response = requests.put(
                f"{MARA_API_BASE}/machines",
                headers={"X-Api-Key": api_key},
                json=optimal_allocation,
                timeout=10
            )
            
            print(f"Optimization result: {optimal_allocation}")
            return response.status_code == 200
            
        except Exception as e:
            print(f"Error optimizing machines: {e}")
            return False

    def allocate_random_machines(self, api_key: str, max_power: int) -> bool:
        """Fallback: Allocate random machines to a site within power constraints"""
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
    
    def auto_optimize_all_sites(self):
        """Automatically re-optimize all sites based on current market conditions"""
        print(f"\n🔄 AUTO-OPTIMIZATION STARTED at {datetime.now().strftime('%H:%M:%S')}")
        
        # Fetch latest market data
        self.fetch_prices()
        
        if not self.current_prices:
            print("❌ No price data available for optimization")
            return
        
        optimized_count = 0
        for site in self.sites:
            if site.api_key and site.power > 0:
                print(f"\n🔧 Re-optimizing {site.name} at ({site.lat:.4f}, {site.lng:.4f})...")
                success = self.optimize_machine_allocation(site.api_key, site.power, site.lat, site.lng)
                
                if success:
                    # Update site's machine data
                    machine_data = self.get_site_machines(site.api_key)
                    if machine_data:
                        site.machines = machine_data
                        optimized_count += 1
                        
                        # Calculate total profit for this site
                        total_revenue = machine_data.get('total_revenue', 0)
                        print(f"✅ {site.name} optimized - Revenue: ${total_revenue:,.2f}")
                else:
                    print(f"⚠️ Failed to optimize {site.name}")
                
                # Small delay between optimizations
                time.sleep(0.2)
        
        print(f"\n🎯 AUTO-OPTIMIZATION COMPLETE: {optimized_count}/{len([s for s in self.sites if s.api_key])} sites optimized")
        print("=" * 60)

    def start_auto_optimization(self):
        """Start background thread for auto-optimization every 5 minutes"""
        def optimization_loop():
            while True:
                try:
                    time.sleep(300)  # Wait 5 minutes (300 seconds)
                    self.auto_optimize_all_sites()
                except Exception as e:
                    print(f"❌ Error in auto-optimization: {e}")
                    time.sleep(60)  # Wait 1 minute before retrying
        
        # Start the background thread
        optimization_thread = threading.Thread(target=optimization_loop, daemon=True)
        optimization_thread.start()
        print("🚀 Auto-optimization thread started (every 5 minutes)")

    def generate_sites(self, count: int = 50):
        """Generate the specified number of sites"""
        print(f"Generating {count} sites...")
        
        # Fetch initial market data for optimization
        self.fetch_prices()
        self.fetch_inventory()
        
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
                
                # Allocate optimal machines to the site based on location
                if site.api_key and site.power > 0:
                    self.optimize_machine_allocation(site.api_key, site.power, lat, lng)
                    
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
        # Get location modifiers for this site
        location_modifiers = site_manager.get_location_modifiers(site.lat, site.lng)
        
        site_dict = {
            'id': site.id,
            'name': site.name,
            'lat': site.lat,
            'lng': site.lng,
            'power': site.power,
            'machines': site.machines,
            'location_modifiers': location_modifiers,
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
    
    # Calculate total revenue across all sites
    total_revenue = 0
    for site in site_manager.sites:
        if site.machines and site.machines.get('total_revenue'):
            total_revenue += site.machines['total_revenue']
    
    return jsonify({
        'total_sites': total_sites,
        'active_sites': active_sites,
        'total_power': total_power,
        'total_revenue': total_revenue,
        'api_connected': active_sites > 0
    })

@app.route('/api/optimize', methods=['POST'])
def manual_optimize():
    """Manually trigger optimization of all sites"""
    site_manager.auto_optimize_all_sites()
    return jsonify({'message': 'Optimization triggered successfully'})

@app.route('/api/profitability', methods=['GET'])
def get_profitability():
    """Get current machine profitability analysis"""
    site_manager.fetch_prices()
    profitability = site_manager.calculate_machine_profitability(lat=None, lng=None)
    return jsonify(profitability)

@app.route('/api/sites/<int:site_id>/profitability', methods=['GET'])
def get_site_profitability(site_id):
    """Get profitability analysis for a specific site"""
    site = next((s for s in site_manager.sites if s.id == site_id), None)
    if not site:
        return jsonify({'error': 'Site not found'}), 404
    
    # Calculate detailed profitability for this site's location
    profitability_data = site_manager.get_detailed_profitability(site.lat, site.lng)
    
    return jsonify(profitability_data)

@app.route('/api/simulate-event', methods=['POST'])
def simulate_event():
    """Simulate a weather/disaster event"""
    data = request.get_json()
    if not data or 'description' not in data:
        return jsonify({'error': 'Event description required'}), 400
    
    result = site_manager.simulate_event(data['description'])
    return jsonify(result)

@app.route('/api/events', methods=['GET'])
def get_active_events():
    """Get all currently active events"""
    return jsonify(site_manager.active_events)

@app.route('/api/events/<event_id>', methods=['DELETE'])
def clear_event(event_id):
    """Clear a specific event"""
    success = site_manager.clear_event(event_id)
    if success:
        return jsonify({'message': f'Event {event_id} cleared successfully'})
    else:
        return jsonify({'error': 'Event not found'}), 404

if __name__ == '__main__':
    print("Starting MARA Site Manager...")
    
    # Generate initial sites
    site_manager.generate_sites(5)
    
    # Fetch initial market data
    site_manager.fetch_prices()
    site_manager.fetch_inventory()
    
    # Start auto-optimization background thread
    site_manager.start_auto_optimization()
    
    print("Server ready!")
    app.run(debug=True, port=5001)
