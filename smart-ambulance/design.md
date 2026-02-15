# Design Document
## AI-Based Smart Ambulance Routing System

### Document Information
**Version**: 1.0  
**Date**: January 30, 2026  
**Project**: Smart Ambulance Routing System  
**Target Hackathon**: AI for Bharat 2026

---

## 1. Executive Summary

### 1.1 Project Vision
Create an intelligent, real-time ambulance routing system that leverages geospatial AI and routing algorithms to minimize emergency response times and save lives across India.

### 1.2 Design Philosophy
- **Simplicity**: Clean, intuitive interface requiring zero training
- **Speed**: Sub-5-second response time for critical operations
- **Reliability**: Graceful degradation and comprehensive error handling
- **Accessibility**: Free, open-source, and universally accessible
- **Scalability**: Modular architecture supporting future enhancements

### 1.3 Key Innovation
Integration of real-time geospatial data processing with intelligent routing algorithms to provide instant, optimal emergency healthcare navigation.

---

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                        │
│  ┌──────────────────┐              ┌──────────────────┐    │
│  │  Control Panel   │              │   Map Display    │    │
│  │  - Emergency Btn │              │  - Leaflet.js    │    │
│  │  - Status Info   │              │  - Markers       │    │
│  │  - Hospital Data │              │  - Route Line    │    │
│  └──────────────────┘              └──────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP/JSON
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      FLASK BACKEND API                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              app.py (Main Controller)                 │  │
│  │  - Health Check Endpoint (GET /)                     │  │
│  │  - Emergency Endpoint (POST /emergency)              │  │
│  │  - Input Validation & Error Handling                 │  │
│  └──────────────────────────────────────────────────────┘  │
│                            │                                 │
│         ┌──────────────────┴──────────────────┐            │
│         ▼                                      ▼            │
│  ┌──────────────────┐              ┌──────────────────┐   │
│  │ Hospital Service │              │ Routing Service  │   │
│  │  - Search Logic  │              │  - OSRM API      │   │
│  │  - Overpass API  │              │  - Route Calc    │   │
│  │  - Distance Calc │              │  - Coord Convert │   │
│  └──────────────────┘              └──────────────────┘   │
│         │                                      │            │
│         └──────────────────┬──────────────────┘            │
│                            ▼                                 │
│                  ┌──────────────────┐                       │
│                  │  Distance Utils  │                       │
│                  │  - Haversine     │                       │
│                  └──────────────────┘                       │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTPS
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    EXTERNAL SERVICES                         │
│  ┌──────────────────┐              ┌──────────────────┐    │
│  │  Overpass API    │              │    OSRM API      │    │
│  │  - Hospital Data │              │  - Route Data    │    │
│  └──────────────────┘              └──────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Architecture Patterns
- **Pattern**: Model-Service-Controller (MSC)
- **Communication**: RESTful API with JSON
- **State Management**: Stateless backend, client-side state
- **Error Handling**: Centralized with graceful degradation

---

## 3. Component Design

### 3.1 Frontend Components

#### 3.1.1 Control Panel Component
**Purpose**: User interaction and information display

**Structure**:

```
Control Panel
├── Header Section
│   ├── Title: "Emergency Control"
│   └── Subtitle: System description
├── Emergency Section
│   ├── Emergency Button (Primary CTA)
│   ├── Loading Spinner (conditional)
│   └── Status Message (dynamic)
├── Info Section
│   ├── Current Location Card
│   └── Hospital Info Card (conditional)
└── Footer Section
    └── Copyright & Info
```

**Key Features**:
- Dark theme with gradient background
- Smooth animations and transitions
- Responsive layout (400px width, scales on mobile)
- Real-time status updates

#### 3.1.2 Map Component
**Purpose**: Visual representation of location and route

**Structure**:
```
Map Panel
├── Leaflet Map Instance
├── OpenStreetMap Tile Layer
├── Ambulance Marker (🚑 emoji icon)
├── Hospital Marker (🏥 emoji icon)
└── Route Polyline (red, 4px weight)
```

