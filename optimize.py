#!/usr/bin/env python3
"""
MARA Local Optimizer
Optimize mining configurations using local price data without any API calls
"""

import csv
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

class LocalOptimizer:
    def __init__(self):
        self.pricing_csv = "mara_pricing_history.csv"
        
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
        
        self.sites = {}
        for name, location, electricity_multiplier, water_avail, climate, infra, profile in sites_data:
            self.sites[name] = Site(
                name=name,
                location=location,
                electricity_multiplier=electricity_multiplier,
                water_availability=water_avail,
                climate_factor=climate,
                infrastructure=infra,
                geographic_profile=profile
            )
        
        # Static inventory data with geographic efficiency modifiers
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
    
    def load_latest_price(self) -> Optional[PricingData]:
        """Load the most recent price from CSV"""
        if not os.path.exists(self.pricing_csv):
            print(f"❌ No price data found. Run 'python fetch_prices.py' first.")
            return None
        
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
        
        if not prices:
            return None
        
        # Sort by timestamp and return latest
        prices.sort(key=lambda x: x.timestamp, reverse=True)
        return prices[0]
    
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

    def calculate_optimal_configuration(self, site: Site, price: PricingData) -> tuple[MachineConfig, dict]:
        """Calculate optimal machine configuration for a site with geographic factors"""
        
        # Get realistic inventory limits for this site
        inventory_limits = self.get_machine_inventory_limits(site)
        
        # Calculate profitability per power unit for each machine type
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
        total_revenue = 0
        total_cost = 0
        geo_factors = {}
        
        for machine_type, profit in sorted_machines:
            if remaining_power <= 0 or profit <= 0:
                break
            
            # Check inventory limit
            max_available = inventory_limits[machine_type]
            if max_available == 0:
                continue
            
            # Store geographic efficiency for reporting
            geo_efficiency = self.get_geographic_efficiency(site, machine_type)
            geo_factors[machine_type] = geo_efficiency
            
            if machine_type.endswith("_miners"):
                machine_name = machine_type.replace("_miners", "")
                specs = self.inventory["miners"][machine_name]
                effective_hashrate = specs["hashrate"] * geo_efficiency
                revenue_per_machine = effective_hashrate * price.hash_price
                power_per_machine = specs["power"]
            else:
                machine_name = machine_type.replace("_compute", "")
                specs = self.inventory["inference"][machine_name]
                effective_tokens = specs["tokens"] * geo_efficiency
                revenue_per_machine = effective_tokens * price.token_price
                power_per_machine = specs["power"]
            
            cost_per_machine = power_per_machine * site_energy_cost
            
            # Calculate how many we can deploy (limited by power AND inventory)
            max_by_power = remaining_power // power_per_machine
            max_machines = min(max_by_power, max_available)
            
            if max_machines > 0:
                setattr(config, machine_type, max_machines)
                remaining_power -= max_machines * power_per_machine
                total_revenue += max_machines * revenue_per_machine
                total_cost += max_machines * cost_per_machine
        
        performance = {
            "total_revenue": total_revenue,
            "total_cost": total_cost,
            "net_profit": total_revenue - total_cost,
            "power_used": site.power_limit - remaining_power,
            "efficiency": (total_revenue - total_cost) / (site.power_limit - remaining_power) if remaining_power < site.power_limit else 0,
            "profitability_ranking": sorted_machines,
            "geographic_factors": geo_factors,
            "inventory_limits": inventory_limits
        }
        
        return config, performance
    
    def optimize_all_sites(self):
        """Calculate optimal configurations for all sites"""
        price = self.load_latest_price()
        if not price:
            return
        
        print("🧠 MARA GEOGRAPHIC OPTIMIZER")
        print("=" * 70)
        print(f"Latest Price Data: {price.timestamp}")
        print(f"Energy: ${price.energy_price:.4f} | Hash: ${price.hash_price:.4f} | Token: ${price.token_price:.4f}")
        print()
        
        results = []
        
        for site_name, site in self.sites.items():
            config, performance = self.calculate_optimal_configuration(site, price)
            results.append((site, config, performance))
        
        # Sort by profit (best first)
        results.sort(key=lambda x: x[2]["net_profit"], reverse=True)
        
        print("🏆 GEOGRAPHICALLY OPTIMIZED CONFIGURATIONS")
        print("-" * 70)
        
        total_profit = 0
        for i, (site, config, perf) in enumerate(results, 1):
            total_profit += perf["net_profit"]
            
            print(f"\n{i}. {site.name} ({site.location})")
            print(f"   Profile: {site.geographic_profile.replace('_', ' ').title()}")
            print(f"   Water: {site.water_availability:.0%} | Climate: {site.climate_factor:.0%} | Infrastructure: {site.infrastructure:.0%}")
            print(f"   Electricity Cost: {site.electricity_multiplier:.1f}x")
            print(f"   Net Profit: ${perf['net_profit']:,.0f}")
            print(f"   Efficiency: {perf['efficiency']:.4f} profit/power")
            
            # Show available inventory
            limits = perf['inventory_limits']
            print(f"   Available Inventory: {limits['air_miners']} Air, {limits['hydro_miners']} Hydro, "
                  f"{limits['immersion_miners']} Immersion, {limits['gpu_compute']} GPU, {limits['asic_compute']} ASIC")
            
            # Show machine allocation with geographic efficiency
            machines = []
            geo_info = []
            if config.air_miners > 0:
                geo_eff = perf['geographic_factors'].get('air_miners', 1.0)
                machines.append(f"{config.air_miners} Air Miners")
                geo_info.append(f"Air: {geo_eff:.0%} efficiency")
            if config.hydro_miners > 0:
                geo_eff = perf['geographic_factors'].get('hydro_miners', 1.0)
                machines.append(f"{config.hydro_miners} Hydro Miners")
                geo_info.append(f"Hydro: {geo_eff:.0%} efficiency")
            if config.immersion_miners > 0:
                geo_eff = perf['geographic_factors'].get('immersion_miners', 1.0)
                machines.append(f"{config.immersion_miners} Immersion Miners")
                geo_info.append(f"Immersion: {geo_eff:.0%} efficiency")
            if config.gpu_compute > 0:
                geo_eff = perf['geographic_factors'].get('gpu_compute', 1.0)
                machines.append(f"{config.gpu_compute} GPU Compute")
                geo_info.append(f"GPU: {geo_eff:.0%} efficiency")
            if config.asic_compute > 0:
                geo_eff = perf['geographic_factors'].get('asic_compute', 1.0)
                machines.append(f"{config.asic_compute} ASIC Compute")
                geo_info.append(f"ASIC: {geo_eff:.0%} efficiency")
            
            if machines:
                print(f"   Allocation: {', '.join(machines)}")
                print(f"   Geographic Efficiency: {' | '.join(geo_info)}")
            else:
                print(f"   Allocation: Unprofitable - No machines deployed")
        
        print(f"\n🎯 TOTAL PROFIT ACROSS ALL SITES: ${total_profit:,.0f}")
        
        # Show best strategy
        best_site, best_config, best_perf = results[0]
        worst_site, worst_config, worst_perf = results[-1]
        
        profit_difference = best_perf["net_profit"] - worst_perf["net_profit"]
        
        print(f"\n📊 GEOGRAPHIC INSIGHTS:")
        print(f"   Best Location: {best_site.name} (${best_perf['net_profit']:,.0f} profit)")
        print(f"   Worst Location: {worst_site.name} (${worst_perf['net_profit']:,.0f} profit)")
        print(f"   Geographic Advantage: ${profit_difference:,.0f}")
        
        # Show geographic optimization summary
        hydro_sites = [s for s, c, p in results if c.hydro_miners > 0]
        air_sites = [s for s, c, p in results if c.air_miners > 0]
        immersion_sites = [s for s, c, p in results if c.immersion_miners > 0]
        
        print(f"\n🌍 GEOGRAPHIC DISTRIBUTION:")
        if hydro_sites:
            print(f"   Hydro-Optimized Sites: {', '.join([s.name for s in hydro_sites])}")
        if air_sites:
            print(f"   Air-Optimized Sites: {', '.join([s.name for s in air_sites])}")
        if immersion_sites:
            print(f"   Immersion Sites: {', '.join([s.name for s in immersion_sites])}")
        
        return results
    
    def export_configurations(self, results, filename="optimal_configs.csv"):
        """Export optimal configurations to CSV"""
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'rank', 'site_name', 'location', 'electricity_multiplier',
                'net_profit', 'efficiency', 'power_used',
                'air_miners', 'hydro_miners', 'immersion_miners', 'gpu_compute', 'asic_compute'
            ])
            
            for i, (site, config, perf) in enumerate(results, 1):
                writer.writerow([
                    i, site.name, site.location, site.electricity_multiplier,
                    perf['net_profit'], perf['efficiency'], perf['power_used'],
                    config.air_miners, config.hydro_miners, config.immersion_miners,
                    config.gpu_compute, config.asic_compute
                ])
        
        print(f"✅ Configurations exported to {filename}")

