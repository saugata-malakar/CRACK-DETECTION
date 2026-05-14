"""
Image Annotation Module
Mark and annotate crack locations on images
"""

import sqlite3
import json
from datetime import datetime
import base64
import io

class ImageAnnotator:
    """
    Annotate images with crack locations, measurements, and notes
    """
    
    def __init__(self, db_path='crack_detection.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize annotation tables"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Annotations table
        c.execute('''CREATE TABLE IF NOT EXISTS annotations
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      inspection_id INTEGER,
                      user_id INTEGER,
                      annotation_type TEXT,
                      coordinates TEXT,
                      measurements TEXT,
                      label TEXT,
                      description TEXT,
                      color TEXT DEFAULT '#ef4444',
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      FOREIGN KEY (inspection_id) REFERENCES inspections (id),
                      FOREIGN KEY (user_id) REFERENCES users (id))''')
        
        # Annotated images table
        c.execute('''CREATE TABLE IF NOT EXISTS annotated_images
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      inspection_id INTEGER,
                      original_image TEXT,
                      annotated_image TEXT,
                      annotation_count INTEGER DEFAULT 0,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      FOREIGN KEY (inspection_id) REFERENCES inspections (id))''')
        
        conn.commit()
        conn.close()
    
    def create_annotation(self, inspection_id, user_id, annotation_data):
        """
        Create a new annotation
        
        Args:
            inspection_id (int): Inspection ID
            user_id (int): User ID
            annotation_data (dict): Annotation details
                - type: 'line', 'arrow', 'rectangle', 'circle', 'polygon', 'text'
                - coordinates: List of points
                - measurements: Dict with width, length, area
                - label: Text label
                - description: Detailed description
                - color: Hex color code
                
        Returns:
            int: Annotation ID
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''INSERT INTO annotations 
                     (inspection_id, user_id, annotation_type, coordinates, 
                      measurements, label, description, color)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                  (inspection_id, user_id,
                   annotation_data.get('type', 'line'),
                   json.dumps(annotation_data.get('coordinates', [])),
                   json.dumps(annotation_data.get('measurements', {})),
                   annotation_data.get('label', ''),
                   annotation_data.get('description', ''),
                   annotation_data.get('color', '#ef4444')))
        
        annotation_id = c.lastrowid
        conn.commit()
        conn.close()
        
        return annotation_id
    
    def get_inspection_annotations(self, inspection_id):
        """
        Get all annotations for an inspection
        
        Args:
            inspection_id (int): Inspection ID
            
        Returns:
            list: Annotations
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''SELECT a.*, u.username 
                     FROM annotations a
                     LEFT JOIN users u ON a.user_id = u.id
                     WHERE a.inspection_id = ?
                     ORDER BY a.created_at ASC''', (inspection_id,))
        
        annotations = c.fetchall()
        conn.close()
        
        # Parse JSON fields
        parsed_annotations = []
        for ann in annotations:
            parsed_annotations.append({
                'id': ann[0],
                'inspection_id': ann[1],
                'user_id': ann[2],
                'type': ann[3],
                'coordinates': json.loads(ann[4]) if ann[4] else [],
                'measurements': json.loads(ann[5]) if ann[5] else {},
                'label': ann[6],
                'description': ann[7],
                'color': ann[8],
                'created_at': ann[9],
                'updated_at': ann[10],
                'username': ann[11] if len(ann) > 11 else None
            })
        
        return parsed_annotations
    
    def update_annotation(self, annotation_id, **kwargs):
        """
        Update annotation
        
        Args:
            annotation_id (int): Annotation ID
            **kwargs: Fields to update
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Build update query
        updates = []
        values = []
        
        for key, value in kwargs.items():
            if key in ['coordinates', 'measurements']:
                updates.append(f"{key} = ?")
                values.append(json.dumps(value))
            else:
                updates.append(f"{key} = ?")
                values.append(value)
        
        if updates:
            query = f"UPDATE annotations SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
            values.append(annotation_id)
            c.execute(query, values)
        
        conn.commit()
        conn.close()
    
    def delete_annotation(self, annotation_id):
        """Delete annotation"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('DELETE FROM annotations WHERE id = ?', (annotation_id,))
        
        conn.commit()
        conn.close()
    
    def save_annotated_image(self, inspection_id, original_image, annotated_image):
        """
        Save annotated image
        
        Args:
            inspection_id (int): Inspection ID
            original_image (str): Base64 original image
            annotated_image (str): Base64 annotated image
            
        Returns:
            int: Annotated image ID
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Count annotations
        c.execute('SELECT COUNT(*) FROM annotations WHERE inspection_id = ?', (inspection_id,))
        annotation_count = c.fetchone()[0]
        
        # Check if already exists
        c.execute('SELECT id FROM annotated_images WHERE inspection_id = ?', (inspection_id,))
        existing = c.fetchone()
        
        if existing:
            # Update existing
            c.execute('''UPDATE annotated_images 
                         SET annotated_image = ?, annotation_count = ?
                         WHERE inspection_id = ?''',
                      (annotated_image, annotation_count, inspection_id))
            image_id = existing[0]
        else:
            # Create new
            c.execute('''INSERT INTO annotated_images 
                         (inspection_id, original_image, annotated_image, annotation_count)
                         VALUES (?, ?, ?, ?)''',
                      (inspection_id, original_image, annotated_image, annotation_count))
            image_id = c.lastrowid
        
        conn.commit()
        conn.close()
        
        return image_id
    
    def get_annotated_image(self, inspection_id):
        """
        Get annotated image for inspection
        
        Args:
            inspection_id (int): Inspection ID
            
        Returns:
            dict: Image data
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('SELECT * FROM annotated_images WHERE inspection_id = ?', (inspection_id,))
        image = c.fetchone()
        
        conn.close()
        
        if image:
            return {
                'id': image[0],
                'inspection_id': image[1],
                'original_image': image[2],
                'annotated_image': image[3],
                'annotation_count': image[4],
                'created_at': image[5]
            }
        
        return None
    
    def generate_annotation_summary(self, inspection_id):
        """
        Generate summary of all annotations
        
        Args:
            inspection_id (int): Inspection ID
            
        Returns:
            dict: Summary statistics
        """
        annotations = self.get_inspection_annotations(inspection_id)
        
        summary = {
            'total_annotations': len(annotations),
            'by_type': {},
            'total_crack_length': 0,
            'average_crack_width': 0,
            'max_crack_width': 0,
            'critical_areas': 0,
            'annotations': []
        }
        
        crack_widths = []
        
        for ann in annotations:
            # Count by type
            ann_type = ann['type']
            summary['by_type'][ann_type] = summary['by_type'].get(ann_type, 0) + 1
            
            # Measurements
            measurements = ann.get('measurements', {})
            if measurements.get('length'):
                summary['total_crack_length'] += measurements['length']
            
            if measurements.get('width'):
                crack_widths.append(measurements['width'])
                summary['max_crack_width'] = max(summary['max_crack_width'], measurements['width'])
            
            # Critical areas (red annotations)
            if ann.get('color') == '#ef4444' or ann.get('label', '').upper() == 'CRITICAL':
                summary['critical_areas'] += 1
            
            # Add to list
            summary['annotations'].append({
                'id': ann['id'],
                'type': ann['type'],
                'label': ann['label'],
                'description': ann['description'],
                'measurements': measurements
            })
        
        # Calculate averages
        if crack_widths:
            summary['average_crack_width'] = sum(crack_widths) / len(crack_widths)
        
        return summary
    
    def get_annotation_templates(self):
        """
        Get predefined annotation templates
        
        Returns:
            dict: Annotation templates
        """
        return {
            'crack_line': {
                'type': 'line',
                'label': 'Crack',
                'color': '#ef4444',
                'description': 'Linear crack'
            },
            'crack_area': {
                'type': 'polygon',
                'label': 'Crack Area',
                'color': '#f59e0b',
                'description': 'Area with multiple cracks'
            },
            'spalling': {
                'type': 'circle',
                'label': 'Spalling',
                'color': '#8b5cf6',
                'description': 'Concrete spalling'
            },
            'corrosion': {
                'type': 'rectangle',
                'label': 'Corrosion',
                'color': '#f97316',
                'description': 'Rebar corrosion'
            },
            'measurement': {
                'type': 'arrow',
                'label': 'Measurement',
                'color': '#3b82f6',
                'description': 'Dimension measurement'
            },
            'note': {
                'type': 'text',
                'label': 'Note',
                'color': '#10b981',
                'description': 'Inspector note'
            }
        }
    
    def export_annotations_to_json(self, inspection_id):
        """
        Export annotations to JSON format
        
        Args:
            inspection_id (int): Inspection ID
            
        Returns:
            str: JSON string
        """
        annotations = self.get_inspection_annotations(inspection_id)
        summary = self.generate_annotation_summary(inspection_id)
        
        export_data = {
            'inspection_id': inspection_id,
            'export_date': datetime.now().isoformat(),
            'summary': summary,
            'annotations': annotations
        }
        
        return json.dumps(export_data, indent=2)
    
    def import_annotations_from_json(self, inspection_id, user_id, json_data):
        """
        Import annotations from JSON
        
        Args:
            inspection_id (int): Inspection ID
            user_id (int): User ID
            json_data (str): JSON string
            
        Returns:
            int: Number of annotations imported
        """
        data = json.loads(json_data)
        count = 0
        
        for ann in data.get('annotations', []):
            self.create_annotation(inspection_id, user_id, ann)
            count += 1
        
        return count


# Example usage
if __name__ == '__main__':
    annotator = ImageAnnotator()
    
    print("Image Annotator Initialized")
    print("="*50)
    print("\nAnnotation Types:")
    print("  • Line - Mark linear cracks")
    print("  • Arrow - Show measurements")
    print("  • Rectangle - Highlight areas")
    print("  • Circle - Mark spalling")
    print("  • Polygon - Define crack zones")
    print("  • Text - Add notes")
    
    print("\nFeatures:")
    print("  • Create/Update/Delete annotations")
    print("  • Save annotated images")
    print("  • Generate summaries")
    print("  • Export/Import JSON")
    print("  • Predefined templates")
