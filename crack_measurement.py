"""
Crack Measurement Module
Estimate crack width, length, and area using image processing
"""

import numpy as np
from datetime import datetime

class CrackMeasurement:
    """
    Measure crack dimensions from images
    Note: This uses OpenCV for advanced measurements. Install with: pip install opencv-python
    """
    
    def __init__(self):
        try:
            import cv2
            self.cv2 = cv2
            self.opencv_available = True
        except ImportError:
            self.opencv_available = False
            print("Warning: OpenCV not installed. Using estimation methods.")
    
    def estimate_crack_width_from_confidence(self, confidence, prediction='Cracked'):
        """
        Estimate crack width based on AI confidence score
        This is a simplified estimation method
        
        Args:
            confidence (float): Confidence score (0-100)
            prediction (str): 'Cracked' or 'Non-cracked'
            
        Returns:
            dict: Width estimation
        """
        if prediction == 'Non-cracked':
            return {
                'width_mm': 0.0,
                'category': 'No Crack',
                'severity': 'SAFE',
                'description': 'No visible cracks detected'
            }
        
        # Estimate based on confidence
        if confidence < 70:
            width = 0.1
            category = 'Hairline'
            severity = 'LOW'
            description = 'Very fine crack, barely visible'
        elif confidence < 80:
            width = 0.3
            category = 'Fine'
            severity = 'LOW'
            description = 'Fine crack, visible upon close inspection'
        elif confidence < 88:
            width = 0.8
            category = 'Moderate'
            severity = 'MEDIUM'
            description = 'Moderate crack, clearly visible'
        elif confidence < 94:
            width = 1.5
            category = 'Wide'
            severity = 'MEDIUM'
            description = 'Wide crack, requires attention'
        elif confidence < 97:
            width = 3.0
            category = 'Very Wide'
            severity = 'HIGH'
            description = 'Very wide crack, structural concern'
        else:
            width = 5.5
            category = 'Severe'
            severity = 'CRITICAL'
            description = 'Severe crack, immediate action required'
        
        return {
            'width_mm': width,
            'category': category,
            'severity': severity,
            'description': description,
            'confidence': confidence,
            'method': 'AI Confidence Estimation'
        }
    
    def classify_crack_width(self, width_mm):
        """
        Classify crack based on width (ACI standards)
        
        Args:
            width_mm (float): Crack width in millimeters
            
        Returns:
            dict: Classification
        """
        if width_mm < 0.1:
            return {
                'class': 'Negligible',
                'severity': 'SAFE',
                'action': 'No action required',
                'aci_rating': 'Acceptable'
            }
        elif width_mm < 0.3:
            return {
                'class': 'Hairline',
                'severity': 'LOW',
                'action': 'Monitor during routine inspections',
                'aci_rating': 'Acceptable'
            }
        elif width_mm < 1.0:
            return {
                'class': 'Fine',
                'severity': 'LOW',
                'action': 'Seal to prevent water ingress',
                'aci_rating': 'Tolerable'
            }
        elif width_mm < 2.0:
            return {
                'class': 'Moderate',
                'severity': 'MEDIUM',
                'action': 'Repair with epoxy injection',
                'aci_rating': 'Requires Attention'
            }
        elif width_mm < 5.0:
            return {
                'class': 'Wide',
                'severity': 'HIGH',
                'action': 'Structural repair required',
                'aci_rating': 'Unacceptable'
            }
        else:
            return {
                'class': 'Severe',
                'severity': 'CRITICAL',
                'action': 'Immediate structural intervention',
                'aci_rating': 'Unsafe'
            }
    
    def estimate_crack_length(self, coordinates, pixel_to_mm_ratio=1.0):
        """
        Calculate crack length from coordinates
        
        Args:
            coordinates (list): List of (x, y) points
            pixel_to_mm_ratio (float): Conversion ratio
            
        Returns:
            dict: Length measurement
        """
        if len(coordinates) < 2:
            return {
                'length_mm': 0,
                'length_cm': 0,
                'length_m': 0,
                'points': 0
            }
        
        total_length_pixels = 0
        
        for i in range(1, len(coordinates)):
            x1, y1 = coordinates[i-1]
            x2, y2 = coordinates[i]
            
            # Euclidean distance
            distance = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            total_length_pixels += distance
        
        length_mm = total_length_pixels * pixel_to_mm_ratio
        
        return {
            'length_mm': round(length_mm, 2),
            'length_cm': round(length_mm / 10, 2),
            'length_m': round(length_mm / 1000, 3),
            'points': len(coordinates),
            'method': 'Coordinate-based calculation'
        }
    
    def calculate_crack_area(self, polygon_coordinates, pixel_to_mm_ratio=1.0):
        """
        Calculate area enclosed by crack polygon
        
        Args:
            polygon_coordinates (list): List of (x, y) points
            pixel_to_mm_ratio (float): Conversion ratio
            
        Returns:
            dict: Area measurement
        """
        if len(polygon_coordinates) < 3:
            return {
                'area_mm2': 0,
                'area_cm2': 0,
                'perimeter_mm': 0
            }
        
        # Shoelace formula for polygon area
        n = len(polygon_coordinates)
        area_pixels = 0
        
        for i in range(n):
            j = (i + 1) % n
            area_pixels += polygon_coordinates[i][0] * polygon_coordinates[j][1]
            area_pixels -= polygon_coordinates[j][0] * polygon_coordinates[i][1]
        
        area_pixels = abs(area_pixels) / 2
        
        # Calculate perimeter
        perimeter_pixels = 0
        for i in range(n):
            j = (i + 1) % n
            x1, y1 = polygon_coordinates[i]
            x2, y2 = polygon_coordinates[j]
            perimeter_pixels += np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        
        # Convert to mm
        area_mm2 = area_pixels * (pixel_to_mm_ratio ** 2)
        perimeter_mm = perimeter_pixels * pixel_to_mm_ratio
        
        return {
            'area_mm2': round(area_mm2, 2),
            'area_cm2': round(area_mm2 / 100, 2),
            'perimeter_mm': round(perimeter_mm, 2),
            'perimeter_cm': round(perimeter_mm / 10, 2),
            'method': 'Polygon area calculation'
        }
    
    def calculate_crack_density(self, total_crack_length_mm, inspection_area_mm2):
        """
        Calculate crack density (length per unit area)
        
        Args:
            total_crack_length_mm (float): Total crack length
            inspection_area_mm2 (float): Inspection area
            
        Returns:
            dict: Density metrics
        """
        if inspection_area_mm2 == 0:
            return {'density': 0, 'rating': 'N/A'}
        
        # Density in mm/mm²
        density = total_crack_length_mm / inspection_area_mm2
        
        # Convert to more useful units (m/m²)
        density_m_per_m2 = density * 1000
        
        # Rating based on density
        if density_m_per_m2 < 0.5:
            rating = 'Low'
            severity = 'LOW'
        elif density_m_per_m2 < 1.5:
            rating = 'Moderate'
            severity = 'MEDIUM'
        elif density_m_per_m2 < 3.0:
            rating = 'High'
            severity = 'HIGH'
        else:
            rating = 'Very High'
            severity = 'CRITICAL'
        
        return {
            'density_mm_per_mm2': round(density, 6),
            'density_m_per_m2': round(density_m_per_m2, 3),
            'rating': rating,
            'severity': severity,
            'description': f'{rating} crack density detected'
        }
    
    def generate_measurement_report(self, measurements):
        """
        Generate comprehensive measurement report
        
        Args:
            measurements (dict): All measurements
            
        Returns:
            dict: Formatted report
        """
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_cracks': measurements.get('crack_count', 0),
                'total_length': measurements.get('total_length_mm', 0),
                'average_width': measurements.get('average_width_mm', 0),
                'max_width': measurements.get('max_width_mm', 0),
                'total_area': measurements.get('total_area_mm2', 0),
                'crack_density': measurements.get('density', 0)
            },
            'severity_distribution': measurements.get('severity_distribution', {}),
            'recommendations': self._generate_recommendations(measurements),
            'compliance': self._check_compliance(measurements)
        }
        
        return report
    
    def _generate_recommendations(self, measurements):
        """Generate repair recommendations based on measurements"""
        recommendations = []
        
        max_width = measurements.get('max_width_mm', 0)
        total_length = measurements.get('total_length_mm', 0)
        crack_count = measurements.get('crack_count', 0)
        
        if max_width > 5.0:
            recommendations.append({
                'priority': 'CRITICAL',
                'action': 'Immediate structural assessment required',
                'reason': f'Crack width exceeds 5mm ({max_width}mm detected)'
            })
        elif max_width > 2.0:
            recommendations.append({
                'priority': 'HIGH',
                'action': 'Schedule structural repair within 30 days',
                'reason': f'Significant crack width detected ({max_width}mm)'
            })
        elif max_width > 1.0:
            recommendations.append({
                'priority': 'MEDIUM',
                'action': 'Epoxy injection recommended',
                'reason': f'Moderate crack width ({max_width}mm)'
            })
        
        if total_length > 1000:  # > 1 meter
            recommendations.append({
                'priority': 'MEDIUM',
                'action': 'Extensive crack sealing required',
                'reason': f'Total crack length: {total_length/10:.1f}cm'
            })
        
        if crack_count > 10:
            recommendations.append({
                'priority': 'MEDIUM',
                'action': 'Investigate root cause of multiple cracks',
                'reason': f'{crack_count} cracks detected in inspection area'
            })
        
        if not recommendations:
            recommendations.append({
                'priority': 'LOW',
                'action': 'Continue routine monitoring',
                'reason': 'Crack measurements within acceptable limits'
            })
        
        return recommendations
    
    def _check_compliance(self, measurements):
        """Check compliance with standards"""
        max_width = measurements.get('max_width_mm', 0)
        
        compliance = {
            'ACI_318': 'PASS' if max_width < 0.4 else 'FAIL',
            'ACI_224': 'PASS' if max_width < 0.3 else 'FAIL',
            'AASHTO': 'PASS' if max_width < 0.5 else 'FAIL',
            'Eurocode_2': 'PASS' if max_width < 0.3 else 'FAIL',
            'overall': 'COMPLIANT' if max_width < 0.4 else 'NON-COMPLIANT'
        }
        
        return compliance


# Example usage
if __name__ == '__main__':
    measurer = CrackMeasurement()
    
    print("Crack Measurement Module Initialized")
    print("="*50)
    
    # Test width estimation
    print("\n1. Width Estimation from Confidence:")
    for confidence in [75, 85, 92, 96, 99]:
        result = measurer.estimate_crack_width_from_confidence(confidence)
        print(f"   Confidence {confidence}%: {result['width_mm']}mm ({result['category']})")
    
    # Test length calculation
    print("\n2. Length Calculation:")
    coordinates = [(0, 0), (100, 50), (200, 100), (300, 120)]
    length = measurer.estimate_crack_length(coordinates, pixel_to_mm_ratio=0.5)
    print(f"   Total Length: {length['length_cm']}cm")
    
    # Test area calculation
    print("\n3. Area Calculation:")
    polygon = [(0, 0), (100, 0), (100, 100), (0, 100)]
    area = measurer.calculate_crack_area(polygon, pixel_to_mm_ratio=0.5)
    print(f"   Area: {area['area_cm2']}cm²")
    
    # Test density
    print("\n4. Crack Density:")
    density = measurer.calculate_crack_density(500, 100000)
    print(f"   Density: {density['density_m_per_m2']}m/m² ({density['rating']})")