**Interactions**:
- Click to set manual location
- Zoom and pan controls
- Auto-fit bounds to route
- Popup information on markers

#### 3.1.3 Application Controller (app.js)
**Purpose**: Orchestrate frontend logic and API communication

**Class Structure**:
```javascript
class SmartAmbulanceApp {
  // Properties
  - map: Leaflet map instance
  - currentLocation: {lat, lng}
  - ambulanceMarker: Leaflet marker
  - hospitalMarker: Leaflet marker
  - routePolyline: Leaflet polyline
  - apiUrl: Backend API URL
  
  // Methods
  + initializeApp()
  + initializeMap()
  + bindEvents()
  + getCurrentLocation()
  + setLocation(lat, lng)
  + handleEmergency()
  + displayResults(data)
  + showHospitalInfo(data)
  + addHospitalMarker(lat, lng, name, address)
  + drawRoute(routePoints)
  + fitMapToRoute(routePoints)
  + updateStatus(message, type)
  + setLoading(isLoading)
}
```

### 3.2 Backend Components

#### 3.2.1 Main Application (app.py)
**Purpose**: API endpoint management and request handling

**Endpoints**:
```python
GET /
  - Health check endpoint
  - Returns: {"status": "healthy", "message": "..."}
  - Status Code: 200

POST /emergency
  - Emergency routing endpoint
  - Input: {"lat": float, "lng": float}
  - Output: {
      "hospital": string,
      "hospitalLat": float,
      "hospitalLng": float,
      "route": [[lat, lng], ...],
      "distance": float,
      "address": string
    }
  - Status Codes: 200 (success), 400 (bad request), 404 (not found), 500 (error)
```

**Error Handlers**:
- 404: Not Found
- 500: Internal Server Error
- Custom exception handling for validation errors

#### 3.2.2 Hospital Service (hospital_service.py)
**Purpose**: Hospital search and selection logic

**Class Structure**:
```python
class HospitalService:
  # Properties
  - overpass_url: Overpass API endpoint
  - search_radius: 5000 meters
  
  # Public Methods
  + find_nearest_hospital(lat, lng) -> dict
    Returns nearest hospital with details
  
  # Private Methods
  - _search_hospitals(lat, lng) -> list
    Query Overpass API for hospitals
  
  - _parse_hospital_element(element) -> dict
    Parse hospital data from API response
```

**Algorithm**:
1. Query Overpass API with circular search area
2. Parse all hospital elements from response
3. Calculate distance to each hospital using Haversine
4. Sort by distance and return nearest

#### 3.2.3 Routing Service (routing_service.py)
**Purpose**: Route calculation using OSRM

**Class Structure**:
```python
class RoutingService:
  # Properties
  - osrm_url: OSRM API endpoint
  
  # Public Methods
  + get_route(start_lat, start_lng, end_lat, end_lng) -> list
    Returns route as array of [lat, lng] coordinates
```

**Algorithm**:
1. Convert coordinates to OSRM format (lng, lat)
2. Request route with full geometry
3. Parse GeoJSON response
4. Convert coordinates back to [lat, lng] format
5. Return route points array

#### 3.2.4 Distance Utility (distance.py)
**Purpose**: Accurate distance calculation

**Function**:
```python
def calculate_distance(lat1, lng1, lat2, lng2) -> float
  # Haversine formula implementation
  # Returns distance in meters
```

**Algorithm**: Haversine Formula
```
a = sin²(Δlat/2) + cos(lat1) × cos(lat2) × sin²(Δlng/2)
c = 2 × atan2(√a, √(1−a))
distance = R × c  (where R = 6,371,000 meters)
```

---

## 4. Data Flow Design

### 4.1 Emergency Request Flow

