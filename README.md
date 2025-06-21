# West Texas Energy Pricing Map 🗺️⚡

An interactive topographical map visualization showing real-time energy pricing data from the Texas ERCOT grid. Built with React, Mapbox GL JS, and GridStatus API integration.

![West Texas Energy Map](https://via.placeholder.com/800x400/1f2937/60a5fa?text=West+Texas+Energy+Pricing+Map)

## Features

- **Interactive Topographical Map**: Satellite imagery with terrain elevation
- **Real-time Energy Data**: Live ERCOT pricing data from GridStatus API
- **Multiple Visualizations**: 
  - Colored points showing pricing levels
  - Heatmap overlay for price intensity
  - Regional boundaries (Permian Basin, Wind Corridor)
- **Interactive Elements**:
  - Click points for detailed location info
  - Zoom/pan controls
  - Price legend and market statistics
  - Top 5 highest price locations
- **Responsive Design**: Works on desktop and mobile
- **Auto-refresh**: Data updates every 5 minutes

## Tech Stack

### Backend
- **Flask** - Python web framework
- **GridStatus API** - Real-time energy market data
- **Pandas** - Data processing and analysis
- **Flask-CORS** - Cross-origin resource sharing

### Frontend
- **React** - User interface framework
- **Mapbox GL JS** - Interactive mapping library
- **Tailwind CSS** - Utility-first CSS framework
- **Axios** - HTTP client for API calls

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Mapbox account (free)

### 1. Clone and Setup

```bash
git clone <your-repo>
cd mara
```

### 2. Backend Setup

```bash
cd backend
pip install -r requirements.txt
python server.py
```

The backend will start on `http://localhost:5001`

### 3. Frontend Setup

```bash
cd frontend
npm install
npm start
```

The frontend will start on `http://localhost:3000`

### 4. Get a Free Mapbox Token

1. Sign up at [mapbox.com](https://account.mapbox.com/auth/signup/)
2. Go to [Access Tokens](https://account.mapbox.com/access-tokens/)
3. Click "Create a token"
4. Name it "West Texas Energy Map"
5. Under **Token scopes**, leave all public scopes selected
6. Under **URL restrictions**, add your domain (e.g., `localhost:3000` for development)
7. Click "Create token"
8. Copy the token (starts with `pk.`)

### 5. Configure Mapbox Token

**Option A: Environment Variable (Recommended)**
```bash
# Create .env file in frontend directory
echo "REACT_APP_MAPBOX_TOKEN=your_token_here" > frontend/.env
```

**Option B: Direct Replacement**
Replace the token in `frontend/src/App.js`:
```javascript
const MAPBOX_TOKEN = 'your_token_here';
```

## API Endpoints

### Backend Endpoints

- `GET /api/health` - Health check
- `GET /api/energy-data` - Current energy pricing data
- `GET /api/energy-stats` - Market statistics
- `GET /api/cache-info` - Cache status information

### Example Response

```json
{
  "success": true,
  "data": [
    {
      "location_code": "WR_RN",
      "location_name": "West Texas",
      "lat": 31.5804,
      "lng": -99.5805,
      "type": "Traditional",
      "price_mwh": 45.67,
      "timestamp": "2025-01-09 14:30:00",
      "price_category": "medium"
    }
  ],
  "total_locations": 1024,
  "price_range": {
    "min": -251.45,
    "max": 1985.68,
    "avg": 32.62
  }
}
```

## Configuration

### Environment Variables

#### Backend
- `GRIDSTATUS_API_KEY` - Your GridStatus API key (already configured)

#### Frontend
- `REACT_APP_MAPBOX_TOKEN` - Your Mapbox access token

### Map Configuration

You can customize the map by modifying these settings in `App.js`:

```javascript
// Initial map view
const [viewState, setViewState] = useState({
  longitude: -99.9018,  // West Texas center
  latitude: 31.9686,
  zoom: 6.5,
  pitch: 45,           // 3D tilt angle
  bearing: 0           // Rotation
});

// Map style options
mapStyle="mapbox://styles/mapbox/satellite-streets-v12"
// Other options: satellite-v9, outdoors-v12, light-v11, dark-v11
```

## Data Sources

- **Energy Data**: [GridStatus.io](https://gridstatus.io) - Real-time electricity market data
- **Map Data**: [Mapbox](https://www.mapbox.com) - Satellite imagery and terrain data
- **ERCOT**: Electric Reliability Council of Texas - Texas electricity grid operator

## Map Features Explained

### Price Color Coding
- 🔴 **Red**: Very High (>$100/MWh)
- 🟠 **Orange**: High ($50-100/MWh)  
- 🟡 **Yellow**: Medium ($25-50/MWh)
- 🟢 **Green**: Low ($0-25/MWh)
- ⚫ **Gray**: Zero/Negative

### Regional Overlays
- **Permian Basin**: Major oil & gas producing region
- **Wind Corridor**: High wind energy potential area

### Interactive Elements
- **Click Points**: View detailed location information
- **Heatmap**: Shows price intensity across regions
- **Controls**: Zoom in/out, reset view
- **Auto-refresh**: Data updates every 5 minutes

## Development

### Project Structure
```
mara/
├── backend/
│   ├── server.py          # Flask server
│   └── requirements.txt   # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── App.js        # Main React component
│   │   └── App.css       # Styling
│   ├── package.json      # Node dependencies
│   └── .env              # Environment variables
└── README.md
```

### Adding New Features

1. **Backend**: Add new endpoints in `server.py`
2. **Frontend**: Modify components in `App.js`
3. **Styling**: Update `App.css` or Tailwind classes

### API Rate Limiting

The backend implements caching to avoid hitting GridStatus API limits:
- 5-minute cache duration
- Exponential backoff on retries
- Single moment data fetching (most recent timestamp)

## Troubleshooting

### Map Not Loading
1. Check Mapbox token is correct
2. Verify URL restrictions in Mapbox dashboard
3. Check browser console for errors

### No Data Showing
1. Ensure backend is running on port 5001
2. Check GridStatus API status
3. Verify CORS settings

### Performance Issues
1. Reduce map size or zoom level
2. Check Mapbox usage limits
3. Monitor API call frequency

## Future Enhancements

### Planned Features
- **AI Agent Simulation**: 1000s of agents simulating population movement
- **Weather Integration**: Weather data affecting energy prices
- **Historical Data**: Time-series analysis and trends
- **More Regions**: Expand beyond West Texas
- **Mobile App**: React Native version

### Technical Improvements
- WebSocket real-time updates
- Advanced caching strategies
- Machine learning price predictions
- 3D terrain visualization

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is for educational and demonstration purposes.

## Support

For questions or issues:
1. Check the troubleshooting section
2. Review the API documentation
3. Open an issue on GitHub

---

**Built with ❤️ for energy market visualization and mapping innovation**