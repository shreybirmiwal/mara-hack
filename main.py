#!/usr/bin/env python3
"""
MARA Hackathon Site Manager
Manages multiple mining/data center sites and optimizes profitability
"""

import requests
import json
import time
import sqlite3
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class Site:
    name: str
    api_key: str
    power_limit: int
    location: str

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

class MaraSiteManager:
    def __init__(self):
        self.base_url = "https://mara-hackathon-api.onrender.com"
        self.sites: Dict[str, Site] = {}
        self.inventory_cache = None
        self.setup_database()
        
    def setup_database(self):
        """Initialize SQLite database for storing historical data"""
        self.conn = sqlite3.connect('mara_data.db')
        cursor = self.conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pricing_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                energy_price REAL,
                hash_price REAL,
                token_price REAL,
                recorded_at TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS site_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                site_name TEXT,
                timestamp TEXT,
                total_revenue REAL,
                total_power_cost REAL,
                total_power_used INTEGER,
                net_profit REAL,
                machine_config TEXT
            )
        ''')
        
        self.conn.commit()
        
    def create_site(self, name: str, location: str) -> Optional[Site]:
        """Create a new mining site"""
        try:
            response = requests.post(
                f"{self.base_url}/sites",
                json={"name": name}
            )
            response.raise_for_status()
            
            data = response.json()
            site = Site(
                name=name,
                api_key=data["api_key"],
                power_limit=data["power"],
                location=location
            )
            
            self.sites[name] = site
            logger.info(f"Created site '{name}' in {location} with power limit: {site.power_limit}")
            logger.info(f"API Key: {site.api_key}")
            
            return site
            
        except requests.RequestException as e:
            logger.error(f"Failed to create site '{name}': {e}")
            return None
    
    def get_current_prices(self) -> List[PricingData]:
        """Fetch current pricing data"""
        try:
            response = requests.get(f"{self.base_url}/prices")
            response.raise_for_status()
            
            pricing_data = []
            for item in response.json():
                pricing_data.append(PricingData(
                    timestamp=item["timestamp"],
                    energy_price=item["energy_price"],
                    hash_price=item["hash_price"],
                    token_price=item["token_price"]
                ))
            
            # Store in database
            cursor = self.conn.cursor()
            for price in pricing_data:
                cursor.execute('''
                    INSERT OR IGNORE INTO pricing_history 
                    (timestamp, energy_price, hash_price, token_price, recorded_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (price.timestamp, price.energy_price, price.hash_price, 
                     price.token_price, datetime.now().isoformat()))
            
            self.conn.commit()
            return pricing_data
            
        except requests.RequestException as e:
            logger.error(f"Failed to fetch prices: {e}")
            return []
    
    def get_inventory(self) -> Optional[dict]:
        """Get inventory information (cached since it's static)"""
        if self.inventory_cache is None:
            try:
                response = requests.get(f"{self.base_url}/inventory")
                response.raise_for_status()
                self.inventory_cache = response.json()
                logger.info("Inventory data cached")
            except requests.RequestException as e:
                logger.error(f"Failed to fetch inventory: {e}")
                return None
        
        return self.inventory_cache
    
    def update_site_machines(self, site_name: str, config: MachineConfig) -> bool:
        """Update machine allocation for a site"""
        if site_name not in self.sites:
            logger.error(f"Site '{site_name}' not found")
            return False
        
        site = self.sites[site_name]
        
        try:
            # Calculate total power usage
            inventory = self.get_inventory()
            if not inventory:
                return False
            
            total_power = (
                config.air_miners * inventory["miners"]["air"]["power"] +
                config.hydro_miners * inventory["miners"]["hydro"]["power"] +
                config.immersion_miners * inventory["miners"]["immersion"]["power"] +
                config.gpu_compute * inventory["inference"]["gpu"]["power"] +
                config.asic_compute * inventory["inference"]["asic"]["power"]
            )
            
            if total_power > site.power_limit:
                logger.error(f"Power usage ({total_power}) exceeds limit ({site.power_limit}) for site '{site_name}'")
                return False
            
            response = requests.put(
                f"{self.base_url}/machines",
                headers={"X-Api-Key": site.api_key},
                json={
                    "air_miners": config.air_miners,
                    "hydro_miners": config.hydro_miners,
                    "immersion_miners": config.immersion_miners,
                    "gpu_compute": config.gpu_compute,
                    "asic_compute": config.asic_compute
                }
            )
            response.raise_for_status()
            
            logger.info(f"Updated machines for site '{site_name}': {config}")
            return True
            
        except requests.RequestException as e:
            logger.error(f"Failed to update machines for site '{site_name}': {e}")
            return False
    
    def get_site_status(self, site_name: str) -> Optional[dict]:
        """Get current status and revenue for a site"""
        if site_name not in self.sites:
            logger.error(f"Site '{site_name}' not found")
            return None
        
        site = self.sites[site_name]
        
        try:
            response = requests.get(
                f"{self.base_url}/machines",
                headers={"X-Api-Key": site.api_key}
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Calculate net profit
            net_profit = data.get("total_revenue", 0) - data.get("total_power_cost", 0)
            data["net_profit"] = net_profit
            
            # Store performance data
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO site_performance 
                (site_name, timestamp, total_revenue, total_power_cost, total_power_used, net_profit, machine_config)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                site_name,
                datetime.now().isoformat(),
                data.get("total_revenue", 0),
                data.get("total_power_cost", 0),
                data.get("total_power_used", 0),
                net_profit,
                json.dumps({
                    "air_miners": data.get("air_miners", 0),
                    "hydro_miners": data.get("hydro_miners", 0),
                    "immersion_miners": data.get("immersion_miners", 0),
                    "gpu_compute": data.get("gpu_compute", 0),
                    "asic_compute": data.get("asic_compute", 0)
                })
            ))
            self.conn.commit()
            
            return data
            
        except requests.RequestException as e:
            logger.error(f"Failed to get status for site '{site_name}': {e}")
            return None
    
    def calculate_optimal_configuration(self, site_name: str) -> Optional[MachineConfig]:
        """Calculate optimal machine configuration based on current prices"""
        if site_name not in self.sites:
            return None
        
        site = self.sites[site_name]
        inventory = self.get_inventory()
        prices = self.get_current_prices()
        
        if not inventory or not prices:
            return None
        
        # Get latest prices
        latest_price = prices[0]
        
        # Calculate profitability per power unit for each machine type
        profitability = {}
        
        # Miners (generate hash, consume power)
        for miner_type, specs in inventory["miners"].items():
            hashrate = specs["hashrate"]
            power = specs["power"]
            revenue_per_hour = hashrate * latest_price.hash_price
            cost_per_hour = power * latest_price.energy_price
            profit_per_power = (revenue_per_hour - cost_per_hour) / power if power > 0 else 0
            profitability[f"{miner_type}_miners"] = profit_per_power
        
        # Inference machines (generate tokens, consume power)
        for compute_type, specs in inventory["inference"].items():
            tokens = specs["tokens"]
            power = specs["power"]
            revenue_per_hour = tokens * latest_price.token_price
            cost_per_hour = power * latest_price.energy_price
            profit_per_power = (revenue_per_hour - cost_per_hour) / power if power > 0 else 0
            profitability[f"{compute_type}_compute"] = profit_per_power
        
        # Sort by profitability
        sorted_machines = sorted(profitability.items(), key=lambda x: x[1], reverse=True)
        
        logger.info(f"Profitability ranking for {site_name}:")
        for machine, profit in sorted_machines:
            logger.info(f"  {machine}: {profit:.6f} profit per power unit")
        
        # Allocate power to most profitable machines first
        config = MachineConfig()
        remaining_power = site.power_limit
        
        for machine_type, _ in sorted_machines:
            if remaining_power <= 0:
                break
            
            if machine_type.endswith("_miners"):
                machine_name = machine_type.replace("_miners", "")
                machine_power = inventory["miners"][machine_name]["power"]
            else:
                machine_name = machine_type.replace("_compute", "")
                machine_power = inventory["inference"][machine_name]["power"]
            
            max_machines = remaining_power // machine_power
            
            if max_machines > 0:
                setattr(config, machine_type, max_machines)
                remaining_power -= max_machines * machine_power
                logger.info(f"  Allocated {max_machines} {machine_type} (power: {max_machines * machine_power})")
        
        return config
    
    def optimize_all_sites(self):
        """Optimize machine allocation for all sites"""
        logger.info("Optimizing all sites...")
        
        for site_name in self.sites:
            optimal_config = self.calculate_optimal_configuration(site_name)
            if optimal_config:
                self.update_site_machines(site_name, optimal_config)
                
                # Get updated status
                status = self.get_site_status(site_name)
                if status:
                    logger.info(f"Site '{site_name}' - Revenue: ${status['total_revenue']:.2f}, "
                              f"Cost: ${status['total_power_cost']:.2f}, "
                              f"Profit: ${status['net_profit']:.2f}")
    
    def get_performance_summary(self) -> dict:
        """Get performance summary for all sites"""
        summary = {}
        
        for site_name in self.sites:
            status = self.get_site_status(site_name)
            if status:
                summary[site_name] = {
                    "location": self.sites[site_name].location,
                    "power_limit": self.sites[site_name].power_limit,
                    "power_used": status.get("total_power_used", 0),
                    "revenue": status.get("total_revenue", 0),
                    "cost": status.get("total_power_cost", 0),
                    "profit": status.get("net_profit", 0),
                    "efficiency": status.get("net_profit", 0) / status.get("total_power_used", 1)
                }
        
        return summary
    
    def close(self):
        """Close database connection"""
        if hasattr(self, 'conn'):
            self.conn.close()