```
User Action: Click Emergency Button
         │
         ▼
[1] Get Current Location
    - Check if location available
    - If not, show error
         │
         ▼
[2] Send POST Request to /emergency
    - Payload: {lat, lng}
    - Show loading spinner
    - Disable button
         │
         ▼
[3] Backend: Validate Input
    - Check lat/lng format
    - Validate coordinate ranges
    - Return 400 if invalid
         │
         ▼
[4] Backend: Search Hospitals
    - Query Overpass API
    - Parse hospital data
    - Calculate distances
    - Find nearest hospital
    - Return 404 if none found
         │
         ▼
[5] Backend: Calculate Route
    - Query OSRM API
    - Parse route geometry
    - Convert coordinates
    - Return 500 if routing fails
         │
         ▼
[6] Backend: Return Response
    - Compile hospital + route data
    - Return JSON response
         │
         ▼
[7] Frontend: Display Results
    - Update status message
    - Show hospital info card
    - Add hospital marker
    - Draw route polyline
    - Fit map bounds
    - Hide loading spinner
    - Enable button
```

### 4.2 Data Models

#### 4.2.1 Location Model
```json
{
  "lat": 40.7128,
  "lng": -74.0060
}
```

#### 4.2.2 Hospital Model
```json
{
  "name": "City General Hospital",
  "lat": 40.7589,
  "lng": -73.9851,
  "address": "123 Hospital St, New York, NY",
  "distance": 2500.5,
  "type": "hospital"
}
```

#### 4.2.3 Route Model
```json
{
  "route": [
    [40.7128, -74.0060],
    [40.7150, -74.0045],
    [40.7589, -73.9851]
  ]
}
```

#### 4.2.4 Emergency Response Model
```json
{
  "hospital": "City General Hospital",
  "hospitalLat": 40.7589,
  "hospitalLng": -73.9851,
  "route": [[40.7128, -74.0060], ...],
  "distance": 2500.5,
  "address": "123 Hospital St, New York, NY"
}
```

---

## 5. User Interface Design

### 5.1 Layout Design

**Desktop Layout** (1920x1080):
```
┌────────────────────────────────────────────────────────┐
│  Control Panel (400px)  │    Map Panel (flex: 1)      │
│  ┌──────────────────┐   │  ┌────────────────────────┐ │
│  │     Header       │   │  │                        │ │
│  └──────────────────┘   │  │                        │ │
│  ┌──────────────────┐   │  │      Leaflet Map       │ │
│  │  Emergency Btn   │   │  │                        │ │
│  │  Status/Loading  │   │  │    (Markers + Route)   │ │
│  └──────────────────┘   │  │                        │ │
│  ┌──────────────────┐   │  │                        │ │
│  │ Current Location │   │  │                        │ │
│  └──────────────────┘   │  └────────────────────────┘ │
│  ┌──────────────────┐   │                             │
│  │  Hospital Info   │   │                             │
│  └──────────────────┘   │                             │
│  ┌──────────────────┐   │                             │
│  │     Footer       │   │                             │
│  └──────────────────┘   │                             │
└────────────────────────────────────────────────────────┘
```

**Mobile Layout** (375x667):
```
┌─────────────────────┐
│   Control Panel     │
│   (50vh height)     │
│  ┌───────────────┐  │
│  │    Header     │  │
│  ├───────────────┤  │
│  │ Emergency Btn │  │
│  ├───────────────┤  │
│  │ Status/Info   │  │
│  └───────────────┘  │
├─────────────────────┤
│    Map Panel        │
│   (50vh height)     │
│  ┌───────────────┐  │
│  │               │  │
│  │  Leaflet Map  │  │
│  │               │  │
│  └───────────────┘  │
└─────────────────────┘
```

### 5.2 Color Scheme

**Primary Colors**:
- Background Gradient: `#1e3c72` → `#2a5298` (Blue gradient)
- Control Panel: `rgba(30, 30, 30, 0.95)` (Dark with transparency)
- Emergency Button: `#ff6b6b` → `#ee5a24` (Red-orange gradient)
- Accent Color: `#4ecdc4` (Teal)

**Status Colors**:
- Success: `#2ecc71` (Green)
- Error: `#e74c3c` (Red)
- Info: `#4ecdc4` (Teal)
- Warning: `#f39c12` (Orange)

