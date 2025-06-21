# 🚀 MARA Geographic Mining Optimizer

A comprehensive system for optimizing cryptocurrency mining operations across geographically diverse locations using real-world constraints like water availability, climate conditions, and infrastructure capabilities.

## 🎯 Key Features

### **Geographic Realism**
- **Water Constraints**: Hydro/immersion miners limited by actual water availability
- **Climate Factors**: Air cooling efficiency varies by regional climate
- **Infrastructure**: Compute workloads require appropriate infrastructure
- **Electricity Costs**: Regional multipliers (Idaho 0.8x vs New York 1.5x)

### **Interactive Map Visualization**
- **Real-time Mapbox Integration**: Interactive map showing all 10 mining locations
- **Hover Tooltips**: Quick stats on machine counts and profitability 
- **Click for Details**: Comprehensive site information with efficiency meters
- **Color-coded Markers**: Visual profitability indicators (Green = High, Red = Low)

### **Realistic Machine Allocation**
- **Location-specific Inventory Limits**: 
  - Boise ID: 160 Hydro (excellent water access)
  - Cheyenne WY: 0 Hydro (water scarce desert)
  - Montana: Air-cooling preferred (dry climate)
- **Geographic Efficiency Modifiers**: Performance varies by location suitability

## 🗺️ Mining Locations

| Location | Profile | Water | Climate | Infrastructure | Key Strengths |
|----------|---------|--------|---------|----------------|---------------|
| **Boise, ID** | Hydro Optimal | 95% | 80% | 70% | Abundant hydro power |
| **Massena, NY** | Hydro Optimal | 98% | 90% | 80% | Excellent water access |
| **Knoxville, TN** | Hydro Preferred | 85% | 70% | 80% | Good water infrastructure |
| **Massillon, OH** | Mixed Hydro | 80% | 75% | 85% | Balanced capabilities |
| **Muskogee, OK** | Mixed Balanced | 65% | 60% | 70% | Cost-effective location |
| **Butte, MT** | Air Preferred | 45% | 85% | 60% | Excellent air cooling |
| **Sandersville, GA** | Air Immersion | 40% | 50% | 75% | Hot climate + limited water |
| **Cheyenne, WY** | Air Optimal | 25% | 95% | 65% | Dry desert conditions |
| **Kearney, NE** | Air Optimal | 30% | 90% | 70% | Great Plains efficiency |
| **Rockdale, TX** | Air Compute | 35% | 85% | 80% | High infrastructure |

## 🚀 Quick Start

### **1. Run Current Optimization**
```bash
python optimize.py
```

### **2. Launch Interactive Map**
```bash
# Option 1: Use the launch script (creates .env automatically)
./start_app.sh

# Option 2: Create .env file manually and start
python create_env.py
python export_map_data.py
npm start

# Option 3: Set environment variable manually
python export_map_data.py
REACT_APP_MAPBOX_TOKEN="pk.eyJ1Ijoic2hyZXliIiwiYSI6ImNtYzZxMGMzbTE2NmwybXB0c21wODc3am8ifQ.CvTe9eKqRgGaEgGRp3ApTw" npm start
```

### **3. Historical Analysis**
```bash
python simulate.py
```

### **4. View Data & Analytics**
```bash
python view_data.py
```

## 🎮 Using the Interactive Map

### **Map Controls**
- **🖱️ Hover**: Quick profit and machine stats
- **🖱️ Click**: Detailed site information with efficiency meters
- **🔍 Zoom/Pan**: Explore different regions
- **📊 Legend**: Understand profitability color coding

### **Tooltip Information**
- **💰 Profitability**: Net profit, revenue, costs
- **⚡ Electricity**: Regional cost per MWh
- **🏭 Machine Allocation**: Current vs maximum capacity
- **📊 Efficiency Meters**: Water, climate, infrastructure ratings
- **🌍 Geographic Profile**: Location optimization strategy

