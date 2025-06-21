# MARA Energy App Setup Instructions

## Quick Setup Guide

### 1. Fix Mapbox Token (Frontend Issue)

The current Mapbox token is invalid. You need to get a free token:

1. Go to [mapbox.com](https://account.mapbox.com/access-tokens/)
2. Sign up for a free account (if you don't have one)
3. Go to "Access tokens"
4. Create a new token (or copy your default public token)
5. Copy the example file: `cp frontend/.env.example frontend/.env`
6. Replace `YOUR_MAPBOX_TOKEN_HERE` with your actual token in `frontend/.env`

**Example:**
```bash
# frontend/.env
REACT_APP_MAPBOX_TOKEN=pk.eyJ1Ijoic2hyZXliIiwiYSI6ImNtYzZuMmhlaDE0Z3Qya3BwZTB1Z3VvMWwifQ.zj5cBOnK5USIcD5TBa5z5w
```

### 2. Fix Backend API Keys (Optional but Recommended)

For full functionality, set up API keys for real energy data and AI scenarios:

1. Copy the example file: `cp backend/.env.example backend/.env`
2. Get API keys:
   - **GridStatus API**: Go to [gridstatus.io](https://gridstatus.io) for real energy data
   - **OpenRouter API**: Go to [openrouter.ai/keys](https://openrouter.ai/keys) for AI scenario analysis

**Example:**
```bash
# backend/.env
GRIDSTATUS_API_KEY=your_actual_gridstatus_key_here
OPENROUTER_API_KEY=your_actual_openrouter_key_here
```

### 3. Start the Applications

**Terminal 1 - Backend:**
```bash
cd backend
python3 -m pip install -r requirements.txt
python3 server.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm install
npm start
```

## What Each API Key Does

- **Mapbox Token**: Required for map display. Without it, you'll see a setup screen.
- **GridStatus API**: Provides real Texas energy market data. Without it, the app uses mock data.
- **OpenRouter API**: Powers AI scenario analysis. Without it, you get basic scenario effects.

## The app will work with just the Mapbox token, but you'll get the full experience with all three keys configured. 