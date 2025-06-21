#!/usr/bin/env python3
"""
MARA Hackathon Demo
Complete workflow demonstration
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and show its output"""
    print(f"\n🚀 {description}")
    print("=" * 60)
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(f"Error: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"Failed to run command: {e}")
        return False

def main():
    print("🎬 MARA Hackathon Complete Workflow Demo")
    print("=" * 50)
    
    # Step 1: Fetch latest prices
    if not run_command("python fetch_prices.py", "Step 1: Fetching Latest Price Data"):
        print("❌ Failed to fetch prices. Check API connection.")
        return
    
    # Step 2: Show current optimization
    print(f"\n🧠 Step 2: Current Optimization Results")
    print("=" * 60)
    run_command("echo '1' | python optimize.py | head -50", "Running Optimization")
    
    # Step 3: Show electricity cost comparison
    print(f"\n💡 Step 3: Regional Electricity Cost Analysis") 
    print("=" * 60)
    run_command("echo '2' | python optimize.py | head -20", "Electricity Costs")
    
    # Step 4: Show historical simulation sample
    print(f"\n📊 Step 4: Historical Simulation Sample")
    print("=" * 60)
    run_command("echo '2' | python simulate.py | head -30", "Recent Historical Data")
    
    # Step 5: Show available data
    if os.path.exists("mara_pricing_history.csv"):
        with open("mara_pricing_history.csv", 'r') as f:
            lines = f.readlines()
            record_count = len(lines) - 1  # Subtract header
        
        print(f"\n📈 Step 5: Data Summary")
        print("=" * 60)
        print(f"📊 Total price records collected: {record_count}")
        print(f"📁 Price data file: mara_pricing_history.csv")
        print(f"🔧 Ready for Excel/Python analysis")
    
    print(f"\n✨ Demo Complete!")
    print("=" * 30)
    print("🚀 Available Commands:")
    print("   python fetch_prices.py   # Update price data")
    print("   python optimize.py       # Optimize configurations") 
    print("   python simulate.py       # Historical simulation")
    print("   python view_data.py      # View/analyze data")
    print()
    print("💡 Key Insights:")
    print("   • BoiseID has the lowest electricity costs (0.8x)")
    print("   • MassenaNY has the highest electricity costs (1.5x)")
    print("   • Geographic arbitrage can save ~$792k+ per site")
    print("   • All optimization runs locally after initial price fetch")

if __name__ == "__main__":
    main() 