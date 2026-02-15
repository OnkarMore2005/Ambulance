import requests
import logging

logger = logging.getLogger(__name__)

class RoutingService:
    """Service for calculating routes using OSRM API"""
    
    def __init__(self):
        self.osrm_url = "https://router.project-osrm.org/route/v1/driving"
    
    def get_route(self, start_lat, start_lng, end_lat, end_lng):
        """Get driving route between two points"""
        try:
            # OSRM expects longitude,latitude format
            coordinates = f"{start_lng},{start_lat};{end_lng},{end_lat}"
            
            # Request route with full geometry
            url = f"{self.osrm_url}/{coordinates}"
            params = {
                'overview': 'full',
                'geometries': 'geojson',
                'steps': 'false'
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('code') != 'Ok':
                logger.error(f"OSRM routing failed: {data.get('message', 'Unknown error')}")
                return None
            
            routes = data.get('routes', [])
            if not routes:
                logger.error("No routes found")
                return None
            
            # Extract route coordinates
            geometry = routes[0].get('geometry', {})
            coordinates = geometry.get('coordinates', [])
            
            # Convert from [lng, lat] to [lat, lng] format
            route_points = [[coord[1], coord[0]] for coord in coordinates]
            
            logger.info(f"Route calculated with {len(route_points)} points")
            return route_points
            
        except requests.RequestException as e:
            logger.error(f"OSRM API request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Error calculating route: {e}")
            return None