class SmartAmbulanceApp {
    constructor() {
        this.map = null;
        this.currentLocation = null;
        this.ambulanceMarker = null;
        this.hospitalMarker = null;
        this.routePolyline = null;
        this.apiUrl = 'http://localhost:5000';
        
        this.initializeApp();
    }
    
    initializeApp() {
        this.initializeMap();
        this.bindEvents();
        this.getCurrentLocation();
    }
    
    initializeMap() {
        // Initialize Leaflet map
        this.map = L.map('map').setView([40.7128, -74.0060], 13);
        
        // Add OpenStreetMap tiles
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 19
        }).addTo(this.map);
        
        // Add map click handler for manual location setting
        this.map.on('click', (e) => {
            this.setLocation(e.latlng.lat, e.latlng.lng);
        });
    }
    
    bindEvents() {
        const emergencyBtn = document.getElementById('emergencyBtn');
        emergencyBtn.addEventListener('click', () => this.handleEmergency());
    }
    
    getCurrentLocation() {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const lat = position.coords.latitude;
                    const lng = position.coords.longitude;
                    this.setLocation(lat, lng);
                },
                (error) => {
                    console.error('Geolocation error:', error);
                    this.updateStatus('Location access denied. Click on map to set location.', 'error');
                    // Default to New York City
                    this.setLocation(40.7128, -74.0060);
                }
            );
        } else {
            this.updateStatus('Geolocation not supported. Click on map to set location.', 'error');
            this.setLocation(40.7128, -74.0060);
        }
    }
    
    setLocation(lat, lng) {
        this.currentLocation = { lat, lng };
        
        // Update location display
        document.getElementById('currentLocation').textContent = 
            `${lat.toFixed(4)}, ${lng.toFixed(4)}`;
        
        // Add/update ambulance marker
        if (this.ambulanceMarker) {
            this.map.removeLayer(this.ambulanceMarker);
        }
        
        this.ambulanceMarker = L.marker([lat, lng], {
            icon: L.divIcon({
                html: '🚑',
                iconSize: [30, 30],
                className: 'ambulance-marker'
            })
        }).addTo(this.map);
        
        this.ambulanceMarker.bindPopup('Ambulance Location').openPopup();
        
        // Center map on location
        this.map.setView([lat, lng], 13);
    }
    
    async handleEmergency() {
        if (!this.currentLocation) {
            this.updateStatus('Location not available. Please allow location access or click on map.', 'error');
            return;
        }
        
        try {
            this.setLoading(true);
            this.updateStatus('Searching for nearest hospital...', '');
            
            const response = await fetch(`${this.apiUrl}/emergency`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    lat: this.currentLocation.lat,
                    lng: this.currentLocation.lng
                })
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to find hospital');
            }
            
            const data = await response.json();
            this.displayResults(data);
            
        } catch (error) {
            console.error('Emergency request failed:', error);
            this.updateStatus(`Error: ${error.message}`, 'error');
        } finally {
            this.setLoading(false);
        }
    }
    
    displayResults(data) {
        // Update status
        this.updateStatus('Route calculated successfully!', 'success');
        
        // Display hospital information
        this.showHospitalInfo(data);
        
        // Add hospital marker
        this.addHospitalMarker(data.hospitalLat, data.hospitalLng, data.hospital, data.address);
        
        // Draw route
        this.drawRoute(data.route);
        
        // Fit map to show both markers and route
        this.fitMapToRoute(data.route);
    }
    
    showHospitalInfo(data) {
        const hospitalInfo = document.getElementById('hospitalInfo');
        const hospitalName = document.getElementById('hospitalName');
        const hospitalAddress = document.getElementById('hospitalAddress');
        const hospitalDistance = document.getElementById('hospitalDistance');
        
        hospitalName.textContent = data.hospital;
        hospitalAddress.textContent = data.address;
        hospitalDistance.textContent = `Distance: ${(data.distance / 1000).toFixed(2)} km`;
        
        hospitalInfo.classList.remove('hidden');
    }
    
    addHospitalMarker(lat, lng, name, address) {
        // Remove existing hospital marker
        if (this.hospitalMarker) {
            this.map.removeLayer(this.hospitalMarker);
        }
        
        this.hospitalMarker = L.marker([lat, lng], {
            icon: L.divIcon({
                html: '🏥',
                iconSize: [30, 30],
                className: 'hospital-marker'
            })
        }).addTo(this.map);
        
        this.hospitalMarker.bindPopup(`
            <div>
                <strong>${name}</strong><br>
                ${address}
            </div>
        `);
    }
    
    drawRoute(routePoints) {
        // Remove existing route
        if (this.routePolyline) {
            this.map.removeLayer(this.routePolyline);
        }
        
        // Draw new route
        this.routePolyline = L.polyline(routePoints, {
            color: '#ff6b6b',
            weight: 4,
            opacity: 0.8,
            smoothFactor: 1
        }).addTo(this.map);
    }
    
    fitMapToRoute(routePoints) {
        if (routePoints && routePoints.length > 0) {
            const group = new L.featureGroup([this.ambulanceMarker, this.hospitalMarker, this.routePolyline]);
            this.map.fitBounds(group.getBounds().pad(0.1));
        }
    }
    
    updateStatus(message, type = '') {
        const statusElement = document.getElementById('statusMessage');
        statusElement.textContent = message;
        statusElement.className = `status-message ${type}`;
    }
    
    setLoading(isLoading) {
        const emergencyBtn = document.getElementById('emergencyBtn');
        const loadingSpinner = document.getElementById('loadingSpinner');
        const statusMessage = document.getElementById('statusMessage');
        
        emergencyBtn.disabled = isLoading;
        
        if (isLoading) {
            loadingSpinner.classList.remove('hidden');
            statusMessage.classList.add('hidden');
        } else {
            loadingSpinner.classList.add('hidden');
            statusMessage.classList.remove('hidden');
        }
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new SmartAmbulanceApp();
});