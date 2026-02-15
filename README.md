# AI-Based Smart Ambulance Routing System

A production-ready web application for real-time ambulance routing with hospital search and route optimization.

## Features

- Real-time GPS location detection
- Nearest hospital search using OpenStreetMap
- Optimal route calculation using OSRM
- Interactive map with markers and route visualization
- Modern dark-themed UI with smooth animations
- Mobile-responsive design
- Completely free (no API keys required)

## Setup Instructions

### Prerequisites

- Python 3.7+
- Modern web browser

### Installation

1. **Clone/Download the project**
   ```bash
   cd smart-ambulance
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the backend server**
   ```bash
   cd backend
   python app.py
   ```
   Server will start at `http://localhost:5000`

4. **Open the frontend**
   - Open `frontend/index.html` in your web browser
   - Or serve it using a local server:
   ```bash
   cd frontend
   python -m http.server 8000
   ```
   Then visit `http://localhost:8000`

## Usage

1. **Allow location access** when prompted by the browser
2. **Click the EMERGENCY button** to find the nearest hospital
3. **View the calculated route** on the map
4. **Check hospital details** in the left panel

## API Endpoints

### GET /
Health check endpoint

### POST /emergency
Find nearest hospital and calculate route

**Request:**
```json
{
  "lat": 40.7128,
  "lng": -74.0060
}
```

**Response:**
```json
{
  "hospital": "Hospital Name",
  "hospitalLat": 40.7589,
  "hospitalLng": -73.9851,
  "route": [[40.7128, -74.0060], ...],
  "distance": 2500,
  "address": "123 Hospital St, New York, NY"
}
```

## Architecture

- **Backend**: Flask with modular service architecture
- **Frontend**: Vanilla JavaScript with Leaflet.js for maps
- **APIs**: OpenStreetMap Overpass API, OSRM routing service
- **Styling**: Modern CSS with flexbox/grid layout

## Project Structure

```
smart-ambulance/
├── backend/
│   ├── app.py                 # Main Flask application
│   ├── services/
│   │   ├── hospital_service.py # Hospital search logic
│   │   └── routing_service.py  # Route calculation
│   └── utils/
│       └── distance.py        # Distance calculations
├── frontend/
│   ├── index.html            # Main HTML page
│   ├── css/
│   │   └── styles.css        # Styling
│   └── js/
│       └── app.js           # Frontend logic
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## Technologies Used

- **Backend**: Python, Flask, Flask-CORS, Requests
- **Frontend**: HTML5, CSS3, JavaScript ES6+, Leaflet.js
- **APIs**: OpenStreetMap, Overpass API, OSRM
- **Maps**: OpenStreetMap tiles

## License

MIT License
