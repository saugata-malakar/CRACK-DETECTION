"""
Crack Severity Classification Module
Classifies cracks into severity levels based on confidence and patterns
"""

class SeverityClassifier:
    """
    Classify crack severity based on AI confidence and crack characteristics
    """
    
    # Severity thresholds
    SEVERITY_LEVELS = {
        'SAFE': {
            'color': '#10b981',  # Green
            'icon': 'check-circle',
            'priority': 0,
            'action': 'No action required',
            'description': 'Structure is safe, no cracks detected'
        },
        'LOW': {
            'color': '#3b82f6',  # Blue
            'icon': 'info-circle',
            'priority': 1,
            'action': 'Monitor during routine inspections',
            'description': 'Minor surface cracks, cosmetic only'
        },
        'MEDIUM': {
            'color': '#f59e0b',  # Yellow/Orange
            'icon': 'exclamation-triangle',
            'priority': 2,
            'action': 'Schedule inspection within 30 days',
            'description': 'Moderate cracks, requires monitoring'
        },
        'HIGH': {
            'color': '#ef4444',  # Red
            'icon': 'exclamation-circle',
            'priority': 3,
            'action': 'Inspect within 7 days, plan repairs',
            'description': 'Significant cracks, structural concern'
        },
        'CRITICAL': {
            'color': '#7f1d1d',  # Dark Red
            'icon': 'times-circle',
            'priority': 4,
            'action': 'IMMEDIATE ACTION REQUIRED',
            'description': 'Severe cracks, potential safety hazard'
        }
    }
    
    @staticmethod
    def classify(prediction, confidence, crack_width=None, crack_length=None):
        """
        Classify crack severity based on multiple factors
        
        Args:
            prediction (str): 'Cracked' or 'Non-cracked'
            confidence (float): Confidence score (0-100)
            crack_width (float, optional): Crack width in mm
            crack_length (float, optional): Crack length in cm
            
        Returns:
            dict: Severity information
        """
        
        # If not cracked, it's safe
        if prediction == 'Non-cracked':
            severity = 'SAFE'
        else:
            # Classify based on confidence and measurements
            if confidence >= 95:
                # Very confident it's cracked
                if crack_width and crack_width > 5.0:
                    severity = 'CRITICAL'  # Wide cracks (>5mm)
                elif crack_width and crack_width > 2.0:
                    severity = 'HIGH'  # Moderate width (2-5mm)
                elif confidence >= 98:
                    severity = 'HIGH'  # Very high confidence
                else:
                    severity = 'MEDIUM'
            elif confidence >= 85:
                severity = 'MEDIUM'  # Moderate confidence
            elif confidence >= 70:
                severity = 'LOW'  # Lower confidence
            else:
                severity = 'LOW'  # Uncertain
        
        # Get severity details
        severity_info = SeverityClassifier.SEVERITY_LEVELS[severity].copy()
        severity_info['level'] = severity
        severity_info['confidence'] = confidence
        
        # Add measurements if available
        if crack_width:
            severity_info['crack_width'] = crack_width
        if crack_length:
            severity_info['crack_length'] = crack_length
            
        return severity_info
    
    @staticmethod
    def estimate_crack_width(confidence):
        """
        Estimate crack width based on confidence score
        This is a simplified estimation - real measurement requires image processing
        
        Args:
            confidence (float): Confidence score (0-100)
            
        Returns:
            float: Estimated crack width in mm
        """
        if confidence < 70:
            return 0.1  # Hairline crack
        elif confidence < 85:
            return 0.5  # Fine crack
        elif confidence < 95:
            return 1.5  # Moderate crack
        elif confidence < 98:
            return 3.0  # Wide crack
        else:
            return 6.0  # Very wide crack
    
    @staticmethod
    def get_repair_recommendation(severity_level):
        """
        Get repair recommendations based on severity
        
        Args:
            severity_level (str): Severity level
            
        Returns:
            dict: Repair recommendations
        """
        recommendations = {
            'SAFE': {
                'repair_type': 'None',
                'urgency': 'None',
                'estimated_cost': '$0',
                'methods': ['No repair needed'],
                'timeline': 'N/A'
            },
            'LOW': {
                'repair_type': 'Cosmetic',
                'urgency': 'Low',
                'estimated_cost': '$100-500',
                'methods': [
                    'Surface sealing',
                    'Epoxy injection for hairline cracks',
                    'Cosmetic patching'
                ],
                'timeline': '3-6 months'
            },
            'MEDIUM': {
                'repair_type': 'Preventive',
                'urgency': 'Medium',
                'estimated_cost': '$500-2,000',
                'methods': [
                    'Epoxy or polyurethane injection',
                    'Crack routing and sealing',
                    'Carbon fiber reinforcement',
                    'Structural monitoring'
                ],
                'timeline': '1-3 months'
            },
            'HIGH': {
                'repair_type': 'Structural',
                'urgency': 'High',
                'estimated_cost': '$2,000-10,000',
                'methods': [
                    'Structural epoxy injection',
                    'Steel plate bonding',
                    'FRP (Fiber Reinforced Polymer) wrapping',
                    'Concrete replacement',
                    'Load testing required'
                ],
                'timeline': '1-4 weeks'
            },
            'CRITICAL': {
                'repair_type': 'Emergency',
                'urgency': 'Critical',
                'estimated_cost': '$10,000+',
                'methods': [
                    'Immediate structural shoring',
                    'Emergency load restrictions',
                    'Complete structural assessment',
                    'Major concrete replacement',
                    'Structural redesign may be required',
                    'Consult structural engineer immediately'
                ],
                'timeline': 'Immediate (1-7 days)'
            }
        }
        
        return recommendations.get(severity_level, recommendations['LOW'])
    
    @staticmethod
    def get_compliance_status(severity_level):
        """
        Check compliance with common standards
        
        Args:
            severity_level (str): Severity level
            
        Returns:
            dict: Compliance information
        """
        compliance = {
            'SAFE': {
                'aashto': 'PASS',
                'aci': 'PASS',
                'eurocode': 'PASS',
                'is_code': 'PASS',
                'overall': 'COMPLIANT'
            },
            'LOW': {
                'aashto': 'PASS',
                'aci': 'PASS',
                'eurocode': 'PASS',
                'is_code': 'PASS',
                'overall': 'COMPLIANT - Monitor'
            },
            'MEDIUM': {
                'aashto': 'CAUTION',
                'aci': 'CAUTION',
                'eurocode': 'CAUTION',
                'is_code': 'CAUTION',
                'overall': 'REQUIRES ATTENTION'
            },
            'HIGH': {
                'aashto': 'FAIL',
                'aci': 'FAIL',
                'eurocode': 'FAIL',
                'is_code': 'FAIL',
                'overall': 'NON-COMPLIANT'
            },
            'CRITICAL': {
                'aashto': 'FAIL',
                'aci': 'FAIL',
                'eurocode': 'FAIL',
                'is_code': 'FAIL',
                'overall': 'UNSAFE - IMMEDIATE ACTION'
            }
        }
        
        return compliance.get(severity_level, compliance['LOW'])


# Example usage
if __name__ == '__main__':
    classifier = SeverityClassifier()
    
    # Test cases
    test_cases = [
        ('Non-cracked', 95.5),
        ('Cracked', 72.3),
        ('Cracked', 88.5),
        ('Cracked', 96.8),
        ('Cracked', 99.2),
    ]
    
    print("Crack Severity Classification Tests\n" + "="*50)
    
    for prediction, confidence in test_cases:
        severity = classifier.classify(prediction, confidence)
        print(f"\nPrediction: {prediction}, Confidence: {confidence}%")
        print(f"Severity: {severity['level']} - {severity['description']}")
        print(f"Action: {severity['action']}")
        
        # Get repair recommendations
        repair = classifier.get_repair_recommendation(severity['level'])
        print(f"Repair Type: {repair['repair_type']}")
        print(f"Estimated Cost: {repair['estimated_cost']}")
        print(f"Timeline: {repair['timeline']}")