**Text Colors**:
- Primary Text: `#ffffff` (White)
- Secondary Text: `rgba(255, 255, 255, 0.7)` (70% white)
- Muted Text: `rgba(255, 255, 255, 0.5)` (50% white)

### 5.3 Typography

**Font Family**: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif

**Font Sizes**:
- H1 (Main Title): 1.8rem (28.8px)
- H3 (Card Titles): 1rem (16px)
- Body Text: 0.9rem (14.4px)
- Button Text: 1.2rem (19.2px)
- Small Text: 0.8rem (12.8px)

**Font Weights**:
- Headers: 700 (Bold)
- Buttons: 700 (Bold)
- Body: 400 (Regular)
- Hospital Name: 600 (Semi-bold)

### 5.4 Component Styling

#### Emergency Button
```css
- Size: Full width × 1.5rem padding
- Background: Linear gradient (red-orange)
- Border Radius: 12px
- Box Shadow: 0 8px 25px rgba(255, 107, 107, 0.3)
- Hover: translateY(-2px) + enhanced shadow
- Active: translateY(0)
- Disabled: opacity 0.6
```

#### Info Cards
```css
- Background: rgba(255, 255, 255, 0.1)
- Border: 1px solid rgba(255, 255, 255, 0.1)
- Border Radius: 12px
- Padding: 1.5rem
- Backdrop Filter: blur(5px)
```

#### Loading Spinner
```css
- Size: 20px × 20px
- Border: 2px solid rgba(255, 255, 255, 0.3)
- Border Top: 2px solid #4ecdc4
- Animation: 360° rotation in 1s (infinite)
```

### 5.5 Animations

**Button Pulse** (Emergency Icon):
```css
@keyframes pulse {
  0%, 100%: scale(1)
  50%: scale(1.1)
}
Duration: 2s infinite
```

**Spinner Rotation**:
```css
@keyframes spin {
  0%: rotate(0deg)
  100%: rotate(360deg)
}
Duration: 1s linear infinite
```

**Hover Transitions**:
- Duration: 0.3s
- Easing: ease
- Properties: transform, box-shadow

---

## 6. API Integration Design

### 6.1 Overpass API Integration

**Endpoint**: `https://overpass-api.de/api/interpreter`

**Query Structure**:
```overpass
[out:json][timeout:25];
(
  node["amenity"="hospital"](around:5000,{lat},{lng});
  way["amenity"="hospital"](around:5000,{lat},{lng});
  relation["amenity"="hospital"](around:5000,{lat},{lng});
);
out center meta;
```

**Request Configuration**:
- Method: POST
- Content-Type: application/x-www-form-urlencoded
- Timeout: 30 seconds

**Response Parsing**:
```python
elements = response.json()['elements']
for element in elements:
    if element['type'] == 'node':
        lat, lng = element['lat'], element['lon']
    elif 'center' in element:
        lat, lng = element['center']['lat'], element['center']['lon']
    
    name = element['tags'].get('name', 'Unknown Hospital')
    address = build_address(element['tags'])
```

### 6.2 OSRM API Integration

**Endpoint**: `https://router.project-osrm.org/route/v1/driving/{lng1},{lat1};{lng2},{lat2}`

**Query Parameters**:
- `overview=full`: Return complete route geometry
- `geometries=geojson`: GeoJSON format for coordinates
- `steps=false`: Skip turn-by-turn instructions

**Request Configuration**:
- Method: GET
- Timeout: 30 seconds

**Response Parsing**:
```python
routes = response.json()['routes']
geometry = routes[0]['geometry']
coordinates = geometry['coordinates']  # [[lng, lat], ...]

# Convert to [lat, lng] format
route_points = [[coord[1], coord[0]] for coord in coordinates]
```

### 6.3 Error Handling Strategy

**Overpass API Errors**:
- Timeout: Retry once, then return error
- No results: Return 404 with message
- Invalid query: Log error, return 500
- Network error: Return 500 with generic message

**OSRM API Errors**:
- Timeout: Return error immediately
- Invalid coordinates: Return 400
- No route found: Return 500 with message
- Network error: Return 500

