#!/usr/bin/env python3
"""
Reset Database and Start Fresh with 10 Sites
"""

import os
import sqlite3
from main import MaraSiteManager

def reset_database():
    """Remove existing database to start fresh"""
    if os.path.exists('mara_data.db'):
        os.remove('mara_data.db')
        print("✅ Cleared existing database")
    else:
        print("✅ No existing database found")

def main():
    print("🚀 MARA Hackathon - 10 Site Setup")
    print("=" * 50)
    
    # Reset database
    reset_database()
    
    # Create fresh manager
    manager = MaraSiteManager()
    
    print("\n📍 Creating 10 mining sites...")
    
    sites_to_create = [
        ("RockdaleTX", "Rockdale, Texas"),
        ("CheyenneWY", "Cheyenne, Wyoming"),
        ("ButteMT", "Butte, Montana"),
        ("MassenaNY", "Massena, New York"),
        ("SandersvilleGA", "Sandersville, Georgia"),
        ("KnoxvilleTN", "Knoxville, Tennessee"),
        ("MuskogeeOK", "Muskogee, Oklahoma"),
        ("KearneyNE", "Kearney, Nebraska"),
        ("MassillonOH", "Massillon, Ohio"),
        ("BoiseID", "Boise, Idaho")
    ]
    
    created_sites = []
    
    for name, location in sites_to_create:
        print(f"\nCreating {name} in {location}...")
        site = manager.create_site(name, location)
        if site:
            created_sites.append(site)
            print(f"✅ {name}: Power limit {site.power_limit:,}, API key: {site.api_key[:20]}...")
        else:
            print(f"❌ Failed to create {name}")
    
    print(f"\n🎉 Successfully created {len(created_sites)}/10 sites!")
    
    # Get initial pricing
    print("\n💰 Fetching current market prices...")
    prices = manager.get_current_prices()
    if prices:
        latest = prices[0]
        print(f"Energy: ${latest.energy_price:.4f} | Hash: ${latest.hash_price:.4f} | Token: ${latest.token_price:.4f}")
    
    # Show inventory
    print("\n⚙️  Available machine types:")
    inventory = manager.get_inventory()
    if inventory:
        print("MINERS:")
        for miner_type, specs in inventory["miners"].items():
            efficiency = specs["hashrate"] / specs["power"]
            print(f"  {miner_type.upper()}: {specs['hashrate']:,} hash, {specs['power']:,} power ({efficiency:.4f} efficiency)")
        
        print("INFERENCE:")
        for compute_type, specs in inventory["inference"].items():
            efficiency = specs["tokens"] / specs["power"]
            print(f"  {compute_type.upper()}: {specs['tokens']:,} tokens, {specs['power']:,} power ({efficiency:.4f} efficiency)")
    
    # Run initial optimization
    print("\n🧠 Running initial optimization...")
    manager.optimize_all_sites()
    
    # Show results
    print("\n📊 Initial Performance Summary:")
    summary = manager.get_performance_summary()
    
    total_profit = 0
    total_power = 0
    
    for site_name, metrics in summary.items():
        print(f"{site_name}: ${metrics['profit']:,.2f} profit, {metrics['power_used']:,} power")
        total_profit += metrics['profit']
        total_power += metrics['power_used']
    
    print(f"\n🏆 TOTAL ACROSS ALL SITES:")
    print(f"   Combined Profit: ${total_profit:,.2f}")
    print(f"   Total Power Used: {total_power:,}")
    print(f"   Average Efficiency: {total_profit/total_power:.6f} profit/power")
    
    print(f"\n✨ Setup complete! Your 10-site mining operation is running.")
    print(f"💡 Run 'python main.py' for continuous optimization")
    print(f"🎮 Run 'python manage_sites.py' for interactive management")
    
    manager.close()

if __name__ == "__main__":
    main() 