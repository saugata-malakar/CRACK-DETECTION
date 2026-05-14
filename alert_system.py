"""
Alert and Notification System
Send email/SMS alerts for critical findings
"""

import sqlite3
from datetime import datetime
import json

class AlertSystem:
    """
    Manage alerts and notifications for critical crack detections
    """
    
    def __init__(self, db_path='crack_detection.db'):
        self.db_path = db_path
        self.init_database()
        
        # Try to import email libraries
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            self.smtplib = smtplib
            self.MIMEText = MIMEText
            self.MIMEMultipart = MIMEMultipart
            self.email_available = True
        except ImportError:
            self.email_available = False
            print("Warning: Email libraries not available")
    
    def init_database(self):
        """Initialize alert tables"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Alert rules table
        c.execute('''CREATE TABLE IF NOT EXISTS alert_rules
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      user_id INTEGER,
                      rule_name TEXT,
                      trigger_condition TEXT,
                      severity_threshold TEXT,
                      notification_method TEXT,
                      recipients TEXT,
                      is_active BOOLEAN DEFAULT 1,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      FOREIGN KEY (user_id) REFERENCES users (id))''')
        
        # Notification log table
        c.execute('''CREATE TABLE IF NOT EXISTS notification_log
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      alert_id INTEGER,
                      user_id INTEGER,
                      notification_type TEXT,
                      recipient TEXT,
                      subject TEXT,
                      message TEXT,
                      status TEXT,
                      sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      FOREIGN KEY (alert_id) REFERENCES alerts (id),
                      FOREIGN KEY (user_id) REFERENCES users (id))''')
        
        conn.commit()
        conn.close()
    
    def create_alert_rule(self, user_id, rule_data):
        """
        Create an alert rule
        
        Args:
            user_id (int): User ID
            rule_data (dict): Rule configuration
                - name: Rule name
                - trigger: 'severity', 'crack_width', 'deterioration_rate'
                - threshold: Threshold value
                - method: 'email', 'sms', 'both'
                - recipients: List of email/phone numbers
                
        Returns:
            int: Rule ID
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''INSERT INTO alert_rules 
                     (user_id, rule_name, trigger_condition, severity_threshold,
                      notification_method, recipients)
                     VALUES (?, ?, ?, ?, ?, ?)''',
                  (user_id,
                   rule_data.get('name', 'Alert Rule'),
                   rule_data.get('trigger', 'severity'),
                   rule_data.get('threshold', 'HIGH'),
                   rule_data.get('method', 'email'),
                   json.dumps(rule_data.get('recipients', []))))
        
        rule_id = c.lastrowid
        conn.commit()
        conn.close()
        
        return rule_id
    
    def get_user_alert_rules(self, user_id):
        """Get all alert rules for a user"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('SELECT * FROM alert_rules WHERE user_id = ? ORDER BY created_at DESC',
                  (user_id,))
        rules = c.fetchall()
        
        conn.close()
        
        # Parse JSON fields
        parsed_rules = []
        for rule in rules:
            parsed_rules.append({
                'id': rule[0],
                'user_id': rule[1],
                'name': rule[2],
                'trigger': rule[3],
                'threshold': rule[4],
                'method': rule[5],
                'recipients': json.loads(rule[6]) if rule[6] else [],
                'is_active': rule[7],
                'created_at': rule[8]
            })
        
        return parsed_rules
    
    def check_alert_triggers(self, inspection_data):
        """
        Check if inspection triggers any alert rules
        
        Args:
            inspection_data (dict): Inspection details
            
        Returns:
            list: Triggered rules
        """
        user_id = inspection_data.get('user_id')
        rules = self.get_user_alert_rules(user_id)
        
        triggered_rules = []
        
        for rule in rules:
            if not rule['is_active']:
                continue
            
            triggered = False
            
            # Check severity trigger
            if rule['trigger'] == 'severity':
                severity_levels = {'SAFE': 0, 'LOW': 1, 'MEDIUM': 2, 'HIGH': 3, 'CRITICAL': 4}
                current_severity = severity_levels.get(inspection_data.get('severity_level'), 0)
                threshold_severity = severity_levels.get(rule['threshold'], 2)
                
                if current_severity >= threshold_severity:
                    triggered = True
            
            # Check crack width trigger
            elif rule['trigger'] == 'crack_width':
                crack_width = inspection_data.get('crack_width', 0)
                threshold = float(rule['threshold'])
                
                if crack_width >= threshold:
                    triggered = True
            
            # Check deterioration rate trigger
            elif rule['trigger'] == 'deterioration_rate':
                deterioration_score = inspection_data.get('deterioration_score', 0)
                threshold = float(rule['threshold'])
                
                if deterioration_score >= threshold:
                    triggered = True
            
            if triggered:
                triggered_rules.append(rule)
        
        return triggered_rules
    
    def send_alert_notification(self, alert_id, rule, inspection_data):
        """
        Send notification based on alert rule
        
        Args:
            alert_id (int): Alert ID
            rule (dict): Alert rule
            inspection_data (dict): Inspection details
            
        Returns:
            bool: Success status
        """
        method = rule['method']
        recipients = rule['recipients']
        
        # Generate message
        subject, message = self._generate_alert_message(inspection_data)
        
        success = False
        
        if method in ['email', 'both']:
            for email in recipients:
                if '@' in email:
                    success = self._send_email(email, subject, message)
                    self._log_notification(alert_id, rule['user_id'], 'email', 
                                         email, subject, message, 
                                         'sent' if success else 'failed')
        
        if method in ['sms', 'both']:
            for phone in recipients:
                if phone.replace('+', '').replace('-', '').isdigit():
                    success = self._send_sms(phone, message)
                    self._log_notification(alert_id, rule['user_id'], 'sms',
                                         phone, subject, message,
                                         'sent' if success else 'failed')
        
        return success
    
    def _generate_alert_message(self, inspection_data):
        """Generate alert message content"""
        severity = inspection_data.get('severity_level', 'UNKNOWN')
        location = inspection_data.get('location', 'Unknown location')
        confidence = inspection_data.get('confidence', 0)
        crack_width = inspection_data.get('crack_width', 0)
        
        subject = f"🚨 CRITICAL ALERT: {severity} Crack Detected"
        
        message = f"""
CRACK DETECTION ALERT
{'='*50}

Severity Level: {severity}
Location: {location}
Confidence: {confidence}%
Crack Width: {crack_width}mm

Inspection Date: {inspection_data.get('date', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}
Inspector: {inspection_data.get('inspector', 'N/A')}

Action Required: {inspection_data.get('action', 'Immediate inspection recommended')}

{'='*50}
This is an automated alert from CrackDetect AI.
Please review the full inspection report for details.
        """
        
        return subject, message.strip()
    
    def _send_email(self, recipient, subject, message):
        """
        Send email notification
        
        Args:
            recipient (str): Email address
            subject (str): Email subject
            message (str): Email body
            
        Returns:
            bool: Success status
        """
        if not self.email_available:
            print(f"Email would be sent to {recipient}: {subject}")
            return False
        
        try:
            # Email configuration (should be in environment variables)
            smtp_server = "smtp.gmail.com"
            smtp_port = 587
            sender_email = "noreply@crackdetect.ai"
            sender_password = "your_app_password"  # Use app-specific password
            
            # Create message
            msg = self.MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = recipient
            msg['Subject'] = subject
            
            msg.attach(self.MIMEText(message, 'plain'))
            
            # Send email
            server = self.smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            server.quit()
            
            print(f"✅ Email sent to {recipient}")
            return True
            
        except Exception as e:
            print(f"❌ Email failed: {str(e)}")
            return False
    
    def _send_sms(self, phone_number, message):
        """
        Send SMS notification (requires Twilio or similar service)
        
        Args:
            phone_number (str): Phone number
            message (str): SMS text
            
        Returns:
            bool: Success status
        """
        # This would require Twilio API or similar
        # For now, just log it
        print(f"SMS would be sent to {phone_number}: {message[:50]}...")
        return False
    
    def _log_notification(self, alert_id, user_id, notification_type, 
                         recipient, subject, message, status):
        """Log notification attempt"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''INSERT INTO notification_log 
                     (alert_id, user_id, notification_type, recipient, 
                      subject, message, status)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  (alert_id, user_id, notification_type, recipient,
                   subject, message, status))
        
        conn.commit()
        conn.close()
    
    def get_notification_history(self, user_id, days=30):
        """Get notification history for a user"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''SELECT * FROM notification_log 
                     WHERE user_id = ? 
                     AND sent_at >= datetime('now', '-' || ? || ' days')
                     ORDER BY sent_at DESC''',
                  (user_id, days))
        
        history = c.fetchall()
        conn.close()
        
        return history
    
    def toggle_alert_rule(self, rule_id, is_active):
        """Enable/disable an alert rule"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('UPDATE alert_rules SET is_active = ? WHERE id = ?',
                  (is_active, rule_id))
        
        conn.commit()
        conn.close()
    
    def delete_alert_rule(self, rule_id):
        """Delete an alert rule"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('DELETE FROM alert_rules WHERE id = ?', (rule_id,))
        
        conn.commit()
        conn.close()
    
    def get_alert_statistics(self, user_id):
        """Get alert statistics for a user"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Total alerts
        c.execute('SELECT COUNT(*) FROM alerts WHERE user_id = ?', (user_id,))
        total_alerts = c.fetchone()[0]
        
        # Unread alerts
        c.execute('SELECT COUNT(*) FROM alerts WHERE user_id = ? AND is_read = 0', (user_id,))
        unread_alerts = c.fetchone()[0]
        
        # Alerts by severity
        c.execute('''SELECT severity, COUNT(*) FROM alerts 
                     WHERE user_id = ? GROUP BY severity''', (user_id,))
        by_severity = dict(c.fetchall())
        
        # Recent notifications
        c.execute('''SELECT COUNT(*) FROM notification_log 
                     WHERE user_id = ? 
                     AND sent_at >= datetime('now', '-7 days')''', (user_id,))
        recent_notifications = c.fetchone()[0]
        
        conn.close()
        
        return {
            'total_alerts': total_alerts,
            'unread_alerts': unread_alerts,
            'by_severity': by_severity,
            'recent_notifications': recent_notifications
        }


# Example usage
if __name__ == '__main__':
    alert_system = AlertSystem()
    
    print("Alert System Initialized")
    print("="*50)
    print("\nFeatures:")
    print("  • Create custom alert rules")
    print("  • Email notifications")
    print("  • SMS notifications (requires Twilio)")
    print("  • Severity-based triggers")
    print("  • Crack width triggers")
    print("  • Deterioration rate triggers")
    print("  • Notification history")
    print("  • Alert statistics")
    
    print("\nExample Alert Rule:")
    print("  Trigger: Severity >= HIGH")
    print("  Method: Email")
    print("  Recipients: engineer@company.com")
