import requests
import logging
from utils.distance import calculate_distance

logger = logging.getLogger(__name__)

class HospitalService:
    """Service for finding hospitals using OpenStreetMap Overpass API"""
    
    def __init__(self):
        self.overpass_url = "https://overpass-api.de/api/interpreter"
        self.search_radius = 5000  # 5km radius
    
    def find_nearest_hospital(self, lat, lng):
        """Find the nearest hospital to given coordinates"""
        try:
            # Get hospitals within radius
            hospitals = self._search_hospitals(lat, lng)
            if not hospitals:
                logger.warning(f"No hospitals found near {lat}, {lng}")
                return None
            
            # Calculate distances and find nearest
            nearest_hospital = None
            min_distance = float('inf')
            
            for hospital in hospitals:
                distance = calculate_distance(lat, lng, hospital['lat'], hospital['lng'])
                hospital['distance'] = distance
                
                if distance < min_distance:
                    min_distance = distance
                    nearest_hospital = hospital
            
            logger.info(f"Found {len(hospitals)} hospitals, nearest: {nearest_hospital['name']}")
            return nearest_hospital
            
        except Exception as e:
            logger.error(f"Error finding hospitals: {e}")
            return None
    
    def _search_hospitals(self, lat, lng):
        """Search for hospitals using Overpass API"""
        try:
            # Overpass query to find hospitals within radius
            query = f"""
            [out:json][timeout:25];
            (
              node["amenity"="hospital"](around:{self.search_radius},{lat},{lng});
              way["amenity"="hospital"](around:{self.search_radius},{lat},{lng});
              relation["amenity"="hospital"](around:{self.search_radius},{lat},{lng});
            );
            out center meta;
            """
            
            response = requests.post(
                self.overpass_url,
                data=query,
                timeout=30,
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            response.raise_for_status()
            
            data = response.json()
            hospitals = []
            
            for element in data.get('elements', []):
                hospital = self._parse_hospital_element(element)
                if hospital:
                    hospitals.append(hospital)
            
            return hospitals
            
        except requests.RequestException as e:
            logger.error(f"Overpass API request failed: {e}")
            return []
        except Exception as e:
            logger.error(f"Error parsing hospital data: {e}")
            return []
    
    def _parse_hospital_element(self, element):
        """Parse hospital element from Overpass API response"""
        try:
            # Get coordinates
            if element['type'] == 'node':
                lat = element['lat']
                lng = element['lon']
            elif 'center' in element:
                lat = element['center']['lat']
                lng = element['center']['lon']
            else:
                return None
            
            # Get hospital name
            tags = element.get('tags', {})
            name = (tags.get('name') or 
                   tags.get('name:en') or 
                   tags.get('operator') or 
                   'Unknown Hospital')
            
            # Get address
            address_parts = []
            if tags.get('addr:street'):
                address_parts.append(tags['addr:street'])
            if tags.get('addr:city'):
                address_parts.append(tags['addr:city'])
            
            address = ', '.join(address_parts) if address_parts else 'Address not available'
            
            return {
                'name': name,
                'lat': lat,
                'lng': lng,
                'address': address,
                'type': tags.get('healthcare', 'hospital')
            }
            
        except Exception as e:
            logger.error(f"Error parsing hospital element: {e}")
            return None