#!/bin/bash

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
REACT_APP_MAPBOX_TOKEN=pk.eyJ1Ijoic2hyZXliIiwiYSI6ImNtYzZxMGMzbTE2NmwybXB0c21wODc3am8ifQ.CvTe9eKqRgGaEgGRp3ApTw
EOF
    echo "✅ .env file created"
fi

# Set the Mapbox token as an environment variable (backup)
export REACT_APP_MAPBOX_TOKEN="pk.eyJ1Ijoic2hyZXliIiwiYSI6ImNtYzZxMGMzbTE2NmwybXB0c21wODc3am8ifQ.CvTe9eKqRgGaEgGRp3ApTw"

# Generate fresh site data
echo "🔄 Generating site data..."
python export_map_data.py

# Start the React app
echo "🚀 Starting MARA Geographic Optimizer..."
npm start 