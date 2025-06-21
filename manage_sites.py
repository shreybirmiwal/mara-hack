#!/usr/bin/env python3
"""
MARA Site Management Utility
Interactive script for managing mining sites and testing configurations
"""

import sys
from main import MaraSiteManager, MachineConfig
import json
import logging

# Set up logging for interactive use
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def print_banner():
    print("=" * 60)
    print("      MARA Hackathon Site Management Utility")
    print("=" * 60)
    print()

def display_menu():
    print("\nAvailable commands:")
    print("1. Create sites")
    print("2. Check current prices")
    print("3. View inventory")
    print("4. Optimize all sites")
    print("5. Show site status")
    print("6. Performance summary")
    print("7. Manual machine allocation")
    print("8. Historical data analysis")
    print("9. Exit")
    print()

def create_sites(manager):
    """Create the three sites"""
    sites_to_create = [
        ("RockdaleTX", "Rockdale, Texas"),
        ("CheyenneWY", "Cheyenne, Wyoming"),
        ("ButteMT", "Butte, Montana")
    ]
    
    print("Creating mining sites...")
    for name, location in sites_to_create:
        if name in manager.sites:
            print(f"Site {name} already exists")
            continue
            
        site = manager.create_site(name, location)
        if site:
            print(f"✓ Created {name} in {location}")
            print(f"  Power Limit: {site.power_limit:,}")
            print(f"  API Key: {site.api_key}")
        else:
            print(f"✗ Failed to create {name}")
    print()

def check_prices(manager):
    """Display current pricing information"""
    print("Fetching current prices...")
    prices = manager.get_current_prices()
    
    if not prices:
        print("No pricing data available")
        return
    
    print(f"\nPricing Data ({len(prices)} records):")
    print("-" * 50)
    
    for i, price in enumerate(prices[:5]):  # Show first 5 records
        print(f"{i+1}. {price.timestamp}")
        print(f"   Energy: ${price.energy_price:.4f}/unit")
        print(f"   Hash:   ${price.hash_price:.4f}/unit")
        print(f"   Token:  ${price.token_price:.4f}/unit")
        print()

def view_inventory(manager):
    """Display inventory information"""
    print("Fetching inventory...")
    inventory = manager.get_inventory()
    
    if not inventory:
        print("No inventory data available")
        return
    
    print("\nInventory Information:")
    print("-" * 30)
    
    print("MINERS:")
    for miner_type, specs in inventory["miners"].items():
        efficiency = specs["hashrate"] / specs["power"]
        print(f"  {miner_type.upper()}")
        print(f"    Hashrate: {specs['hashrate']:,}/unit")
        print(f"    Power:    {specs['power']:,}/unit")
        print(f"    Efficiency: {efficiency:.4f} hash/power")
        print()
    
    print("INFERENCE MACHINES:")
    for compute_type, specs in inventory["inference"].items():
        efficiency = specs["tokens"] / specs["power"]
        print(f"  {compute_type.upper()}")
        print(f"    Tokens: {specs['tokens']:,}/unit")
        print(f"    Power:  {specs['power']:,}/unit")
        print(f"    Efficiency: {efficiency:.4f} tokens/power")
        print()

def show_site_status(manager):
    """Display status for all sites"""
    if not manager.sites:
        print("No sites created yet")
        return
    
    print("\nSite Status:")
    print("-" * 60)
    
    for site_name in manager.sites:
        status = manager.get_site_status(site_name)
        if status:
            site = manager.sites[site_name]
            print(f"\n{site_name} ({site.location}):")
            print(f"  Power: {status['total_power_used']:,}/{site.power_limit:,} "
                  f"({status['total_power_used']/site.power_limit*100:.1f}%)")
            print(f"  Revenue: ${status['total_revenue']:,.2f}")
            print(f"  Cost:    ${status['total_power_cost']:,.2f}")
            print(f"  Profit:  ${status['net_profit']:,.2f}")
            
            # Show machine allocation
            print("  Machines:")
            for machine_type in ['air_miners', 'hydro_miners', 'immersion_miners', 'gpu_compute', 'asic_compute']:
                count = status.get(machine_type, 0)
                if count > 0:
                    print(f"    {machine_type}: {count}")
        else:
            print(f"\n{site_name}: Unable to get status")

