#!/usr/bin/env python3
"""
View MARA Historical Data
Simple script to display CSV data in readable format
"""

import csv
import os
from datetime import datetime

def view_pricing_data():
    """Display pricing history from CSV"""
    csv_file = "mara_pricing_history.csv"
    
    if not os.path.exists(csv_file):
        print("❌ No pricing data found. Run the application first to collect data.")
        return
    
    print("📊 PRICING HISTORY")
    print("=" * 80)
    
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        data = list(reader)
    
    if not data:
        print("No pricing data available")
        return
    
    print(f"Total records: {len(data)}")
    print(f"First record: {data[0]['timestamp']}")
    print(f"Last record: {data[-1]['timestamp']}")
    print()
    
    # Show recent prices
    print("RECENT PRICES (last 10 records):")
    print("-" * 80)
    print(f"{'Timestamp':<20} {'Energy':<10} {'Hash':<10} {'Token':<10}")
    print("-" * 80)
    
    for row in data[-10:]:
        print(f"{row['timestamp']:<20} ${float(row['energy_price']):<9.4f} ${float(row['hash_price']):<9.4f} ${float(row['token_price']):<9.4f}")
    
    # Calculate price ranges
    energy_prices = [float(row['energy_price']) for row in data]
    hash_prices = [float(row['hash_price']) for row in data]
    token_prices = [float(row['token_price']) for row in data]
    
    print("\nPRICE RANGES:")
    print("-" * 40)
    print(f"Energy: ${min(energy_prices):.4f} - ${max(energy_prices):.4f}")
    print(f"Hash:   ${min(hash_prices):.4f} - ${max(hash_prices):.4f}")  
    print(f"Token:  ${min(token_prices):.4f} - ${max(token_prices):.4f}")

def view_performance_data():
    """Display site performance history from CSV"""
    csv_file = "mara_site_performance.csv"
    
    if not os.path.exists(csv_file):
        print("❌ No performance data found. Run the application first to collect data.")
        return
    
    print("\n\n🏗️ SITE PERFORMANCE HISTORY")
    print("=" * 80)
    
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        data = list(reader)
    
    if not data:
        print("No performance data available")
        return
    
    print(f"Total records: {len(data)}")
    print()
    
    # Group by site
    sites = {}
    for row in data:
        site = row['site_name']
        if site not in sites:
            sites[site] = []
        sites[site].append(row)
    
    # Show summary for each site
    for site_name, records in sites.items():
        profits = [float(r['net_profit']) for r in records]
        revenues = [float(r['total_revenue']) for r in records]
        
        print(f"\n{site_name}:")
        print(f"  Records: {len(records)}")
        print(f"  Latest Profit: ${profits[-1]:,.2f}")
        print(f"  Average Profit: ${sum(profits)/len(profits):,.2f}")
        print(f"  Max Profit: ${max(profits):,.2f}")
        print(f"  Latest Revenue: ${revenues[-1]:,.2f}")

def export_summary():
    """Export a summary CSV with key metrics"""
    pricing_file = "mara_pricing_history.csv"
    performance_file = "mara_site_performance.csv"
    
    if not (os.path.exists(pricing_file) and os.path.exists(performance_file)):
        print("❌ Missing data files for summary export")
        return
    
    # Read pricing data
    with open(pricing_file, 'r') as f:
        pricing_data = list(csv.DictReader(f))
    
    # Read performance data
    with open(performance_file, 'r') as f:
        performance_data = list(csv.DictReader(f))
    
    # Create summary
    summary_file = "mara_summary.csv"
    
    with open(summary_file, 'w', newline='') as f:
        writer = csv.writer(f)
        
        # Write pricing summary
        writer.writerow(['PRICING SUMMARY'])
        writer.writerow(['Total Price Records', len(pricing_data)])
        
        if pricing_data:
            energy_prices = [float(row['energy_price']) for row in pricing_data]
            hash_prices = [float(row['hash_price']) for row in pricing_data]
            token_prices = [float(row['token_price']) for row in pricing_data]
            
            writer.writerow(['Energy Price Range', f"${min(energy_prices):.4f} - ${max(energy_prices):.4f}"])
            writer.writerow(['Hash Price Range', f"${min(hash_prices):.4f} - ${max(hash_prices):.4f}"])
            writer.writerow(['Token Price Range', f"${min(token_prices):.4f} - ${max(token_prices):.4f}"])
        
        writer.writerow([])  # Empty row
        
        # Write performance summary
        writer.writerow(['SITE PERFORMANCE SUMMARY'])
        writer.writerow(['Site Name', 'Total Records', 'Latest Profit', 'Average Profit', 'Max Profit'])
        
        # Group performance by site
        sites = {}
        for row in performance_data:
            site = row['site_name']
            if site not in sites:
                sites[site] = []
            sites[site].append(row)
        
        for site_name, records in sites.items():
            profits = [float(r['net_profit']) for r in records]
            writer.writerow([
                site_name,
                len(records),
                f"${profits[-1]:,.2f}",
                f"${sum(profits)/len(profits):,.2f}",
                f"${max(profits):,.2f}"
            ])
    
    print(f"✅ Summary exported to {summary_file}")

def main():
    print("🚀 MARA Data Viewer")
    print("=" * 40)
    
    while True:
        print("\nOptions:")
        print("1. View pricing history")
        print("2. View site performance")
        print("3. Export summary CSV")
        print("4. Exit")
        
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == "1":
            view_pricing_data()
        elif choice == "2":
            view_performance_data()
        elif choice == "3":
            export_summary()
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid option")

if __name__ == "__main__":
    main() 