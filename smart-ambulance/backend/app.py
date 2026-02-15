from flask import Flask, request, jsonify
from flask_cors import CORS
from services.hospital_service import HospitalService
from services.routing_service import RoutingService
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize services
hospital_service = HospitalService()
routing_service = RoutingService()

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Smart Ambulance Routing System API'
    }), 200

@app.route('/emergency', methods=['POST'])
def handle_emergency():
    """Handle emergency request and find nearest hospital with route"""
    try:
        # Validate request data
        data = request.get_json()
        if not data or 'lat' not in data or 'lng' not in data:
            return jsonify({
                'error': 'Missing required fields: lat, lng'
            }), 400
        
        lat = float(data['lat'])
        lng = float(data['lng'])
        
        # Validate coordinates
        if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
            return jsonify({
                'error': 'Invalid coordinates'
            }), 400
        
        logger.info(f"Emergency request at coordinates: {lat}, {lng}")
        
        # Find nearest hospital
        hospital = hospital_service.find_nearest_hospital(lat, lng)
        if not hospital:
            return jsonify({
                'error': 'No hospitals found in the area'
            }), 404
        
        # Get route to hospital
        route = routing_service.get_route(lat, lng, hospital['lat'], hospital['lng'])
        if not route:
            return jsonify({
                'error': 'Could not calculate route to hospital'
            }), 500
        
        # Return response
        response = {
            'hospital': hospital['name'],
            'hospitalLat': hospital['lat'],
            'hospitalLng': hospital['lng'],
            'route': route,
            'distance': hospital.get('distance', 0),
            'address': hospital.get('address', 'Address not available')
        }
        
        logger.info(f"Found hospital: {hospital['name']}")
        return jsonify(response), 200
        
    except ValueError as e:
        logger.error(f"Invalid input: {e}")
        return jsonify({'error': 'Invalid coordinate format'}), 400
    except Exception as e:
        logger.error(f"Emergency request failed: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)