**Frontend Error Handling**:
- Network errors: Display "Connection failed" message
- 400 errors: Display "Invalid location" message
- 404 errors: Display "No hospitals found nearby"
- 500 errors: Display "Service temporarily unavailable"

---

## 7. Performance Optimization

### 7.1 Frontend Optimizations

**Map Performance**:
- Lazy load Leaflet.js library
- Use tile caching (browser default)
- Limit route polyline points if > 1000
- Debounce map interactions

**Asset Optimization**:
- Minify CSS and JavaScript (production)
- Use CDN for Leaflet.js
- Compress images (if any added)
- Enable browser caching

**Rendering Optimization**:
- Use CSS transforms for animations (GPU-accelerated)
- Minimize DOM manipulations
- Use event delegation where possible
- Lazy render hospital info card

### 7.2 Backend Optimizations

**API Call Optimization**:
- Set appropriate timeouts (30s)
- Implement connection pooling
- Cache frequently accessed data (future)
- Parallel API calls where possible

**Response Optimization**:
- Minimize JSON payload size
- Compress responses (gzip)
- Return only necessary data
- Use efficient data structures

**Code Optimization**:
- Use list comprehensions (Python)
- Avoid unnecessary loops
- Efficient coordinate conversion
- Proper exception handling

### 7.3 Network Optimization

**Request Optimization**:
- Single API call for complete workflow
- Minimize request payload
- Use HTTP/2 (production)
- Enable CORS preflight caching

**Response Optimization**:
- Compress responses
- Set appropriate cache headers
- Minimize response size
- Use efficient JSON serialization

---

## 8. Security Design

### 8.1 Input Validation

**Coordinate Validation**:
```python
def validate_coordinates(lat, lng):
    if not isinstance(lat, (int, float)):
        raise ValueError("Latitude must be numeric")
    if not isinstance(lng, (int, float)):
        raise ValueError("Longitude must be numeric")
    if not -90 <= lat <= 90:
        raise ValueError("Latitude out of range")
    if not -180 <= lng <= 180:
        raise ValueError("Longitude out of range")
```

**Request Validation**:
- Check Content-Type header
- Validate JSON structure
- Sanitize all inputs
- Limit request size

### 8.2 API Security

**CORS Configuration**:
```python
CORS(app, resources={
    r"/*": {
        "origins": "*",  # Restrict in production
        "methods": ["GET", "POST"],
        "allow_headers": ["Content-Type"]
    }
})
```

**Rate Limiting** (Future):
- Implement per-IP rate limiting
- Max 60 requests per minute
- Return 429 if exceeded

### 8.3 Data Security

**Privacy Protection**:
- No location data storage
- No user tracking
- No cookies or sessions
- No personal data collection

**API Key Protection**:
- No API keys required (by design)
- All services are public
- No sensitive credentials

---

## 9. Testing Strategy

### 9.1 Unit Testing

**Backend Tests**:
```python
# test_distance.py
def test_calculate_distance():
    # Test known distances
    assert calculate_distance(0, 0, 0, 1) ≈ 111,320 meters

# test_hospital_service.py
def test_parse_hospital_element():
    # Test element parsing
    element = {...}
    hospital = service._parse_hospital_element(element)
    assert hospital['name'] is not None

# test_routing_service.py
def test_get_route():
    # Test route calculation
    route = service.get_route(40.7, -74.0, 40.8, -73.9)
    assert len(route) > 0
```

**Frontend Tests**:
```javascript
// test_app.js
describe('SmartAmbulanceApp', () => {
  test('initializes map correctly', () => {
    const app = new SmartAmbulanceApp();
    expect(app.map).toBeDefined();
  });
  
  test('validates location', () => {
    const app = new SmartAmbulanceApp();
    app.setLocation(40.7, -74.0);
    expect(app.currentLocation).toEqual({lat: 40.7, lng: -74.0});
  });
});
```

### 9.2 Integration Testing

