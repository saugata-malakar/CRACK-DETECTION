"""
Compliance and Standards Checker Module
Check compliance with international standards
"""

from datetime import datetime
import json

class ComplianceChecker:
    """
    Check crack inspection compliance with various standards
    """
    
    # Standard crack width limits (in mm)
    STANDARDS = {
        'ACI_318': {
            'name': 'ACI 318 - Building Code Requirements for Structural Concrete',
            'limits': {
                'interior_exposure': 0.41,
                'exterior_exposure': 0.33,
                'corrosive_exposure': 0.18
            },
            'description': 'American Concrete Institute standard for structural concrete'
        },
        'ACI_224': {
            'name': 'ACI 224R - Control of Cracking in Concrete Structures',
            'limits': {
                'dry_air': 0.41,
                'humidity_moist': 0.30,
                'deicing_chemicals': 0.18,
                'seawater': 0.15,
                'water_retaining': 0.10
            },
            'description': 'ACI guide for crack control'
        },
        'AASHTO': {
            'name': 'AASHTO LRFD Bridge Design Specifications',
            'limits': {
                'moderate_exposure': 0.30,
                'severe_exposure': 0.23
            },
            'description': 'American Association of State Highway and Transportation Officials'
        },
        'EUROCODE_2': {
            'name': 'Eurocode 2 - Design of Concrete Structures',
            'limits': {
                'reinforced_concrete': 0.30,
                'prestressed_concrete': 0.20
            },
            'description': 'European standard for concrete structures'
        },
        'BS_8110': {
            'name': 'BS 8110 - British Standard for Structural Concrete',
            'limits': {
                'general': 0.30,
                'aggressive_environment': 0.10
            },
            'description': 'British standard for structural concrete'
        },
        'IS_456': {
            'name': 'IS 456 - Indian Standard for Plain and Reinforced Concrete',
            'limits': {
                'moderate_exposure': 0.30,
                'severe_exposure': 0.20,
                'very_severe_exposure': 0.10
            },
            'description': 'Indian standard for concrete structures'
        },
        'AS_3600': {
            'name': 'AS 3600 - Australian Standard for Concrete Structures',
            'limits': {
                'general': 0.30,
                'aggressive_environment': 0.20
            },
            'description': 'Australian standard for concrete structures'
        }
    }
    
    def check_compliance(self, crack_width_mm, exposure_condition='general'):
        """
        Check compliance with all standards
        
        Args:
            crack_width_mm (float): Crack width in millimeters
            exposure_condition (str): Exposure condition
            
        Returns:
            dict: Compliance results for all standards
        """
        results = {
            'crack_width_mm': crack_width_mm,
            'exposure_condition': exposure_condition,
            'timestamp': datetime.now().isoformat(),
            'standards': {},
            'overall_compliance': True,
            'most_restrictive': None,
            'recommendations': []
        }
        
        most_restrictive_limit = float('inf')
        most_restrictive_standard = None
        
        for standard_code, standard_info in self.STANDARDS.items():
            # Find applicable limit
            limit = self._get_applicable_limit(standard_info['limits'], exposure_condition)
            
            if limit:
                compliant = crack_width_mm <= limit
                
                results['standards'][standard_code] = {
                    'name': standard_info['name'],
                    'limit_mm': limit,
                    'compliant': compliant,
                    'status': 'PASS' if compliant else 'FAIL',
                    'margin': round(limit - crack_width_mm, 3),
                    'description': standard_info['description']
                }
                
                if not compliant:
                    results['overall_compliance'] = False
                
                # Track most restrictive
                if limit < most_restrictive_limit:
                    most_restrictive_limit = limit
                    most_restrictive_standard = standard_code
        
        results['most_restrictive'] = {
            'standard': most_restrictive_standard,
            'limit_mm': most_restrictive_limit
        }
        
        # Generate recommendations
        results['recommendations'] = self._generate_recommendations(
            crack_width_mm, 
            results['overall_compliance'],
            most_restrictive_limit
        )
        
        return results
    
    def _get_applicable_limit(self, limits, exposure_condition):
        """Get applicable limit for exposure condition"""
        # Try exact match first
        if exposure_condition in limits:
            return limits[exposure_condition]
        
        # Try general/default
        if 'general' in limits:
            return limits['general']
        
        # Return first limit as fallback
        if limits:
            return list(limits.values())[0]
        
        return None
    
    def _generate_recommendations(self, crack_width, compliant, most_restrictive_limit):
        """Generate compliance recommendations"""
        recommendations = []
        
        if compliant:
            recommendations.append({
                'priority': 'LOW',
                'action': 'Continue routine monitoring',
                'reason': 'Crack width within acceptable limits for all applicable standards'
            })
        else:
            if crack_width > most_restrictive_limit * 2:
                recommendations.append({
                    'priority': 'CRITICAL',
                    'action': 'Immediate structural assessment required',
                    'reason': f'Crack width ({crack_width}mm) significantly exceeds most restrictive limit ({most_restrictive_limit}mm)'
                })
            elif crack_width > most_restrictive_limit * 1.5:
                recommendations.append({
                    'priority': 'HIGH',
                    'action': 'Schedule structural repair within 30 days',
                    'reason': f'Crack width exceeds standards by {((crack_width/most_restrictive_limit - 1) * 100):.1f}%'
                })
            else:
                recommendations.append({
                    'priority': 'MEDIUM',
                    'action': 'Plan repair and increase monitoring frequency',
                    'reason': 'Crack width exceeds one or more standard limits'
                })
            
            recommendations.append({
                'priority': 'MEDIUM',
                'action': 'Document non-compliance',
                'reason': 'Required for regulatory reporting and liability protection'
            })
        
        return recommendations
    
    def generate_compliance_report(self, inspection_data):
        """
        Generate comprehensive compliance report
        
        Args:
            inspection_data (dict): Inspection details
            
        Returns:
            dict: Compliance report
        """
        crack_width = inspection_data.get('crack_width_mm', 0)
        exposure = inspection_data.get('exposure_condition', 'general')
        
        compliance = self.check_compliance(crack_width, exposure)
        
        report = {
            'report_id': f"COMP-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            'inspection_id': inspection_data.get('inspection_id'),
            'generated_at': datetime.now().isoformat(),
            'inspector': inspection_data.get('inspector', 'N/A'),
            'location': inspection_data.get('location', 'N/A'),
            'structure_type': inspection_data.get('structure_type', 'General'),
            'compliance_check': compliance,
            'certification': self._generate_certification(compliance),
            'next_inspection_date': self._calculate_next_inspection(compliance)
        }
        
        return report
    
    def _generate_certification(self, compliance):
        """Generate certification statement"""
        if compliance['overall_compliance']:
            return {
                'status': 'CERTIFIED',
                'statement': 'This structure meets all applicable concrete crack width standards.',
                'valid_until': self._calculate_certification_expiry(compliance),
                'certifying_standards': list(compliance['standards'].keys())
            }
        else:
            failed_standards = [
                code for code, result in compliance['standards'].items()
                if not result['compliant']
            ]
            
            return {
                'status': 'NON-COMPLIANT',
                'statement': 'This structure does not meet all applicable standards.',
                'failed_standards': failed_standards,
                'action_required': 'Repair or remediation required before certification'
            }
    
    def _calculate_certification_expiry(self, compliance):
        """Calculate certification expiry date"""
        from datetime import timedelta
        
        # Base on severity
        crack_width = compliance['crack_width_mm']
        
        if crack_width < 0.1:
            months = 24  # 2 years
        elif crack_width < 0.2:
            months = 12  # 1 year
        else:
            months = 6   # 6 months
        
        expiry = datetime.now() + timedelta(days=months*30)
        return expiry.strftime('%Y-%m-%d')
    
    def _calculate_next_inspection(self, compliance):
        """Calculate recommended next inspection date"""
        from datetime import timedelta
        
        if not compliance['overall_compliance']:
            days = 30  # 1 month for non-compliant
        elif compliance['crack_width_mm'] > 0.2:
            days = 90  # 3 months
        elif compliance['crack_width_mm'] > 0.1:
            days = 180  # 6 months
        else:
            days = 365  # 1 year
        
        next_date = datetime.now() + timedelta(days=days)
        return next_date.strftime('%Y-%m-%d')
    
    def get_standard_details(self, standard_code):
        """Get detailed information about a standard"""
        if standard_code in self.STANDARDS:
            return self.STANDARDS[standard_code]
        return None
    
    def compare_standards(self, crack_width_mm):
        """
        Compare crack width against all standards
        
        Args:
            crack_width_mm (float): Crack width
            
        Returns:
            list: Sorted comparison
        """
        comparisons = []
        
        for code, info in self.STANDARDS.items():
            for condition, limit in info['limits'].items():
                comparisons.append({
                    'standard': code,
                    'name': info['name'],
                    'condition': condition,
                    'limit_mm': limit,
                    'compliant': crack_width_mm <= limit,
                    'margin_mm': round(limit - crack_width_mm, 3)
                })
        
        # Sort by limit (most restrictive first)
        comparisons.sort(key=lambda x: x['limit_mm'])
        
        return comparisons


# Example usage
if __name__ == '__main__':
    checker = ComplianceChecker()
    
    print("Compliance Checker Initialized")
    print("="*50)
    print("\nSupported Standards:")
    for code, info in checker.STANDARDS.items():
        print(f"  • {code}: {info['name']}")
    
    print("\n" + "="*50)
    print("Example Compliance Check:")
    
    # Test with 0.35mm crack
    result = checker.check_compliance(0.35, 'general')
    print(f"\nCrack Width: 0.35mm")
    print(f"Overall Compliance: {'PASS' if result['overall_compliance'] else 'FAIL'}")
    print(f"\nStandards:")
    for code, details in result['standards'].items():
        print(f"  {code}: {details['status']} (limit: {details['limit_mm']}mm)")