def performance_summary(manager):
    """Show performance summary"""
    summary = manager.get_performance_summary()
    
    if not summary:
        print("No performance data available")
        return
    
    print("\nPerformance Summary:")
    print("-" * 80)
    
    total_profit = 0
    total_revenue = 0
    total_cost = 0
    
    for site_name, metrics in summary.items():
        print(f"\n{site_name} ({metrics['location']}):")
        print(f"  Power Usage: {metrics['power_used']:,}/{metrics['power_limit']:,} "
              f"({metrics['power_used']/metrics['power_limit']*100:.1f}%)")
        print(f"  Revenue:     ${metrics['revenue']:,.2f}")
        print(f"  Cost:        ${metrics['cost']:,.2f}")
        print(f"  Profit:      ${metrics['profit']:,.2f}")
        print(f"  Efficiency:  {metrics['efficiency']:.6f} profit/power")
        
        total_profit += metrics['profit']
        total_revenue += metrics['revenue']
        total_cost += metrics['cost']
    
    print(f"\nTOTAL ACROSS ALL SITES:")
    print(f"  Revenue: ${total_revenue:,.2f}")
    print(f"  Cost:    ${total_cost:,.2f}")
    print(f"  Profit:  ${total_profit:,.2f}")

def manual_allocation(manager):
    """Allow manual machine allocation"""
    if not manager.sites:
        print("No sites created yet")
        return
    
    print("\nAvailable sites:")
    for i, site_name in enumerate(manager.sites.keys(), 1):
        print(f"{i}. {site_name}")
    
    try:
        choice = int(input("\nSelect site (number): ")) - 1
        site_names = list(manager.sites.keys())
        
        if 0 <= choice < len(site_names):
            site_name = site_names[choice]
            print(f"\nConfiguring {site_name}:")
            
            config = MachineConfig()
            config.air_miners = int(input("Air miners: ") or "0")
            config.hydro_miners = int(input("Hydro miners: ") or "0")
            config.immersion_miners = int(input("Immersion miners: ") or "0")
            config.gpu_compute = int(input("GPU compute: ") or "0")
            config.asic_compute = int(input("ASIC compute: ") or "0")
            
            if manager.update_site_machines(site_name, config):
                print("✓ Configuration updated successfully")
                
                # Show updated status
                status = manager.get_site_status(site_name)
                if status:
                    print(f"New profit: ${status['net_profit']:,.2f}")
            else:
                print("✗ Failed to update configuration")
        else:
            print("Invalid selection")
            
    except ValueError:
        print("Invalid input")

def historical_analysis(manager):
    """Show historical data analysis"""
    print("Querying historical data...")
    
    cursor = manager.conn.cursor()
    
    # Recent pricing trends
    cursor.execute('''
        SELECT timestamp, energy_price, hash_price, token_price
        FROM pricing_history
        ORDER BY timestamp DESC
        LIMIT 10
    ''')
    
    price_data = cursor.fetchall()
    if price_data:
        print("\nRecent Price Trends:")
        print("-" * 60)
        for row in price_data:
            print(f"{row[0]} | Energy: ${row[1]:.4f} | Hash: ${row[2]:.4f} | Token: ${row[3]:.4f}")
    
    # Site performance history
    cursor.execute('''
        SELECT site_name, AVG(net_profit) as avg_profit, MAX(net_profit) as max_profit, 
               COUNT(*) as records
        FROM site_performance
        GROUP BY site_name
    ''')
    
    perf_data = cursor.fetchall()
    if perf_data:
        print("\nSite Performance History:")
        print("-" * 50)
        for row in perf_data:
            print(f"{row[0]}: Avg Profit: ${row[1]:.2f}, Max: ${row[2]:.2f}, Records: {row[3]}")

def main():
    print_banner()
    
    manager = MaraSiteManager()
    
    try:
        while True:
            display_menu()
            
            try:
                choice = input("Select option (1-9): ").strip()
                
                if choice == "1":
                    create_sites(manager)
                elif choice == "2":
                    check_prices(manager)
                elif choice == "3":
                    view_inventory(manager)
                elif choice == "4":
                    print("Optimizing all sites...")
                    manager.optimize_all_sites()
                    print("✓ Optimization complete")
                elif choice == "5":
                    show_site_status(manager)
                elif choice == "6":
                    performance_summary(manager)
                elif choice == "7":
                    manual_allocation(manager)
                elif choice == "8":
                    historical_analysis(manager)
                elif choice == "9":
                    print("Goodbye!")
                    break
                else:
                    print("Invalid option. Please try again.")
                    
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")
                
    finally:
        manager.close()

if __name__ == "__main__":
    main() 