**API Integration Tests**:
- Test Overpass API connectivity
- Test OSRM API connectivity
- Test error handling for API failures
- Test timeout scenarios

**End-to-End Tests**:
- Test complete emergency workflow
- Test with various locations
- Test error scenarios
- Test on different browsers

### 9.3 Performance Testing

**Load Testing**:
- Simulate 100 concurrent users
- Measure response times
- Identify bottlenecks
- Test API rate limits

**Stress Testing**:
- Test with invalid inputs
- Test with extreme coordinates
- Test with network failures
- Test with API timeouts

---

## 10. Deployment Architecture

### 10.1 Development Deployment

```
Local Machine
├── Backend: Flask dev server (port 5000)
│   └── Auto-reload enabled
└── Frontend: Python HTTP server (port 8000)
    └── Serves static files
```

### 10.2 Production Deployment (Future)

```
Cloud Infrastructure (AWS/Azure/GCP)
├── Load Balancer
│   └── SSL Termination
├── Web Server (Nginx)
│   ├── Static file serving (frontend)
│   └── Reverse proxy to backend
├── Application Server (Gunicorn)
│   ├── Multiple worker processes
│   └── Flask application
└── Monitoring & Logging
    ├── Application logs
    ├── Error tracking
    └── Performance metrics
```

### 10.3 Scalability Design

**Horizontal Scaling**:
- Stateless backend (easy to replicate)
- Load balancer distribution
- Multiple application instances
- CDN for static assets

**Vertical Scaling**:
- Increase server resources
- Optimize database queries (if added)
- Cache frequently accessed data
- Upgrade network bandwidth

---

## 11. Monitoring and Logging

### 11.1 Logging Strategy

**Backend Logging**:
```python
# Log Levels
- INFO: Normal operations (requests, responses)
- WARNING: Unusual but handled situations
- ERROR: Errors that need attention
- DEBUG: Detailed diagnostic information

# Log Format
[TIMESTAMP] [LEVEL] [MODULE] Message
```

**Log Examples**:
```
INFO:app:Emergency request at coordinates: 40.7128, -74.0060
INFO:hospital_service:Found 5 hospitals, nearest: City General
ERROR:routing_service:OSRM API request failed: Timeout
```

### 11.2 Error Tracking

**Error Categories**:
- Input validation errors
- External API errors
- Network errors
- Unexpected exceptions

**Error Response Format**:
```json
{
  "error": "Human-readable error message",
  "code": "ERROR_CODE",
  "timestamp": "2026-01-30T10:30:00Z"
}
```

### 11.3 Performance Monitoring

**Key Metrics**:
- Request response time
- API call duration
- Error rate
- Success rate
- Concurrent users

**Monitoring Tools** (Future):
- Application Performance Monitoring (APM)
- Log aggregation (ELK stack)
- Real-time dashboards
- Alert system

---

## 12. Future Enhancements

### 12.1 AI/ML Integration

**Phase 1: Intelligent Hospital Selection**
```
Algorithm: Multi-criteria Decision Making
Factors:
- Distance (weight: 40%)
- Hospital capacity (weight: 20%)
- Specialization match (weight: 20%)
- Historical response time (weight: 20%)

Implementation:
- Collect hospital metadata
- Train ML model on historical data
- Implement scoring algorithm
- A/B test against current system
```

**Phase 2: Traffic Prediction**
```
Algorithm: Time-series Forecasting (LSTM)
Data Sources:
- Historical traffic patterns
- Real-time traffic APIs
- Weather data
- Event calendars

Implementation:
- Collect training data
- Train LSTM model
- Integrate with routing service
- Adjust routes based on predictions
```

**Phase 3: Emergency Classification**
```
Algorithm: Natural Language Processing
Input: Emergency description (text/voice)
Output: Emergency type, severity, required specialization

Implementation:
- Build emergency taxonomy
- Train NLP model (BERT/GPT)
- Integrate voice recognition
- Match to hospital specializations
```

### 12.2 Advanced Features

**Real-time Tracking**:
- WebSocket connection for live updates
- Ambulance location streaming
- ETA calculation and updates
- Hospital notification system

