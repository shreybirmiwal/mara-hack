#!/usr/bin/env python3
"""
MARA Historical Simulation
Replay optimization decisions using historical price data without API calls
"""

import csv
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class Site:
    name: str
    location: str
    electricity_multiplier: float = 1.0
    power_limit: int = 1000000
    # Geographic factors (0.0 to 1.0 representing suitability)
    water_availability: float = 1.0  # For hydro and immersion miners
    climate_factor: float = 1.0      # Air cooling efficiency
    infrastructure: float = 1.0      # For compute/inference
    geographic_profile: str = "balanced"

@dataclass
class PricingData:
    timestamp: str
    energy_price: float
    hash_price: float
    token_price: float

@dataclass
class MachineConfig:
    air_miners: int = 0
    hydro_miners: int = 0
    immersion_miners: int = 0
    gpu_compute: int = 0
    asic_compute: int = 0

class HistoricalSimulator:
    def __init__(self):
        self.pricing_csv = "mara_pricing_history.csv"
        self.sites: Dict[str, Site] = {}
        
        # Initialize sites with regional electricity costs AND geographic factors
        sites_data = [
            # (name, location, elec_mult, water_avail, climate, infra, profile)
            ("BoiseID", "Boise, Idaho", 0.8, 0.95, 0.8, 0.7, "hydro_optimal"),
            ("MassenaNY", "Massena, New York", 1.5, 0.98, 0.9, 0.8, "hydro_optimal"),  
            ("KnoxvilleTN", "Knoxville, Tennessee", 1.0, 0.85, 0.7, 0.8, "hydro_preferred"),
            ("MassillonOH", "Massillon, Ohio", 1.2, 0.80, 0.75, 0.85, "mixed_hydro"),
            ("MuskogeeOK", "Muskogee, Oklahoma", 0.9, 0.65, 0.6, 0.7, "mixed_balanced"),
            ("ButteMT", "Butte, Montana", 1.1, 0.45, 0.85, 0.6, "air_preferred"),
            ("SandersvilleGA", "Sandersville, Georgia", 1.1, 0.40, 0.5, 0.75, "air_immersion"),
            ("CheyenneWY", "Cheyenne, Wyoming", 1.0, 0.25, 0.95, 0.65, "air_optimal"),
            ("KearneyNE", "Kearney, Nebraska", 1.0, 0.30, 0.90, 0.7, "air_optimal"),
            ("RockdaleTX", "Rockdale, Texas", 1.2, 0.35, 0.85, 0.8, "air_compute"),
        ]
        
        # Create sites for simulation
        for name, location, electricity_multiplier, water_avail, climate, infra, profile in sites_data:
            self.sites[name] = Site(
                name=name,
                location=location,
                electricity_multiplier=electricity_multiplier,
                water_availability=water_avail,
                climate_factor=climate,
                infrastructure=infra,
                geographic_profile=profile,
                power_limit=1000000
            )
        
        # Cache inventory data (static) with geographic efficiency modifiers
        self.inventory = {
            "miners": {
                "air": {"hashrate": 1000, "power": 3333, "climate_dependent": True},
                "hydro": {"hashrate": 10000, "power": 5000, "water_dependent": True},
                "immersion": {"hashrate": 5000, "power": 10000, "water_dependent": True}
            },
            "inference": {
                "gpu": {"tokens": 1000, "power": 3333, "infrastructure_dependent": True},
                "asic": {"tokens": 5000, "power": 10000, "infrastructure_dependent": True}
            }
        }
    
    def get_geographic_efficiency(self, site: Site, machine_type: str) -> float:
        """Calculate efficiency modifier based on geographic factors"""
        base_efficiency = 1.0
        
        if machine_type == "air_miners":
            # Air cooling is more efficient in dry, cool climates
            return base_efficiency * site.climate_factor
        
        elif machine_type == "hydro_miners":
            # Hydro miners need good water access and moderate climate
            return base_efficiency * site.water_availability * (0.7 + 0.3 * site.climate_factor)
        
        elif machine_type == "immersion_miners":
            # Immersion miners need water access but work well in hot climates
            return base_efficiency * site.water_availability * (1.2 - 0.2 * site.climate_factor)
        
        elif machine_type in ["gpu_compute", "asic_compute"]:
            # Compute depends on infrastructure and moderate climate
            return base_efficiency * site.infrastructure * (0.8 + 0.2 * site.climate_factor)
        
        return base_efficiency
    
    def get_machine_inventory_limits(self, site: Site) -> Dict[str, int]:
        """Get realistic machine inventory limits based on geographic factors"""
        base_power = site.power_limit
        
        # Calculate maximum machines based on power alone
        max_air = base_power // self.inventory["miners"]["air"]["power"]
        max_hydro = base_power // self.inventory["miners"]["hydro"]["power"] 
        max_immersion = base_power // self.inventory["miners"]["immersion"]["power"]
        max_gpu = base_power // self.inventory["inference"]["gpu"]["power"]
        max_asic = base_power // self.inventory["inference"]["asic"]["power"]
        
        # Apply geographic constraints
        inventory_limits = {}
        
        # Hydro miners - heavily constrained by water availability
        if site.water_availability >= 0.9:  # Excellent water access
            inventory_limits["hydro_miners"] = int(max_hydro * 0.8)  # Up to 80% of theoretical max
        elif site.water_availability >= 0.7:  # Good water access  
            inventory_limits["hydro_miners"] = int(max_hydro * 0.5)  # Up to 50%
        elif site.water_availability >= 0.5:  # Moderate water access
            inventory_limits["hydro_miners"] = int(max_hydro * 0.2)  # Up to 20%
        elif site.water_availability >= 0.3:  # Limited water access
            inventory_limits["hydro_miners"] = int(max_hydro * 0.05)  # Up to 5%
        else:  # Very limited water access
            inventory_limits["hydro_miners"] = 0  # No hydro miners available
        
        # Air miners - constrained by climate (work better in dry, cool climates)
        if site.climate_factor >= 0.8:  # Excellent for air cooling
            inventory_limits["air_miners"] = max_air  # Full capacity
        elif site.climate_factor >= 0.6:  # Good for air cooling
            inventory_limits["air_miners"] = int(max_air * 0.8)
        elif site.climate_factor >= 0.4:  # Moderate for air cooling
            inventory_limits["air_miners"] = int(max_air * 0.5)
        else:  # Poor for air cooling
            inventory_limits["air_miners"] = int(max_air * 0.2)
        
        # Immersion miners - need some water but work in hot climates
        if site.water_availability >= 0.4:  # Need minimum water access
            if site.climate_factor <= 0.6:  # Work better in hot climates
                inventory_limits["immersion_miners"] = int(max_immersion * 0.6)
            else:
                inventory_limits["immersion_miners"] = int(max_immersion * 0.3)
        else:
            inventory_limits["immersion_miners"] = 0  # No water, no immersion
        
        # GPU compute - depends on infrastructure
        if site.infrastructure >= 0.8:  # Excellent infrastructure
            inventory_limits["gpu_compute"] = int(max_gpu * 0.7)
        elif site.infrastructure >= 0.6:  # Good infrastructure
            inventory_limits["gpu_compute"] = int(max_gpu * 0.4)
        else:  # Limited infrastructure
            inventory_limits["gpu_compute"] = int(max_gpu * 0.1)
        
        # ASIC compute - more forgiving infrastructure requirements
        if site.infrastructure >= 0.6:  # Good infrastructure
            inventory_limits["asic_compute"] = int(max_asic * 0.5)
        else:  # Limited infrastructure
            inventory_limits["asic_compute"] = int(max_asic * 0.2)
        
        return inventory_limits
    
    def load_historical_prices(self) -> List[PricingData]:
        """Load historical pricing data from CSV"""
        if not os.path.exists(self.pricing_csv):
            print(f"❌ No historical data found at {self.pricing_csv}")
            print("Run the main application first to collect price data.")
            return []
        
        prices = []
        with open(self.pricing_csv, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                prices.append(PricingData(
                    timestamp=row['timestamp'],
                    energy_price=float(row['energy_price']),
                    hash_price=float(row['hash_price']),
                    token_price=float(row['token_price'])
                ))
        
        # Sort by timestamp (oldest first for simulation)
        prices.sort(key=lambda x: x.timestamp)
        return prices
    
    def calculate_optimal_configuration(self, site_name: str, price: PricingData) -> Optional[MachineConfig]:
        """Calculate optimal machine configuration for a site at a specific price point"""
        if site_name not in self.sites:
            return None
        
        site = self.sites[site_name]
        
        # Get realistic inventory limits for this site
        inventory_limits = self.get_machine_inventory_limits(site)
        
        # Calculate profitability per power unit for each machine type
        # Use site-specific electricity multiplier
        profitability = {}
        site_energy_cost = price.energy_price * site.electricity_multiplier
        
        # Miners (generate hash, consume power)
        for miner_type, specs in self.inventory["miners"].items():
            machine_type = f"{miner_type}_miners"
            if inventory_limits[machine_type] == 0:
                continue  # Skip if no inventory available
                
            hashrate = specs["hashrate"]
            power = specs["power"]
            
            # Apply geographic efficiency modifier
            geo_efficiency = self.get_geographic_efficiency(site, machine_type)
            effective_hashrate = hashrate * geo_efficiency
            
            revenue_per_hour = effective_hashrate * price.hash_price
            cost_per_hour = power * site_energy_cost
            profit_per_power = (revenue_per_hour - cost_per_hour) / power if power > 0 else 0
            profitability[machine_type] = profit_per_power
        
        # Inference machines (generate tokens, consume power)
        for compute_type, specs in self.inventory["inference"].items():
            machine_type = f"{compute_type}_compute"
            if inventory_limits[machine_type] == 0:
                continue  # Skip if no inventory available
                
            tokens = specs["tokens"]
            power = specs["power"]
            
            # Apply geographic efficiency modifier
            geo_efficiency = self.get_geographic_efficiency(site, machine_type)
            effective_tokens = tokens * geo_efficiency
            
            revenue_per_hour = effective_tokens * price.token_price
            cost_per_hour = power * site_energy_cost
            profit_per_power = (revenue_per_hour - cost_per_hour) / power if power > 0 else 0
            profitability[machine_type] = profit_per_power
        
        # Sort by profitability
        sorted_machines = sorted(profitability.items(), key=lambda x: x[1], reverse=True)
        
        # Allocate power to most profitable machines first, respecting inventory limits
        config = MachineConfig()
        remaining_power = site.power_limit
        
        for machine_type, profit in sorted_machines:
            if remaining_power <= 0 or profit <= 0:
                break
            
            # Check inventory limit
            max_available = inventory_limits[machine_type]
            if max_available == 0:
                continue
            
            if machine_type.endswith("_miners"):
                machine_name = machine_type.replace("_miners", "")
                machine_power = self.inventory["miners"][machine_name]["power"]
            else:
                machine_name = machine_type.replace("_compute", "")
                machine_power = self.inventory["inference"][machine_name]["power"]
            
            # Calculate how many we can deploy (limited by power AND inventory)
            max_by_power = remaining_power // machine_power
            max_machines = min(max_by_power, max_available)
            
            if max_machines > 0:
                setattr(config, machine_type, max_machines)
                remaining_power -= max_machines * machine_power
        
        return config
    
    def run_simulation(self, start_index: int = 0, end_index: Optional[int] = None, step: int = 1):
        """Run historical simulation"""
        prices = self.load_historical_prices()
        
        if not prices:
            return
        
        if end_index is None:
            end_index = len(prices)
        
        print(f"🎬 HISTORICAL SIMULATION")
        print("=" * 80)
        print(f"Price data points: {len(prices)}")
        print(f"Simulation range: {start_index} to {end_index} (step: {step})")
        print(f"Time period: {prices[start_index].timestamp} to {prices[end_index-1].timestamp}")
        print()
        
        print(f"{'Time':<20} {'Energy':<8} {'Hash':<8} {'Token':<8} {'Best Site':<12} {'Total Profit':<15}")
        print("-" * 80)
        
        for i in range(start_index, end_index, step):
            price = prices[i]
            timestamp = price.timestamp.split('T')[1][:5]  # Extract time portion
            
            # Find best site for this price point
            best_site = None
            best_profit = -float('inf')
            total_profit = 0
            
            for site_name in self.sites:
                config = self.calculate_optimal_configuration(site_name, price)
                if config:
                    # Calculate profit for this site
                    site = self.sites[site_name]
                    site_energy_cost = price.energy_price * site.electricity_multiplier
                    
                    profit = 0
                    # Calculate total profit for this configuration
                    machine_counts = {
                        "air_miners": config.air_miners,
                        "hydro_miners": config.hydro_miners,
                        "immersion_miners": config.immersion_miners,
                        "gpu_compute": config.gpu_compute,
                        "asic_compute": config.asic_compute
                    }
                    
                    for machine_type, count in machine_counts.items():
                        if count == 0:
                            continue
                        
                        if machine_type.endswith("_miners"):
                            machine_name = machine_type.replace("_miners", "")
                            specs = self.inventory["miners"][machine_name]
                            geo_efficiency = self.get_geographic_efficiency(site, machine_type)
                            effective_hashrate = specs["hashrate"] * geo_efficiency
                            revenue_per_machine = effective_hashrate * price.hash_price
                        else:
                            machine_name = machine_type.replace("_compute", "")
                            specs = self.inventory["inference"][machine_name]
                            geo_efficiency = self.get_geographic_efficiency(site, machine_type)
                            effective_tokens = specs["tokens"] * geo_efficiency
                            revenue_per_machine = effective_tokens * price.token_price
                        
                        power_per_machine = specs["power"]
                        cost_per_machine = power_per_machine * site_energy_cost
                        profit_per_machine = revenue_per_machine - cost_per_machine
                        
                        profit += count * profit_per_machine
                    
                    total_profit += max(0, profit)  # Only count profitable sites
                    
                    if profit > best_profit:
                        best_profit = profit
                        best_site = site_name
            
            print(f"{timestamp:<20} ${price.energy_price:<7.3f} ${price.hash_price:<7.3f} ${price.token_price:<7.3f} "
                  f"{best_site or 'None':<12} ${total_profit:>14,.0f}")

def main():
    simulator = HistoricalSimulator()
    
    print("🎬 MARA Historical Simulation")
    print("=" * 50)
    
    while True:
        print("\nOptions:")
        print("1. Run full simulation")
        print("2. Run recent simulation (last 20 data points)")
        print("3. Show electricity cost comparison")
        print("4. Exit")
        
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == "1":
            simulator.run_simulation()
                
        elif choice == "2":
            simulator.run_simulation(start_index=-20)
                
        elif choice == "3":
            print("\n🌍 GEOGRAPHIC FACTORS COMPARISON")
            print("-" * 80)
            print(f"{'Site':<15} {'Location':<25} {'Profile':<18} {'Water':<6} {'Climate':<8} {'Infra':<6}")
            print("-" * 80)
            for site_name, site in sorted(simulator.sites.items(), 
                                        key=lambda x: x[1].electricity_multiplier):
                profile = site.geographic_profile.replace('_', ' ').title()
                print(f"{site_name:<15} {site.location:<25} {profile:<18} "
                      f"{site.water_availability:<6.0%} {site.climate_factor:<8.0%} {site.infrastructure:<6.0%}")
            
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid option")

if __name__ == "__main__":
    main() 