def main():
    optimizer = LocalOptimizer()
    
    while True:
        print("\n🚀 MARA Local Optimizer")
        print("-" * 30)
        print("1. Optimize all sites")
        print("2. Show electricity costs")
        print("3. Export configurations")
        print("4. Exit")
        
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == "1":
            results = optimizer.optimize_all_sites()
            
        elif choice == "2":
            print("\n🌍 GEOGRAPHIC FACTORS COMPARISON")
            print("-" * 80)
            print(f"{'Site':<15} {'Location':<25} {'Profile':<18} {'Water':<6} {'Climate':<8} {'Infra':<6}")
            print("-" * 80)
            for site_name, site in sorted(optimizer.sites.items(), 
                                        key=lambda x: x[1].electricity_multiplier):
                profile = site.geographic_profile.replace('_', ' ').title()
                print(f"{site_name:<15} {site.location:<25} {profile:<18} "
                      f"{site.water_availability:<6.0%} {site.climate_factor:<8.0%} {site.infrastructure:<6.0%}")
        
        elif choice == "3":
            price = optimizer.load_latest_price()
            if price:
                results = []
                for site_name, site in optimizer.sites.items():
                    config, performance = optimizer.calculate_optimal_configuration(site, price)
                    results.append((site, config, performance))
                results.sort(key=lambda x: x[2]["net_profit"], reverse=True)
                optimizer.export_configurations(results)
            else:
                print("No price data available for export")
                
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid option")

if __name__ == "__main__":
    main() 