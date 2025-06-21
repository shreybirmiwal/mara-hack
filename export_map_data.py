#!/usr/bin/env python3
"""
Export MARA site data and optimization results for React app visualization
"""

import json
from optimize import LocalOptimizer

def get_site_coordinates():
    """Get latitude and longitude for each site"""
    return {
        "BoiseID": {"lat": 43.6150, "lng": -116.2023},
        "MassenaNY": {"lat": 44.9278, "lng": -74.8902},
        "KnoxvilleTN": {"lat": 35.9606, "lng": -83.9207},
        "MassillonOH": {"lat": 40.7967, "lng": -81.5215},
        "MuskogeeOK": {"lat": 35.7479, "lng": -95.3697},
        "ButteMT": {"lat": 46.0038, "lng": -112.5348},
        "SandersvilleGA": {"lat": 32.9801, "lng": -82.8004},
        "CheyenneWY": {"lat": 41.1400, "lng": -104.8197},
        "KearneyNE": {"lat": 40.6994, "lng": -99.0816},
        "RockdaleTX": {"lat": 30.6527, "lng": -97.0131}
    }

def export_map_data():
    """Export all site data for map visualization"""
    optimizer = LocalOptimizer()
    
    # Get latest price data
    price = optimizer.load_latest_price()
    if not price:
        print("❌ No price data available. Run 'python fetch_prices.py' first.")
        return
    
    # Get coordinates
    coordinates = get_site_coordinates()
    
    # Calculate optimizations for all sites
    results = []
    for site_name, site in optimizer.sites.items():
        config, performance = optimizer.calculate_optimal_configuration(site, price)
        
        # Get coordinates for this site
        coords = coordinates.get(site_name, {"lat": 0, "lng": 0})
        
        site_data = {
            "id": site_name,
            "name": site.name,
            "location": site.location,
            "coordinates": coords,
            "geographic_profile": site.geographic_profile,
            "water_availability": site.water_availability,
            "climate_factor": site.climate_factor,
            "infrastructure": site.infrastructure,
            "electricity_multiplier": site.electricity_multiplier,
            "electricity_cost_per_mwh": site.electricity_multiplier * 100,
            "power_limit": site.power_limit,
            "optimization": {
                "net_profit": performance["net_profit"],
                "efficiency": performance["efficiency"],
                "power_used": performance["power_used"],
                "total_revenue": performance["total_revenue"],
                "total_cost": performance["total_cost"]
            },
            "machine_allocation": {
                "air_miners": config.air_miners,
                "hydro_miners": config.hydro_miners,
                "immersion_miners": config.immersion_miners,
                "gpu_compute": config.gpu_compute,
                "asic_compute": config.asic_compute
            },
            "inventory_limits": performance["inventory_limits"],
            "geographic_efficiency": performance["geographic_factors"]
        }
        results.append(site_data)
    
    # Sort by profit (best first)
    results.sort(key=lambda x: x["optimization"]["net_profit"], reverse=True)
    
    # Export metadata
    export_data = {
        "timestamp": price.timestamp,
        "current_prices": {
            "energy": price.energy_price,
            "hash": price.hash_price,
            "token": price.token_price
        },
        "total_sites": len(results),
        "total_profit": sum(r["optimization"]["net_profit"] for r in results),
        "sites": results
    }
    
    # Write to JSON file
    with open('public/site_data.json', 'w') as f:
        json.dump(export_data, f, indent=2)
    
    print(f"✅ Exported data for {len(results)} sites to public/site_data.json")
    print(f"📊 Total profit: ${export_data['total_profit']:,.0f}")
    print(f"🏆 Best site: {results[0]['name']} (${results[0]['optimization']['net_profit']:,.0f})")
    print(f"📉 Worst site: {results[-1]['name']} (${results[-1]['optimization']['net_profit']:,.0f})")

if __name__ == "__main__":
    export_map_data() 