**Multi-hospital Display**:
- Show top 3 nearest hospitals
- Compare distances and routes
- Display hospital ratings
- Show bed availability

**Offline Capability**:
- Cache map tiles for offline use
- Store hospital database locally
- Fallback routing algorithm
- Sync when online

**Mobile Application**:
- Native iOS/Android apps
- Push notifications
- Background location tracking
- Offline maps

### 12.3 Integration Opportunities

**Hospital Management Systems**:
- Real-time bed availability
- Emergency department status
- Specialist availability
- Direct admission coordination

**Emergency Services**:
- Integration with 108/102 services
- Automated dispatch system
- Multi-ambulance coordination
- Resource optimization

**Government Databases**:
- Verified hospital registry
- Accreditation status
- Equipment availability
- Quality ratings

---

## 13. Accessibility Design

### 13.1 WCAG Compliance

**Level AA Requirements**:
- Color contrast ratio ≥ 4.5:1 for text
- Keyboard navigation support
- Screen reader compatibility
- Focus indicators visible
- Alternative text for images

**Implementation**:
```html
<!-- Semantic HTML -->
<button aria-label="Emergency: Find nearest hospital">
  EMERGENCY
</button>

<!-- ARIA attributes -->
<div role="status" aria-live="polite">
  Searching for nearest hospital...
</div>

<!-- Keyboard navigation -->
<div tabindex="0" role="button">
  Map marker
</div>
```

### 13.2 Responsive Design

**Breakpoints**:
- Mobile: 320px - 767px
- Tablet: 768px - 1023px
- Desktop: 1024px+

**Responsive Behavior**:
- Stack layout vertically on mobile
- Adjust font sizes proportionally
- Touch-friendly button sizes (min 44px)
- Simplified navigation on small screens

---

## 14. Documentation Standards

### 14.1 Code Documentation

**Python Docstrings**:
```python
def find_nearest_hospital(self, lat, lng):
    """
    Find the nearest hospital to given coordinates.
    
    Args:
        lat (float): Latitude of current location
        lng (float): Longitude of current location
    
    Returns:
        dict: Hospital information including name, coordinates, address
        None: If no hospitals found
    
    Raises:
        ValueError: If coordinates are invalid
    """
```

**JavaScript Comments**:
```javascript
/**
 * Handle emergency button click
 * Triggers hospital search and route calculation
 * @async
 * @returns {Promise<void>}
 */
async handleEmergency() {
  // Implementation
}
```

### 14.2 API Documentation

**Endpoint Documentation Format**:
```markdown
### POST /emergency

Find nearest hospital and calculate route.

**Request Body:**
{
  "lat": 40.7128,
  "lng": -74.0060
}

**Success Response (200):**
{
  "hospital": "City General Hospital",
  "hospitalLat": 40.7589,
  "hospitalLng": -73.9851,
  "route": [[40.7128, -74.0060], ...],
  "distance": 2500.5,
  "address": "123 Hospital St"
}

**Error Responses:**
- 400: Invalid coordinates
- 404: No hospitals found
- 500: Internal server error
```

---

## 15. Quality Assurance

### 15.1 Code Quality Standards

**Python (PEP 8)**:
- 4 spaces for indentation
- Max line length: 79 characters
- Snake_case for functions/variables
- PascalCase for classes

**JavaScript (ES6+)**:
- 2 spaces for indentation
- Semicolons required
- camelCase for functions/variables
- PascalCase for classes

### 15.2 Code Review Checklist

- [ ] Code follows style guidelines
- [ ] All functions have docstrings/comments
- [ ] Error handling implemented
- [ ] Input validation present
- [ ] No hardcoded values
- [ ] Efficient algorithms used
- [ ] Security considerations addressed
- [ ] Tests written and passing

---

## Document Control

**Version History**:
- v1.0 (2026-01-30): Initial design document

**Approval**:
- Technical Lead: Approved
- UI/UX Designer: Approved
- Security Review: Approved

**Next Review**: February 28, 2026