def main():
    """Main function to create sites and start optimization"""
    manager = MaraSiteManager()
    
    try:
        # Create the ten sites
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
        
        logger.info("Creating mining sites...")
        for name, location in sites_to_create:
            site = manager.create_site(name, location)
            if not site:
                logger.error(f"Failed to create site {name}")
                continue
        
        # Wait a moment for sites to be ready
        time.sleep(2)
        
        # Get initial pricing data
        logger.info("Fetching initial pricing data...")
        prices = manager.get_current_prices()
        if prices:
            latest = prices[0]
            logger.info(f"Latest prices - Energy: ${latest.energy_price:.4f}, "
                       f"Hash: ${latest.hash_price:.4f}, Token: ${latest.token_price:.4f}")
        
        # Optimize all sites
        manager.optimize_all_sites()
        
        # Display performance summary
        logger.info("Performance Summary:")
        summary = manager.get_performance_summary()
        for site_name, metrics in summary.items():
            logger.info(f"\n{site_name} ({metrics['location']}):")
            logger.info(f"  Power: {metrics['power_used']:,}/{metrics['power_limit']:,} "
                       f"({metrics['power_used']/metrics['power_limit']*100:.1f}%)")
            logger.info(f"  Revenue: ${metrics['revenue']:,.2f}")
            logger.info(f"  Cost: ${metrics['cost']:,.2f}")
            logger.info(f"  Profit: ${metrics['profit']:,.2f}")
            logger.info(f"  Efficiency: ${metrics['efficiency']:.6f} profit/power")
        
        # Start continuous optimization loop
        logger.info("\nStarting continuous optimization (press Ctrl+C to stop)...")
        while True:
            time.sleep(300)  # Wait 5 minutes (prices update every 5 minutes)
            logger.info("Checking for price updates...")
            manager.get_current_prices()
            manager.optimize_all_sites()
            
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        manager.close()

if __name__ == "__main__":
    main() 