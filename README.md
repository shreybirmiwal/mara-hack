# MARA Hackathon Site Manager

A Python application for managing multiple mining/data center sites and optimizing profitability for the MARA Hackathon 2025.

## Features

- **Multi-Site Management**: Create and manage 3 mining sites (Rockdale TX, Cheyenne WY, Butte MT)
- **Real-Time Optimization**: Automatically optimize machine allocation based on current prices
- **Historical Data Tracking**: Store and analyze pricing and performance data
- **Profitability Analysis**: Calculate optimal configurations for maximum profit
- **Interactive Management**: Easy-to-use command-line interface for manual control

## Files

- `main.py` - Main application with automatic optimization loop
- `manage_sites.py` - Interactive utility for manual site management
- `requirements.txt` - Python dependencies
- `mara_data.db` - SQLite database (created automatically)

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Option 1: Automatic Mode (Recommended)
Run the main application for continuous optimization:
```bash
python main.py
```

This will:
1. Create 3 mining sites in Rockdale TX, Cheyenne WY, and Butte MT
2. Fetch current pricing data
3. Optimize machine allocation for maximum profit
4. Continue monitoring and reoptimizing every 5 minutes

### Option 2: Interactive Mode
Use the management utility for manual control:
```bash
python manage_sites.py
```

Available commands:
1. **Create sites** - Set up the 3 mining locations
2. **Check current prices** - View latest energy, hash, and token prices
3. **View inventory** - See available machine types and specifications
4. **Optimize all sites** - Run optimization algorithm once
5. **Show site status** - Display current allocation and profitability
6. **Performance summary** - View comprehensive performance metrics
7. **Manual machine allocation** - Manually configure machine types
8. **Historical data analysis** - View pricing trends and performance history

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
- **pricing_history**: Historical price data updated every 5 minutes
- **site_performance**: Site performance metrics and machine configurations

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
**Database Issues**: Delete `mara_data.db` to reset and recreate database

## Support

This application was built for the MARA Hackathon 2025. For questions or issues, refer to the hackathon documentation or API specification. 