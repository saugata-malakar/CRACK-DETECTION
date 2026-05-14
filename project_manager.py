"""
Project and Site Management Module
Organize inspections by projects, sites, and structures
"""

import sqlite3
from datetime import datetime
import json

class ProjectManager:
    """
    Manage projects, sites, and structures for crack inspections
    """
    
    def __init__(self, db_path='crack_detection.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize project management tables"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Projects table
        c.execute('''CREATE TABLE IF NOT EXISTS projects
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      user_id INTEGER,
                      name TEXT NOT NULL,
                      description TEXT,
                      location TEXT,
                      project_type TEXT,
                      status TEXT DEFAULT 'active',
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      FOREIGN KEY (user_id) REFERENCES users (id))''')
        
        # Sites table (buildings, bridges, etc.)
        c.execute('''CREATE TABLE IF NOT EXISTS sites
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      project_id INTEGER,
                      name TEXT NOT NULL,
                      site_type TEXT,
                      address TEXT,
                      gps_latitude REAL,
                      gps_longitude REAL,
                      construction_year INTEGER,
                      last_inspection_date TIMESTAMP,
                      health_score REAL DEFAULT 100.0,
                      status TEXT DEFAULT 'active',
                      notes TEXT,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      FOREIGN KEY (project_id) REFERENCES projects (id))''')
        
        # Structures table (specific elements like columns, beams, etc.)
        c.execute('''CREATE TABLE IF NOT EXISTS structures
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      site_id INTEGER,
                      name TEXT NOT NULL,
                      structure_type TEXT,
                      material TEXT,
                      dimensions TEXT,
                      location_description TEXT,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      FOREIGN KEY (site_id) REFERENCES sites (id))''')
        
        # Inspections table (enhanced)
        c.execute('''CREATE TABLE IF NOT EXISTS inspections
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      user_id INTEGER,
                      project_id INTEGER,
                      site_id INTEGER,
                      structure_id INTEGER,
                      prediction_id INTEGER,
                      inspector_name TEXT,
                      inspection_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      severity_level TEXT,
                      crack_width REAL,
                      crack_length REAL,
                      gps_latitude REAL,
                      gps_longitude REAL,
                      weather_conditions TEXT,
                      temperature REAL,
                      notes TEXT,
                      images TEXT,
                      status TEXT DEFAULT 'completed',
                      FOREIGN KEY (user_id) REFERENCES users (id),
                      FOREIGN KEY (project_id) REFERENCES projects (id),
                      FOREIGN KEY (site_id) REFERENCES sites (id),
                      FOREIGN KEY (structure_id) REFERENCES structures (id),
                      FOREIGN KEY (prediction_id) REFERENCES predictions (id))''')
        
        # Team members table
        c.execute('''CREATE TABLE IF NOT EXISTS team_members
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      project_id INTEGER,
                      user_id INTEGER,
                      role TEXT,
                      permissions TEXT,
                      added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      FOREIGN KEY (project_id) REFERENCES projects (id),
                      FOREIGN KEY (user_id) REFERENCES users (id))''')
        
        # Alerts table
        c.execute('''CREATE TABLE IF NOT EXISTS alerts
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      user_id INTEGER,
                      inspection_id INTEGER,
                      alert_type TEXT,
                      severity TEXT,
                      message TEXT,
                      is_read BOOLEAN DEFAULT 0,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      FOREIGN KEY (user_id) REFERENCES users (id),
                      FOREIGN KEY (inspection_id) REFERENCES inspections (id))''')
        
        conn.commit()
        conn.close()
    
    # ==================== PROJECT MANAGEMENT ====================
    
    def create_project(self, user_id, name, description='', location='', project_type='General'):
        """Create a new project"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''INSERT INTO projects (user_id, name, description, location, project_type)
                     VALUES (?, ?, ?, ?, ?)''',
                  (user_id, name, description, location, project_type))
        
        project_id = c.lastrowid
        conn.commit()
        conn.close()
        
        return project_id
    
    def get_user_projects(self, user_id):
        """Get all projects for a user"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''SELECT p.*, 
                     COUNT(DISTINCT s.id) as site_count,
                     COUNT(DISTINCT i.id) as inspection_count
                     FROM projects p
                     LEFT JOIN sites s ON p.id = s.project_id
                     LEFT JOIN inspections i ON p.id = i.project_id
                     WHERE p.user_id = ?
                     GROUP BY p.id
                     ORDER BY p.updated_at DESC''', (user_id,))
        
        projects = c.fetchall()
        conn.close()
        
        return projects
    
    def get_project(self, project_id):
        """Get project details"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('SELECT * FROM projects WHERE id = ?', (project_id,))
        project = c.fetchone()
        
        conn.close()
        return project
    
    def update_project(self, project_id, **kwargs):
        """Update project details"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Build update query dynamically
        fields = ', '.join([f"{k} = ?" for k in kwargs.keys()])
        values = list(kwargs.values()) + [project_id]
        
        c.execute(f'UPDATE projects SET {fields}, updated_at = CURRENT_TIMESTAMP WHERE id = ?', values)
        
        conn.commit()
        conn.close()
    
    # ==================== SITE MANAGEMENT ====================
    
    def create_site(self, project_id, name, site_type, address='', gps_lat=None, gps_lon=None, **kwargs):
        """Create a new site"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''INSERT INTO sites (project_id, name, site_type, address, 
                     gps_latitude, gps_longitude, construction_year, notes)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                  (project_id, name, site_type, address, gps_lat, gps_lon,
                   kwargs.get('construction_year'), kwargs.get('notes', '')))
        
        site_id = c.lastrowid
        conn.commit()
        conn.close()
        
        return site_id
    
    def get_project_sites(self, project_id):
        """Get all sites for a project"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''SELECT s.*, 
                     COUNT(DISTINCT i.id) as inspection_count,
                     MAX(i.inspection_date) as last_inspection
                     FROM sites s
                     LEFT JOIN inspections i ON s.id = i.site_id
                     WHERE s.project_id = ?
                     GROUP BY s.id
                     ORDER BY s.created_at DESC''', (project_id,))
        
        sites = c.fetchall()
        conn.close()
        
        return sites
    
    def update_site_health_score(self, site_id, health_score):
        """Update site health score based on inspections"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('UPDATE sites SET health_score = ?, last_inspection_date = CURRENT_TIMESTAMP WHERE id = ?',
                  (health_score, site_id))
        
        conn.commit()
        conn.close()
    
    # ==================== STRUCTURE MANAGEMENT ====================
    
    def create_structure(self, site_id, name, structure_type, material='Concrete', **kwargs):
        """Create a new structure element"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''INSERT INTO structures (site_id, name, structure_type, material, 
                     dimensions, location_description)
                     VALUES (?, ?, ?, ?, ?, ?)''',
                  (site_id, name, structure_type, material,
                   kwargs.get('dimensions', ''), kwargs.get('location_description', '')))
        
        structure_id = c.lastrowid
        conn.commit()
        conn.close()
        
        return structure_id
    
    def get_site_structures(self, site_id):
        """Get all structures for a site"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('SELECT * FROM structures WHERE site_id = ? ORDER BY created_at DESC', (site_id,))
        structures = c.fetchall()
        
        conn.close()
        return structures
    
    # ==================== INSPECTION MANAGEMENT ====================
    
    def create_inspection(self, user_id, prediction_id, **kwargs):
        """Create a detailed inspection record"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''INSERT INTO inspections (user_id, project_id, site_id, structure_id,
                     prediction_id, inspector_name, severity_level, crack_width, crack_length,
                     gps_latitude, gps_longitude, weather_conditions, temperature, notes, images)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (user_id, kwargs.get('project_id'), kwargs.get('site_id'), kwargs.get('structure_id'),
                   prediction_id, kwargs.get('inspector_name'), kwargs.get('severity_level'),
                   kwargs.get('crack_width'), kwargs.get('crack_length'),
                   kwargs.get('gps_latitude'), kwargs.get('gps_longitude'),
                   kwargs.get('weather_conditions'), kwargs.get('temperature'),
                   kwargs.get('notes', ''), kwargs.get('images', '')))
        
        inspection_id = c.lastrowid
        conn.commit()
        conn.close()
        
        return inspection_id
    
    def get_site_inspections(self, site_id):
        """Get all inspections for a site"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''SELECT i.*, p.prediction, p.confidence, p.model_used
                     FROM inspections i
                     LEFT JOIN predictions p ON i.prediction_id = p.id
                     WHERE i.site_id = ?
                     ORDER BY i.inspection_date DESC''', (site_id,))
        
        inspections = c.fetchall()
        conn.close()
        
        return inspections
    
    # ==================== TEAM COLLABORATION ====================
    
    def add_team_member(self, project_id, user_id, role='Inspector', permissions='view'):
        """Add team member to project"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''INSERT INTO team_members (project_id, user_id, role, permissions)
                     VALUES (?, ?, ?, ?)''',
                  (project_id, user_id, role, permissions))
        
        conn.commit()
        conn.close()
    
    def get_project_team(self, project_id):
        """Get all team members for a project"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''SELECT tm.*, u.username, u.email
                     FROM team_members tm
                     JOIN users u ON tm.user_id = u.id
                     WHERE tm.project_id = ?''', (project_id,))
        
        team = c.fetchall()
        conn.close()
        
        return team
    
    # ==================== ALERTS ====================
    
    def create_alert(self, user_id, inspection_id, alert_type, severity, message):
        """Create an alert for critical findings"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''INSERT INTO alerts (user_id, inspection_id, alert_type, severity, message)
                     VALUES (?, ?, ?, ?, ?)''',
                  (user_id, inspection_id, alert_type, severity, message))
        
        alert_id = c.lastrowid
        conn.commit()
        conn.close()
        
        return alert_id
    
    def get_user_alerts(self, user_id, unread_only=False):
        """Get alerts for a user"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        query = 'SELECT * FROM alerts WHERE user_id = ?'
        if unread_only:
            query += ' AND is_read = 0'
        query += ' ORDER BY created_at DESC'
        
        c.execute(query, (user_id,))
        alerts = c.fetchall()
        
        conn.close()
        return alerts


# Example usage
if __name__ == '__main__':
    pm = ProjectManager()
    
    print("Project Management System Initialized")
    print("="*50)
    print("\nDatabase tables created:")
    print("  • projects")
    print("  • sites")
    print("  • structures")
    print("  • inspections")
    print("  • team_members")
    print("  • alerts")
