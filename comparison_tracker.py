"""
Before/After Comparison Module
Track crack progression over time and compare inspections
"""

import sqlite3
from datetime import datetime, timedelta
import json

class ComparisonTracker:
    """
    Track and compare crack inspections over time
    """
    
    def __init__(self, db_path='crack_detection.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize comparison tracking tables"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Comparison records table
        c.execute('''CREATE TABLE IF NOT EXISTS comparisons
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      site_id INTEGER,
                      structure_id INTEGER,
                      before_inspection_id INTEGER,
                      after_inspection_id INTEGER,
                      time_difference_days INTEGER,
                      severity_change TEXT,
                      crack_growth_rate REAL,
                      deterioration_score REAL,
                      notes TEXT,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      FOREIGN KEY (site_id) REFERENCES sites (id),
                      FOREIGN KEY (structure_id) REFERENCES structures (id),
                      FOREIGN KEY (before_inspection_id) REFERENCES inspections (id),
                      FOREIGN KEY (after_inspection_id) REFERENCES inspections (id))''')
        
        # Timeline tracking table
        c.execute('''CREATE TABLE IF NOT EXISTS inspection_timeline
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      site_id INTEGER,
                      structure_id INTEGER,
                      inspection_id INTEGER,
                      inspection_date TIMESTAMP,
                      severity_level TEXT,
                      confidence REAL,
                      crack_width REAL,
                      health_score REAL,
                      FOREIGN KEY (site_id) REFERENCES sites (id),
                      FOREIGN KEY (structure_id) REFERENCES structures (id),
                      FOREIGN KEY (inspection_id) REFERENCES inspections (id))''')
        
        conn.commit()
        conn.close()
    
    def add_to_timeline(self, site_id, inspection_id, inspection_data):
        """
        Add inspection to timeline for tracking
        
        Args:
            site_id (int): Site ID
            inspection_id (int): Inspection ID
            inspection_data (dict): Inspection details
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''INSERT INTO inspection_timeline 
                     (site_id, structure_id, inspection_id, inspection_date, 
                      severity_level, confidence, crack_width, health_score)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                  (site_id, 
                   inspection_data.get('structure_id'),
                   inspection_id,
                   inspection_data.get('date', datetime.now()),
                   inspection_data.get('severity_level'),
                   inspection_data.get('confidence'),
                   inspection_data.get('crack_width'),
                   inspection_data.get('health_score', 100.0)))
        
        conn.commit()
        conn.close()
    
    def get_site_timeline(self, site_id, days=365):
        """
        Get inspection timeline for a site
        
        Args:
            site_id (int): Site ID
            days (int): Number of days to look back
            
        Returns:
            list: Timeline data
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        c.execute('''SELECT * FROM inspection_timeline 
                     WHERE site_id = ? AND inspection_date >= ?
                     ORDER BY inspection_date ASC''',
                  (site_id, cutoff_date))
        
        timeline = c.fetchall()
        conn.close()
        
        return timeline
    
    def compare_inspections(self, before_id, after_id):
        """
        Compare two inspections
        
        Args:
            before_id (int): Earlier inspection ID
            after_id (int): Later inspection ID
            
        Returns:
            dict: Comparison results
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Get before inspection
        c.execute('''SELECT i.*, p.prediction, p.confidence, p.image_name
                     FROM inspections i
                     LEFT JOIN predictions p ON i.prediction_id = p.id
                     WHERE i.id = ?''', (before_id,))
        before = c.fetchone()
        
        # Get after inspection
        c.execute('''SELECT i.*, p.prediction, p.confidence, p.image_name
                     FROM inspections i
                     LEFT JOIN predictions p ON i.prediction_id = p.id
                     WHERE i.id = ?''', (after_id,))
        after = c.fetchone()
        
        conn.close()
        
        if not before or not after:
            return None
        
        # Calculate differences
        comparison = {
            'before': {
                'id': before[0],
                'date': before[6],
                'severity': before[7],
                'confidence': before[17] if len(before) > 17 else None,
                'crack_width': before[8],
                'prediction': before[16] if len(before) > 16 else None
            },
            'after': {
                'id': after[0],
                'date': after[6],
                'severity': after[7],
                'confidence': after[17] if len(after) > 17 else None,
                'crack_width': after[8],
                'prediction': after[16] if len(after) > 16 else None
            }
        }
        
        # Calculate time difference
        if before[6] and after[6]:
            before_date = datetime.strptime(before[6], '%Y-%m-%d %H:%M:%S')
            after_date = datetime.strptime(after[6], '%Y-%m-%d %H:%M:%S')
            time_diff = (after_date - before_date).days
            comparison['time_difference_days'] = time_diff
        
        # Calculate severity change
        severity_levels = {'SAFE': 0, 'LOW': 1, 'MEDIUM': 2, 'HIGH': 3, 'CRITICAL': 4}
        before_severity = severity_levels.get(before[7], 0)
        after_severity = severity_levels.get(after[7], 0)
        severity_change = after_severity - before_severity
        
        comparison['severity_change'] = {
            'numeric': severity_change,
            'description': self._get_severity_change_description(severity_change)
        }
        
        # Calculate crack growth
        if before[8] and after[8]:
            crack_growth = after[8] - before[8]
            comparison['crack_growth'] = {
                'absolute': crack_growth,
                'percentage': (crack_growth / before[8] * 100) if before[8] > 0 else 0,
                'rate_per_day': crack_growth / time_diff if time_diff > 0 else 0
            }
        
        # Calculate deterioration score (0-100, higher is worse)
        deterioration_score = self._calculate_deterioration_score(
            severity_change, 
            comparison.get('crack_growth', {}).get('percentage', 0),
            time_diff
        )
        comparison['deterioration_score'] = deterioration_score
        
        # Risk assessment
        comparison['risk_assessment'] = self._assess_risk(deterioration_score, after_severity)
        
        return comparison
    
    def _get_severity_change_description(self, change):
        """Get human-readable severity change description"""
        if change > 0:
            return f"Worsened by {change} level(s)"
        elif change < 0:
            return f"Improved by {abs(change)} level(s)"
        else:
            return "No change"
    
    def _calculate_deterioration_score(self, severity_change, crack_growth_pct, days):
        """
        Calculate deterioration score (0-100)
        Higher score = worse deterioration
        """
        score = 0
        
        # Severity change contribution (0-40 points)
        score += severity_change * 10
        
        # Crack growth contribution (0-40 points)
        if crack_growth_pct > 50:
            score += 40
        elif crack_growth_pct > 25:
            score += 30
        elif crack_growth_pct > 10:
            score += 20
        elif crack_growth_pct > 0:
            score += 10
        
        # Time factor (0-20 points)
        # Faster deterioration = higher score
        if days > 0:
            if days < 30:
                score += 20  # Very fast deterioration
            elif days < 90:
                score += 15  # Fast deterioration
            elif days < 180:
                score += 10  # Moderate deterioration
            else:
                score += 5   # Slow deterioration
        
        return min(score, 100)
    
    def _assess_risk(self, deterioration_score, current_severity):
        """
        Assess risk based on deterioration and current state
        
        Returns:
            dict: Risk assessment
        """
        risk_level = 'LOW'
        action = 'Continue routine monitoring'
        color = '#10b981'
        
        if deterioration_score >= 70 or current_severity >= 3:
            risk_level = 'CRITICAL'
            action = 'IMMEDIATE INTERVENTION REQUIRED'
            color = '#7f1d1d'
        elif deterioration_score >= 50 or current_severity >= 2:
            risk_level = 'HIGH'
            action = 'Accelerate inspection schedule, plan repairs'
            color = '#ef4444'
        elif deterioration_score >= 30:
            risk_level = 'MEDIUM'
            action = 'Increase monitoring frequency'
            color = '#f59e0b'
        
        return {
            'level': risk_level,
            'action': action,
            'color': color,
            'score': deterioration_score
        }
    
    def save_comparison(self, site_id, structure_id, before_id, after_id, comparison_data):
        """
        Save comparison record
        
        Args:
            site_id (int): Site ID
            structure_id (int): Structure ID
            before_id (int): Before inspection ID
            after_id (int): After inspection ID
            comparison_data (dict): Comparison results
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''INSERT INTO comparisons 
                     (site_id, structure_id, before_inspection_id, after_inspection_id,
                      time_difference_days, severity_change, crack_growth_rate, 
                      deterioration_score, notes)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (site_id, structure_id, before_id, after_id,
                   comparison_data.get('time_difference_days'),
                   json.dumps(comparison_data.get('severity_change')),
                   comparison_data.get('crack_growth', {}).get('rate_per_day'),
                   comparison_data.get('deterioration_score'),
                   comparison_data.get('notes', '')))
        
        comparison_id = c.lastrowid
        conn.commit()
        conn.close()
        
        return comparison_id
    
    def get_site_comparisons(self, site_id):
        """Get all comparisons for a site"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''SELECT * FROM comparisons 
                     WHERE site_id = ?
                     ORDER BY created_at DESC''', (site_id,))
        
        comparisons = c.fetchall()
        conn.close()
        
        return comparisons
    
    def predict_future_state(self, site_id, days_ahead=90):
        """
        Predict future crack state based on historical data
        
        Args:
            site_id (int): Site ID
            days_ahead (int): Days to predict ahead
            
        Returns:
            dict: Prediction results
        """
        timeline = self.get_site_timeline(site_id, days=365)
        
        if len(timeline) < 2:
            return {
                'prediction': 'Insufficient data',
                'confidence': 0,
                'message': 'Need at least 2 inspections for prediction'
            }
        
        # Calculate average deterioration rate
        total_deterioration = 0
        total_days = 0
        
        for i in range(1, len(timeline)):
            prev = timeline[i-1]
            curr = timeline[i]
            
            # Calculate severity change
            severity_levels = {'SAFE': 0, 'LOW': 1, 'MEDIUM': 2, 'HIGH': 3, 'CRITICAL': 4}
            prev_severity = severity_levels.get(prev[4], 0)
            curr_severity = severity_levels.get(curr[4], 0)
            
            if prev[3] and curr[3]:
                prev_date = datetime.strptime(str(prev[3]), '%Y-%m-%d %H:%M:%S')
                curr_date = datetime.strptime(str(curr[3]), '%Y-%m-%d %H:%M:%S')
                days_diff = (curr_date - prev_date).days
                
                if days_diff > 0:
                    deterioration = curr_severity - prev_severity
                    total_deterioration += deterioration
                    total_days += days_diff
        
        if total_days == 0:
            return {
                'prediction': 'Unable to calculate',
                'confidence': 0,
                'message': 'Insufficient time data'
            }
        
        # Calculate average deterioration per day
        avg_deterioration_per_day = total_deterioration / total_days
        
        # Predict future severity
        current_severity = severity_levels.get(timeline[-1][4], 0)
        predicted_change = avg_deterioration_per_day * days_ahead
        predicted_severity = current_severity + predicted_change
        
        # Convert back to severity level
        severity_names = ['SAFE', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
        predicted_level = severity_names[min(int(predicted_severity), 4)]
        
        return {
            'current_severity': timeline[-1][4],
            'predicted_severity': predicted_level,
            'days_ahead': days_ahead,
            'deterioration_rate': avg_deterioration_per_day,
            'confidence': min(len(timeline) * 10, 90),  # More data = higher confidence
            'recommendation': self._get_prediction_recommendation(predicted_level)
        }
    
    def _get_prediction_recommendation(self, predicted_level):
        """Get recommendation based on prediction"""
        recommendations = {
            'SAFE': 'Continue routine inspections',
            'LOW': 'Monitor closely, no immediate action needed',
            'MEDIUM': 'Schedule preventive maintenance',
            'HIGH': 'Plan repairs within next inspection cycle',
            'CRITICAL': 'Immediate action recommended to prevent reaching critical state'
        }
        return recommendations.get(predicted_level, 'Continue monitoring')


# Example usage
if __name__ == '__main__':
    tracker = ComparisonTracker()
    
    print("Comparison Tracker Initialized")
    print("="*50)
    print("\nFeatures:")
    print("  • Before/After comparison")
    print("  • Timeline tracking")
    print("  • Deterioration scoring")
    print("  • Risk assessment")
    print("  • Future state prediction")
    print("  • Crack growth rate calculation")
