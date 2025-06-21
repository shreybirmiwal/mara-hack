#!/usr/bin/env python3
"""
MARA Price Fetcher
Simple script to fetch latest pricing data and update CSV
"""

import requests
import csv
import os
from datetime import datetime
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class PricingData:
    timestamp: str
    energy_price: float
    hash_price: float
    token_price: float

def fetch_and_update_prices():
    """Fetch current pricing data and update CSV"""
    base_url = "https://mara-hackathon-api.onrender.com"
    pricing_csv = "mara_pricing_history.csv"
    
    try:
        logger.info("Fetching latest pricing data from MARA API...")
        response = requests.get(f"{base_url}/prices")
        response.raise_for_status()
        
        pricing_data = []
        for item in response.json():
            pricing_data.append(PricingData(
                timestamp=item["timestamp"],
                energy_price=item["energy_price"],
                hash_price=item["hash_price"],
                token_price=item["token_price"]
            ))
        
        # Setup CSV if it doesn't exist
        if not os.path.exists(pricing_csv):
            with open(pricing_csv, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'energy_price', 'hash_price', 'token_price', 'recorded_at'])
        
        # Read existing timestamps to avoid duplicates
        existing_timestamps = set()
        if os.path.exists(pricing_csv):
            with open(pricing_csv, 'r') as f:
                reader = csv.DictReader(f)
                existing_timestamps = {row['timestamp'] for row in reader}
        
        # Append new data
        new_data = []
        for price in pricing_data:
            if price.timestamp not in existing_timestamps:
                new_data.append([
                    price.timestamp,
                    price.energy_price,
                    price.hash_price,
                    price.token_price,
                    datetime.now().isoformat()
                ])
        
        if new_data:
            with open(pricing_csv, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerows(new_data)
            logger.info(f"✅ Added {len(new_data)} new price records to CSV")
            
            # Show latest prices
            latest = pricing_data[0]
            logger.info(f"Latest prices - Energy: ${latest.energy_price:.4f}, "
                       f"Hash: ${latest.hash_price:.4f}, Token: ${latest.token_price:.4f}")
        else:
            logger.info("No new price data to add")
            
        return len(pricing_data)
        
    except requests.RequestException as e:
        logger.error(f"Failed to fetch prices: {e}")
        return 0

def main():
    """Main function"""
    print("🚀 MARA Price Fetcher")
    print("=" * 30)
    
    total_records = fetch_and_update_prices()
    
    if total_records > 0:
        print(f"\n📊 Total records fetched: {total_records}")
        print("✨ Price data updated successfully!")
        print("\n💡 Now you can run:")
        print("   python simulate.py    # Historical simulation")
        print("   python view_data.py   # View/analyze data")
    else:
        print("❌ No data fetched. Check API connection.")

if __name__ == "__main__":
    main() 