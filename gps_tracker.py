"""
GPS and Location Tracking Module
Track inspection locations and generate maps
"""

import sqlite3
import json
from datetime import datetime
import math

class GPSTracker:
    """
    Track and manage GPS locations for inspections
    """
    
    def __init__(self, db_path='crack_detection.db'):
        self.db_path = db_path
    
    def add_gps_to_inspection(self, inspection_id, latitude, longitude, altitude=None, accuracy=None):
        """
        Add GPS coordinates to an inspection
        
        Args:
            inspection_id (int): Inspection ID
            latitude (float): Latitude
            longitude (float): Longitude
            altitude (float, optional): Altitude in meters
            accuracy (float, optional): GPS accuracy in meters
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''UPDATE inspections 
                     SET gps_latitude = ?, gps_longitude = ?
                     WHERE id = ?''',
                  (latitude, longitude, inspection_id))
        
        conn.commit()
        conn.close()
    
    def get_nearby_inspections(self, latitude, longitude, radius_km=1.0):
        """
        Find inspections within radius
        
        Args:
            latitude (float): Center latitude
            longitude (float): Center longitude
            radius_km (float): Search radius in kilometers
            
        Returns:
            list: Nearby inspections
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''SELECT i.*, p.prediction, p.confidence
                     FROM inspections i
                     LEFT JOIN predictions p ON i.prediction_id = p.id
                     WHERE i.gps_latitude IS NOT NULL 
                     AND i.gps_longitude IS NOT NULL''')
        
        all_inspections = c.fetchall()
        conn.close()
        
        nearby = []
        for inspection in all_inspections:
            if len(inspection) > 10:
                insp_lat = inspection[10]
                insp_lon = inspection[11]
                
                if insp_lat and insp_lon:
                    distance = self.calculate_distance(latitude, longitude, insp_lat, insp_lon)
                    if distance <= radius_km:
                        nearby.append({
                            'inspection': inspection,
                            'distance_km': round(distance, 2)
                        })
        
        # Sort by distance
        nearby.sort(key=lambda x: x['distance_km'])
        
        return nearby
    
    def calculate_distance(self, lat1, lon1, lat2, lon2):
        """
        Calculate distance between two GPS coordinates using Haversine formula
        
        Args:
            lat1, lon1: First coordinate
            lat2, lon2: Second coordinate
            
        Returns:
            float: Distance in kilometers
        """
        R = 6371  # Earth's radius in kilometers
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        distance = R * c
        return distance
    
    def get_inspection_cluster_map(self, project_id=None):
        """
        Get all inspections for map visualization
        
        Args:
            project_id (int, optional): Filter by project
            
        Returns:
            dict: Map data with clusters
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        if project_id:
            c.execute('''SELECT i.*, p.prediction, p.confidence, s.name as site_name
                         FROM inspections i
                         LEFT JOIN predictions p ON i.prediction_id = p.id
                         LEFT JOIN sites s ON i.site_id = s.id
                         WHERE i.project_id = ?
                         AND i.gps_latitude IS NOT NULL 
                         AND i.gps_longitude IS NOT NULL''', (project_id,))
        else:
            c.execute('''SELECT i.*, p.prediction, p.confidence, s.name as site_name
                         FROM inspections i
                         LEFT JOIN predictions p ON i.prediction_id = p.id
                         LEFT JOIN sites s ON i.site_id = s.id
                         WHERE i.gps_latitude IS NOT NULL 
                         AND i.gps_longitude IS NOT NULL''')
        
        inspections = c.fetchall()
        conn.close()
        
        # Prepare map data
        map_data = {
            'markers': [],
            'center': {'lat': 0, 'lng': 0},
            'bounds': {'north': -90, 'south': 90, 'east': -180, 'west': 180}
        }
        
        if not inspections:
            return map_data
        
        total_lat = 0
        total_lon = 0
        
        for inspection in inspections:
            lat = inspection[10]
            lon = inspection[11]
            severity = inspection[7]
            
            if lat and lon:
                # Determine marker color based on severity
                color = self._get_severity_color(severity)
                
                marker = {
                    'lat': lat,
                    'lng': lon,
                    'inspection_id': inspection[0],
                    'severity': severity,
                    'confidence': inspection[17] if len(inspection) > 17 else 0,
                    'date': inspection[6],
                    'site_name': inspection[19] if len(inspection) > 19 else 'Unknown',
                    'color': color
                }
                
                map_data['markers'].append(marker)
                
                total_lat += lat
                total_lon += lon
                
                # Update bounds
                map_data['bounds']['north'] = max(map_data['bounds']['north'], lat)
                map_data['bounds']['south'] = min(map_data['bounds']['south'], lat)
                map_data['bounds']['east'] = max(map_data['bounds']['east'], lon)
                map_data['bounds']['west'] = min(map_data['bounds']['west'], lon)
        
        # Calculate center
        count = len(map_data['markers'])
        if count > 0:
            map_data['center'] = {
                'lat': total_lat / count,
                'lng': total_lon / count
            }
        
        return map_data
    
    def _get_severity_color(self, severity):
        """Get marker color based on severity"""
        colors = {
            'SAFE': '#10b981',
            'LOW': '#3b82f6',
            'MEDIUM': '#f59e0b',
            'HIGH': '#ef4444',
            'CRITICAL': '#7f1d1d'
        }
        return colors.get(severity, '#6b7280')
    
    def generate_heatmap_data(self, project_id=None):
        """
        Generate heatmap data for crack density visualization
        
        Args:
            project_id (int, optional): Filter by project
            
        Returns:
            list: Heatmap points with weights
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        if project_id:
            c.execute('''SELECT gps_latitude, gps_longitude, severity_level, crack_width
                         FROM inspections
                         WHERE project_id = ?
                         AND gps_latitude IS NOT NULL 
                         AND gps_longitude IS NOT NULL''', (project_id,))
        else:
            c.execute('''SELECT gps_latitude, gps_longitude, severity_level, crack_width
                         FROM inspections
                         WHERE gps_latitude IS NOT NULL 
                         AND gps_longitude IS NOT NULL''')
        
        inspections = c.fetchall()
        conn.close()
        
        heatmap_data = []
        
        for inspection in inspections:
            lat, lon, severity, crack_width = inspection
            
            # Calculate weight based on severity and crack width
            severity_weights = {'SAFE': 0, 'LOW': 1, 'MEDIUM': 2, 'HIGH': 3, 'CRITICAL': 4}
            weight = severity_weights.get(severity, 1)
            
            if crack_width:
                weight += crack_width / 2  # Add crack width contribution
            
            heatmap_data.append({
                'lat': lat,
                'lng': lon,
                'weight': weight
            })
        
        return heatmap_data
    
    def get_location_statistics(self, project_id=None):
        """
        Get statistics about inspection locations
        
        Args:
            project_id (int, optional): Filter by project
            
        Returns:
            dict: Location statistics
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        if project_id:
            c.execute('''SELECT COUNT(*), 
                         AVG(gps_latitude), AVG(gps_longitude),
                         MIN(gps_latitude), MAX(gps_latitude),
                         MIN(gps_longitude), MAX(gps_longitude)
                         FROM inspections
                         WHERE project_id = ?
                         AND gps_latitude IS NOT NULL''', (project_id,))
        else:
            c.execute('''SELECT COUNT(*), 
                         AVG(gps_latitude), AVG(gps_longitude),
                         MIN(gps_latitude), MAX(gps_latitude),
                         MIN(gps_longitude), MAX(gps_longitude)
                         FROM inspections
                         WHERE gps_latitude IS NOT NULL''')
        
        stats = c.fetchone()
        conn.close()
        
        if stats and stats[0] > 0:
            # Calculate coverage area
            lat_range = stats[4] - stats[3]
            lon_range = stats[6] - stats[5]
            
            # Approximate area in km² (rough estimate)
            area_km2 = lat_range * lon_range * 111 * 111 * math.cos(math.radians(stats[1]))
            
            return {
                'total_inspections': stats[0],
                'center_lat': round(stats[1], 6),
                'center_lng': round(stats[2], 6),
                'coverage_area_km2': round(area_km2, 2),
                'lat_range': round(lat_range, 4),
                'lng_range': round(lon_range, 4)
            }
        
        return {
            'total_inspections': 0,
            'center_lat': 0,
            'center_lng': 0,
            'coverage_area_km2': 0
        }
    
    def export_to_kml(self, project_id, output_file='inspections.kml'):
        """
        Export inspections to KML format for Google Earth
        
        Args:
            project_id (int): Project ID
            output_file (str): Output file path
            
        Returns:
            str: KML content
        """
        map_data = self.get_inspection_cluster_map(project_id)
        
        kml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>Crack Inspections</name>
    <description>Inspection locations from CrackDetect AI</description>
'''
        
        for marker in map_data['markers']:
            kml_content += f'''
    <Placemark>
      <name>{marker['site_name']}</name>
      <description>
        Severity: {marker['severity']}
        Confidence: {marker['confidence']}%
        Date: {marker['date']}
      </description>
      <Point>
        <coordinates>{marker['lng']},{marker['lat']},0</coordinates>
      </Point>
    </Placemark>
'''
        
        kml_content += '''
  </Document>
</kml>
'''
        
        with open(output_file, 'w') as f:
            f.write(kml_content)
        
        return kml_content


# Example usage
if __name__ == '__main__':
    gps = GPSTracker()
    
    print("GPS Tracker Initialized")
    print("="*50)
    print("\nFeatures:")
    print("  • Add GPS to inspections")
    print("  • Find nearby inspections")
    print("  • Calculate distances")
    print("  • Generate map clusters")
    print("  • Create heatmaps")
    print("  • Export to KML (Google Earth)")
    print("  • Location statistics")
