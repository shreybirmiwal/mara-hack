#!/usr/bin/env python3
"""
Create .env file for React app with Mapbox token
"""

import os

def create_env_file():
    """Create .env file if it doesn't exist"""
    env_file = '.env'
    
    if os.path.exists(env_file):
        print("✅ .env file already exists")
        return
    
    mapbox_token = "pk.eyJ1Ijoic2hyZXliIiwiYSI6ImNtYzZxMGMzbTE2NmwybXB0c21wODc3am8ifQ.CvTe9eKqRgGaEgGRp3ApTw"
    
    with open(env_file, 'w') as f:
        f.write(f"REACT_APP_MAPBOX_TOKEN={mapbox_token}\n")
    
    print("✅ Created .env file with Mapbox token")
    print("🚀 You can now run: npm start")

if __name__ == "__main__":
    create_env_file() 