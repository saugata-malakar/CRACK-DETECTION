"""
Predictive Maintenance Module
AI-powered prediction of future structural issues
"""

import sqlite3
import numpy as np
from datetime import datetime, timedelta
import json
import math

class PredictiveMaintenance:
    """
    Predict future maintenance needs using AI and historical data
    """
    
    def __init__(self, db_path='crack_detection.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize predictive maintenance tables"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Predictions table
        c.execute('''CREATE TABLE IF NOT EXISTS maintenance_predictions
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      site_id INTEGER,
                      structure_id INTEGER,
                      prediction_type TEXT,
                      current_condition TEXT,
                      predicted_condition TEXT,
                      confidence REAL,
                      time_horizon_days INTEGER,
                      deterioration_rate REAL,
                      risk_factors TEXT,
                      recommended_actions TEXT,
                      estimated_cost REAL,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      FOREIGN KEY (site_id) REFERENCES sites (id),
                      FOREIGN KEY (structure_id) REFERENCES structures (id))''')
        
        # Maintenance schedules table
        c.execute('''CREATE TABLE IF NOT EXISTS maintenance_schedules
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      site_id INTEGER,
                      structure_id INTEGER,
                      maintenance_type TEXT,
                      priority TEXT,
                      scheduled_date DATE,
                      estimated_cost REAL,
                      description TEXT,
                      status TEXT DEFAULT 'scheduled',
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      FOREIGN KEY (site_id) REFERENCES sites (id),
                      FOREIGN KEY (structure_id) REFERENCES structures (id))''')
        
        conn.commit()
        conn.close()
    
    def analyze_deterioration_trend(self, site_id, structure_id=None):
        """
        Analyze deterioration trend for a site or structure
        
        Args:
            site_id (int): Site ID
            structure_id (int, optional): Structure ID
            
        Returns:
            dict: Trend analysis
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        if structure_id:
            c.execute('''SELECT inspection_date, severity_level, confidence, crack_width
                         FROM inspections
                         WHERE site_id = ? AND structure_id = ?
                         ORDER BY inspection_date ASC''', (site_id, structure_id))
        else:
            c.execute('''SELECT inspection_date, severity_level, confidence, crack_width
                         FROM inspections
                         WHERE site_id = ?
                         ORDER BY inspection_date ASC''', (site_id,))
        
        inspections = c.fetchall()
        conn.close()
        
        if len(inspections) < 2:
            return {
                'trend': 'insufficient_data',
                'message': 'Need at least 2 inspections for trend analysis'
            }
        
        # Convert severity to numeric
        severity_map = {'SAFE': 0, 'LOW': 1, 'MEDIUM': 2, 'HIGH': 3, 'CRITICAL': 4}
        
        data_points = []
        for inspection in inspections:
            date_str = inspection[0]
            severity = severity_map.get(inspection[1], 0)
            confidence = inspection[2] or 0
            crack_width = inspection[3] or 0
            
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                days_since_start = (date_obj - datetime.strptime(inspections[0][0], '%Y-%m-%d %H:%M:%S')).days
                
                data_points.append({
                    'days': days_since_start,
                    'severity': severity,
                    'confidence': confidence,
                    'crack_width': crack_width
                })
            except:
                continue
        
        if len(data_points) < 2:
            return {'trend': 'insufficient_data'}
        
        # Calculate trends
        severity_trend = self._calculate_linear_trend([p['days'] for p in data_points], 
                                                    [p['severity'] for p in data_points])
        
        crack_trend = self._calculate_linear_trend([p['days'] for p in data_points], 
                                                 [p['crack_width'] for p in data_points])
        
        # Determine overall trend
        overall_trend = 'stable'
        if severity_trend['slope'] > 0.01:
            overall_trend = 'deteriorating'
        elif severity_trend['slope'] < -0.01:
            overall_trend = 'improving'
        
        return {
            'trend': overall_trend,
            'severity_trend': severity_trend,
            'crack_trend': crack_trend,
            'data_points': len(data_points),
            'time_span_days': data_points[-1]['days'],
            'current_severity': data_points[-1]['severity'],
            'prediction_confidence': min(len(data_points) * 15, 95)
        }
    
    def _calculate_linear_trend(self, x_values, y_values):
        """Calculate linear trend using least squares"""
        if len(x_values) < 2:
            return {'slope': 0, 'intercept': 0, 'r_squared': 0}
        
        x = np.array(x_values)
        y = np.array(y_values)
        
        # Remove any NaN values
        mask = ~(np.isnan(x) | np.isnan(y))
        x = x[mask]
        y = y[mask]
        
        if len(x) < 2:
            return {'slope': 0, 'intercept': 0, 'r_squared': 0}
        
        # Calculate slope and intercept
        n = len(x)
        slope = (n * np.sum(x * y) - np.sum(x) * np.sum(y)) / (n * np.sum(x**2) - np.sum(x)**2)
        intercept = (np.sum(y) - slope * np.sum(x)) / n
        
        # Calculate R-squared
        y_pred = slope * x + intercept
        ss_res = np.sum((y - y_pred)**2)
        ss_tot = np.sum((y - np.mean(y))**2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        
        return {
            'slope': float(slope),
            'intercept': float(intercept),
            'r_squared': float(r_squared)
        }
    
    def predict_future_condition(self, site_id, structure_id, days_ahead=365):
        """
        Predict future condition of structure
        
        Args:
            site_id (int): Site ID
            structure_id (int): Structure ID
            days_ahead (int): Days to predict ahead
            
        Returns:
            dict: Prediction results
        """
        trend_analysis = self.analyze_deterioration_trend(site_id, structure_id)
        
        if trend_analysis['trend'] == 'insufficient_data':
            return trend_analysis
        
        # Current state
        current_severity = trend_analysis['current_severity']
        severity_slope = trend_analysis['severity_trend']['slope']
        
        # Predict future severity
        predicted_severity_numeric = current_severity + (severity_slope * days_ahead)
        predicted_severity_numeric = max(0, min(4, predicted_severity_numeric))  # Clamp to 0-4
        
        severity_names = ['SAFE', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
        predicted_severity = severity_names[int(round(predicted_severity_numeric))]
        
        # Calculate confidence
        confidence = trend_analysis['prediction_confidence']
        if days_ahead > 365:
            confidence *= 0.8  # Reduce confidence for longer predictions
        if trend_analysis['severity_trend']['r_squared'] < 0.5:
            confidence *= 0.7  # Reduce confidence for poor fit
        
        # Risk factors
        risk_factors = self._identify_risk_factors(trend_analysis, days_ahead)
        
        # Recommended actions
        actions = self._generate_maintenance_actions(predicted_severity, days_ahead, risk_factors)
        
        # Cost estimation
        estimated_cost = self._estimate_maintenance_cost(predicted_severity, actions)
        
        prediction = {
            'site_id': site_id,
            'structure_id': structure_id,
            'current_condition': severity_names[current_severity],
            'predicted_condition': predicted_severity,
            'days_ahead': days_ahead,
            'confidence': round(confidence, 1),
            'deterioration_rate': round(severity_slope * 365, 3),  # Per year
            'risk_factors': risk_factors,
            'recommended_actions': actions,
            'estimated_cost': estimated_cost,
            'prediction_date': (datetime.now() + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
        }
        
        # Save prediction
        self._save_prediction(prediction)
        
        return prediction
    
    def _identify_risk_factors(self, trend_analysis, days_ahead):
        """Identify risk factors affecting deterioration"""
        risk_factors = []
        
        if trend_analysis['severity_trend']['slope'] > 0.005:
            risk_factors.append({
                'factor': 'Accelerating Deterioration',
                'severity': 'HIGH',
                'description': 'Structure showing rapid deterioration trend'
            })
        
        if trend_analysis['crack_trend']['slope'] > 0.01:
            risk_factors.append({
                'factor': 'Crack Growth',
                'severity': 'MEDIUM',
                'description': 'Cracks are growing over time'
            })
        
        if days_ahead > 730:  # 2 years
            risk_factors.append({
                'factor': 'Long Prediction Horizon',
                'severity': 'LOW',
                'description': 'Uncertainty increases with longer predictions'
            })
        
        if trend_analysis['data_points'] < 5:
            risk_factors.append({
                'factor': 'Limited Historical Data',
                'severity': 'MEDIUM',
                'description': 'Predictions based on limited inspection history'
            })
        
        return risk_factors
    
    def _generate_maintenance_actions(self, predicted_severity, days_ahead, risk_factors):
        """Generate recommended maintenance actions"""
        actions = []
        
        if predicted_severity == 'CRITICAL':
            actions.extend([
                {
                    'action': 'Emergency Structural Assessment',
                    'priority': 'CRITICAL',
                    'timeline': 'Immediate',
                    'cost_range': '$5,000-15,000'
                },
                {
                    'action': 'Load Restriction Implementation',
                    'priority': 'CRITICAL',
                    'timeline': 'Immediate',
                    'cost_range': '$1,000-3,000'
                }
            ])
        elif predicted_severity == 'HIGH':
            actions.extend([
                {
                    'action': 'Structural Repair Planning',
                    'priority': 'HIGH',
                    'timeline': f'{max(30, days_ahead-90)} days',
                    'cost_range': '$2,000-8,000'
                },
                {
                    'action': 'Increase Inspection Frequency',
                    'priority': 'HIGH',
                    'timeline': '30 days',
                    'cost_range': '$500-1,500'
                }
            ])
        elif predicted_severity == 'MEDIUM':
            actions.extend([
                {
                    'action': 'Preventive Maintenance',
                    'priority': 'MEDIUM',
                    'timeline': f'{days_ahead-180} days',
                    'cost_range': '$500-2,000'
                },
                {
                    'action': 'Crack Sealing',
                    'priority': 'MEDIUM',
                    'timeline': f'{days_ahead-120} days',
                    'cost_range': '$200-800'
                }
            ])
        else:
            actions.append({
                'action': 'Continue Routine Monitoring',
                'priority': 'LOW',
                'timeline': 'Next scheduled inspection',
                'cost_range': '$100-300'
            })
        
        # Add risk-based actions
        for risk in risk_factors:
            if risk['severity'] == 'HIGH':
                actions.append({
                    'action': f'Address {risk["factor"]}',
                    'priority': 'HIGH',
                    'timeline': '60 days',
                    'cost_range': '$1,000-5,000'
                })
        
        return actions
    
    def _estimate_maintenance_cost(self, predicted_severity, actions):
        """Estimate total maintenance cost"""
        base_costs = {
            'SAFE': 200,
            'LOW': 500,
            'MEDIUM': 1500,
            'HIGH': 5000,
            'CRITICAL': 12000
        }
        
        base_cost = base_costs.get(predicted_severity, 1000)
        
        # Add action costs (rough estimates)
        action_cost = sum([
            2000 if action['priority'] == 'CRITICAL' else
            1000 if action['priority'] == 'HIGH' else
            500 if action['priority'] == 'MEDIUM' else 200
            for action in actions
        ])
        
        total_cost = base_cost + action_cost
        
        return {
            'base_cost': base_cost,
            'action_cost': action_cost,
            'total_estimated': total_cost,
            'range_min': int(total_cost * 0.7),
            'range_max': int(total_cost * 1.5)
        }
    
    def _save_prediction(self, prediction):
        """Save prediction to database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''INSERT INTO maintenance_predictions
                     (site_id, structure_id, prediction_type, current_condition,
                      predicted_condition, confidence, time_horizon_days,
                      deterioration_rate, risk_factors, recommended_actions, estimated_cost)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (prediction['site_id'], prediction['structure_id'], 'deterioration',
                   prediction['current_condition'], prediction['predicted_condition'],
                   prediction['confidence'], prediction['days_ahead'],
                   prediction['deterioration_rate'],
                   json.dumps(prediction['risk_factors']),
                   json.dumps(prediction['recommended_actions']),
                   prediction['estimated_cost']['total_estimated']))
        
        conn.commit()
        conn.close()
    
    def generate_maintenance_schedule(self, site_id, prediction_horizon_days=730):
        """
        Generate maintenance schedule for a site
        
        Args:
            site_id (int): Site ID
            prediction_horizon_days (int): Prediction horizon
            
        Returns:
            list: Maintenance schedule
        """
        # Get all structures for the site
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT id, name, structure_type FROM structures WHERE site_id = ?', (site_id,))
        structures = c.fetchall()
        conn.close()
        
        schedule = []
        
        for structure in structures:
            structure_id, name, structure_type = structure
            
            # Get prediction
            prediction = self.predict_future_condition(site_id, structure_id, prediction_horizon_days)
            
            if prediction.get('recommended_actions'):
                for action in prediction['recommended_actions']:
                    # Calculate scheduled date
                    timeline = action.get('timeline', '365 days')
                    days = self._parse_timeline(timeline)
                    scheduled_date = datetime.now() + timedelta(days=days)
                    
                    schedule_item = {
                        'structure_id': structure_id,
                        'structure_name': name,
                        'structure_type': structure_type,
                        'action': action['action'],
                        'priority': action['priority'],
                        'scheduled_date': scheduled_date.strftime('%Y-%m-%d'),
                        'estimated_cost': self._parse_cost_range(action.get('cost_range', '$500')),
                        'predicted_condition': prediction['predicted_condition']
                    }
                    
                    schedule.append(schedule_item)
        
        # Sort by priority and date
        priority_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        schedule.sort(key=lambda x: (priority_order.get(x['priority'], 4), x['scheduled_date']))
        
        return schedule
    
    def _parse_timeline(self, timeline_str):
        """Parse timeline string to days"""
        if 'immediate' in timeline_str.lower():
            return 7
        elif 'days' in timeline_str:
            try:
                return int(''.join(filter(str.isdigit, timeline_str)))
            except:
                return 30
        else:
            return 30
    
    def _parse_cost_range(self, cost_str):
        """Parse cost range string"""
        try:
            # Extract numbers from string like "$1,000-5,000"
            numbers = [int(s.replace(',', '')) for s in cost_str.split('-')]
            if len(numbers) == 2:
                return sum(numbers) // 2  # Average
            elif len(numbers) == 1:
                return numbers[0]
        except:
            pass
        return 1000  # Default


# Example usage
if __name__ == '__main__':
    pm = PredictiveMaintenance()
    
    print("Predictive Maintenance Module Initialized")
    print("="*50)
    print("\nFeatures:")
    print("  • Deterioration trend analysis")
    print("  • Future condition prediction")
    print("  • Risk factor identification")
    print("  • Maintenance action recommendations")
    print("  • Cost estimation")
    print("  • Maintenance scheduling")
    print("  • Historical data analysis")