### **Profitability Legend**
- 🟢 **High** (>$1.5M): Excellent locations like Boise
- 🟡 **Medium** ($500K-$1.5M): Solid performers
- 🔴 **Low** (<$500K): Marginal locations
- ⚫ **Zero**: Unprofitable (e.g., Wyoming's water scarcity)

## 📁 Project Structure

```
mara-hack/
├── 📊 Core Python Scripts
│   ├── optimize.py          # Geographic optimizer with constraints
│   ├── simulate.py          # Historical simulation
│   ├── fetch_prices.py      # Price data collection
│   └── view_data.py         # Data analysis tools
├── 🗺️ React Map Application
│   ├── src/
│   │   ├── App.js           # Main React application
│   │   ├── App.css          # Styling and UI
│   │   └── components/
│   │       └── MapComponent.js  # Mapbox integration
│   ├── public/
│   │   ├── index.html       # HTML template
│   │   └── site_data.json   # Generated site data
│   └── package.json         # React dependencies
├── 📈 Data Files
│   ├── mara_pricing_history.csv  # Historical price data
│   └── optimal_configs.csv       # Exported configurations
└── 🛠️ Utilities
    ├── export_map_data.py    # Generate JSON for React
    ├── start_app.sh          # Launch script
    └── demo.py              # Complete workflow demo
```

## 🎯 Current Results

### **Geographic Optimization Results**
- **Total Profit**: $7.1M across all sites
- **Best Location**: Boise, ID ($2.5M profit) - Excellent hydro access
- **Worst Location**: Cheyenne, WY ($0 profit) - Water scarcity
- **Geographic Advantage**: $2.5M difference between best/worst

### **Machine Distribution**
- **Hydro-Rich Sites**: Boise (160+20), Massena (160), Knoxville (100)
- **Air-Cooling Sites**: Wyoming, Nebraska, Montana
- **Mixed Sites**: Oklahoma, Ohio with moderate capabilities
- **Zero Hydro**: Wyoming (too dry), some Texas/Georgia locations

### **Key Insights**
- **Water Access is Critical**: Sites with >90% water availability dominate
- **Climate Efficiency Matters**: Air cooling thrives in dry, cool regions
- **Geographic Arbitrage**: $792K profit difference per site location
- **Realistic Constraints**: No more unrealistic 200 hydro miners everywhere!

## 🔧 Technical Features

### **Geographic Constraint Engine**
- **Water Availability**: 0.25 (Wyoming) to 0.98 (Massena NY)
- **Climate Factors**: Desert efficiency vs humid regions
- **Infrastructure**: Data center readiness for compute workloads
- **Electricity Multipliers**: Regional cost variations

### **Machine Type Optimization**
- **💧 Hydro Miners**: High hashrate, needs water access
- **🌬️ Air Miners**: Climate dependent, works in dry regions  
- **🌊 Immersion Miners**: Water required, good for hot climates
- **🖥️ GPU Compute**: Infrastructure dependent
- **⚡ ASIC Compute**: More forgiving requirements

### **Real-time Updates**
- **Live Price Data**: 5-minute API updates
- **Dynamic Optimization**: Automatic recalculation
- **Interactive Visualization**: Real-time map updates

## 🌍 Geographic Intelligence

The system models real-world geographic factors:

- **Idaho**: Abundant hydroelectric power → Optimal for hydro miners
- **Wyoming**: Desert conditions → Zero hydro capacity, perfect for air cooling
- **New York**: High electricity costs but excellent water access
- **Texas**: Hot climate + infrastructure → Good for compute + air cooling
- **Montana**: Mountain region with limited water but excellent air cooling

This creates realistic geographic specialization where each location has natural advantages for specific mining strategies.

---

## 🛠️ Setup Requirements

```bash
# Python Dependencies
pip install requests pandas

# React Dependencies  
npm install

# Create .env file (choose one):
python create_env.py                    # Automatic
./start_app.sh                          # Creates .env and starts app
# OR manually create .env with: REACT_APP_MAPBOX_TOKEN=pk.eyJ1Ijoic2hyZXliIiwiYSI6ImNtYzZxMGMzbTE2NmwybXB0c21wODc3am8ifQ.CvTe9eKqRgGaEgGRp3ApTw
```

## 🎯 Usage Examples

### **Quick Optimization**
```bash
python optimize.py
# Shows: Geographic constraints, machine allocations, profitability rankings
```

### **Map Visualization**
```bash
./start_app.sh
# Opens: http://localhost:3000 with interactive map
```

### **Historical Analysis**
```bash
python simulate.py
# Options: Full simulation, recent data, geographic comparison
```

**Built for MARA Hackathon 2025** 🏆
*Realistic geographic mining optimization with interactive visualization* 