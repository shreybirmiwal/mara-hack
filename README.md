# MARA Hackathon Local Optimizer

A Python application for optimizing mining/data center configurations using local price data without API dependencies.

## Features

- **Regional Cost Analysis**: 10 mining locations with realistic electricity cost multipliers
- **Local Optimization**: Calculate optimal configurations using historical price data
- **Historical Simulation**: Replay optimization decisions across any time period
- **CSV Data Management**: Clean CSV files for easy analysis and export
- **No API Dependencies**: Run everything locally after initial price fetch

## Files

- `fetch_prices.py` - Fetch latest pricing data from MARA API (only when needed)
- `optimize.py` - Local optimizer using latest price data  
- `simulate.py` - Historical simulation using collected price data
- `view_data.py` - View and analyze collected data
- `demo.py` - Complete workflow demonstration
- `requirements.txt` - Python dependencies
- `mara_pricing_history.csv` - Historical pricing data (created automatically)

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Step 1: Fetch Price Data (Only When Needed)
Get the latest pricing data from the MARA API:
```bash
python fetch_prices.py
```

### Step 2: Run Local Optimization
Optimize all sites using the latest price data:
```bash
python optimize.py
```

### Step 3: Historical Analysis
Run simulations using collected historical data:
```bash
python simulate.py
```

### Step 4: View/Export Data
Analyze your collected data:
```bash
python view_data.py
```

### Quick Demo
See the complete workflow in action:
```bash
python demo.py
```

## How It Works

### Machine Types Available:
**Miners** (generate hashrate, consume power):
- Air miners: 1000 hashrate, 3500 power
- Hydro miners: 5000 hashrate, 5000 power  
- Immersion miners: 10000 hashrate, 10000 power

**Inference Machines** (generate tokens, consume power):
- GPU compute: 1000 tokens, 5000 power
- ASIC compute: 50000 tokens, 15000 power

### Optimization Algorithm:
1. Fetch current prices (energy, hash, token)
2. Calculate profitability per power unit for each machine type:
   - Miners: `(hashrate × hash_price - power × energy_price) / power`
   - Inference: `(tokens × token_price - power × energy_price) / power`
3. Rank machine types by profitability
4. Allocate available power to most profitable machines first
5. Update site configuration via API

### Data Storage:
- **mara_pricing_history.csv**: Historical price data updated every 5 minutes
- **mara_site_performance.csv**: Site performance metrics and machine configurations

## Key Features

### Smart Optimization
The system automatically switches between miners and inference machines based on market conditions:
- When hash prices are high → prioritize miners
- When token prices are high → prioritize inference machines
- Always considers energy costs in profitability calculations

### Multi-Site Management
Each site operates independently with its own:
- Power limit (typically 1,000,000 units)
- API key for authentication
- Optimized machine configuration
- Performance tracking

### Real-Time Monitoring
- Prices update every 5 minutes
- Automatic reoptimization when prices change
- Historical trend analysis
- Performance comparison across sites

## Example Output

```
INFO: Created site 'RockdaleTX' in Rockdale, Texas with power limit: 1000000
INFO: API Key: your-api-key-here

INFO: Latest prices - Energy: $0.6479, Hash: $8.4482, Token: $2.9123

INFO: Profitability ranking for RockdaleTX:
INFO:   asic_compute: 0.009636 profit per power unit
INFO:   immersion_miners: 0.008386 profit per power unit
INFO:   hydro_miners: 0.004862 profit per power unit
INFO:   air_miners: 0.001033 profit per power unit
INFO:   gpu_compute: 0.000128 profit per power unit

INFO: Site 'RockdaleTX' - Revenue: $388859.15, Cost: $238466.36, Profit: $150392.79
```

## API Integration

The application integrates with the MARA Hackathon API:
- `POST /sites` - Create mining sites
- `GET /prices` - Fetch current pricing data
- `GET /inventory` - Get machine specifications
- `PUT /machines` - Update machine allocation
- `GET /machines` - Get site status and revenue

## Future Enhancements

This application is designed with GUI development in mind. Potential future features:
- Web dashboard for real-time monitoring
- Advanced analytics and forecasting
- Mobile notifications for significant price changes
- Multi-strategy optimization algorithms
- Export capabilities for reporting

## Troubleshooting

**Connection Issues**: Check internet connection and API endpoint availability
**Authentication Errors**: Verify API keys are correct and sites were created successfully
**Power Limit Exceeded**: Reduce machine allocation or check power calculations
**Data Issues**: Delete CSV files (`mara_pricing_history.csv`, `mara_site_performance.csv`) to reset data

## Support

This application was built for the MARA Hackathon 2025. For questions or issues, refer to the hackathon documentation or API specification. 