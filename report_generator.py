"""
PDF Report Generation Module
Generate professional inspection reports for engineers
"""

from datetime import datetime
import base64
import io

class ReportGenerator:
    """
    Generate professional PDF reports for crack inspections
    Note: This uses reportlab library. Install with: pip install reportlab
    """
    
    def __init__(self):
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.lib import colors
            from reportlab.lib.units import inch
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
            
            self.reportlab_available = True
            self.letter = letter
            self.A4 = A4
            self.colors = colors
            self.inch = inch
            self.SimpleDocTemplate = SimpleDocTemplate
            self.Table = Table
            self.TableStyle = TableStyle
            self.Paragraph = Paragraph
            self.Spacer = Spacer
            self.Image = Image
            self.PageBreak = PageBreak
            self.getSampleStyleSheet = getSampleStyleSheet
            self.ParagraphStyle = ParagraphStyle
            self.TA_CENTER = TA_CENTER
            self.TA_LEFT = TA_LEFT
            self.TA_RIGHT = TA_RIGHT
            
        except ImportError:
            self.reportlab_available = False
            print("Warning: reportlab not installed. Install with: pip install reportlab")
    
    def generate_inspection_report(self, inspection_data, output_path='inspection_report.pdf'):
        """
        Generate a professional inspection report
        
        Args:
            inspection_data (dict): Inspection details
            output_path (str): Output PDF file path
            
        Returns:
            str: Path to generated PDF
        """
        
        if not self.reportlab_available:
            return self._generate_html_report(inspection_data, output_path.replace('.pdf', '.html'))
        
        # Create PDF document
        doc = self.SimpleDocTemplate(output_path, pagesize=self.letter)
        story = []
        styles = self.getSampleStyleSheet()
        
        # Custom styles
        title_style = self.ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=self.colors.HexColor('#667eea'),
            spaceAfter=30,
            alignment=self.TA_CENTER
        )
        
        heading_style = self.ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=self.colors.HexColor('#764ba2'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        # Title
        story.append(self.Paragraph("CONCRETE CRACK INSPECTION REPORT", title_style))
        story.append(self.Spacer(1, 0.3*self.inch))
        
        # Report metadata
        metadata = [
            ['Report ID:', inspection_data.get('id', 'N/A')],
            ['Inspection Date:', inspection_data.get('date', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))],
            ['Inspector:', inspection_data.get('inspector', 'N/A')],
            ['Location:', inspection_data.get('location', 'N/A')],
        ]
        
        metadata_table = self.Table(metadata, colWidths=[2*self.inch, 4*self.inch])
        metadata_table.setStyle(self.TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), self.colors.HexColor('#f3f4f6')),
            ('TEXTCOLOR', (0, 0), (-1, -1), self.colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, self.colors.grey)
        ]))
        
        story.append(metadata_table)
        story.append(self.Spacer(1, 0.5*self.inch))
        
        # Executive Summary
        story.append(self.Paragraph("EXECUTIVE SUMMARY", heading_style))
        
        severity = inspection_data.get('severity', {})
        severity_color = self.colors.HexColor(severity.get('color', '#10b981'))
        
        summary_data = [
            ['Prediction:', inspection_data.get('prediction', 'N/A')],
            ['Confidence:', f"{inspection_data.get('confidence', 0)}%"],
            ['Severity Level:', severity.get('level', 'N/A')],
            ['Action Required:', severity.get('action', 'N/A')],
        ]
        
        summary_table = self.Table(summary_data, colWidths=[2*self.inch, 4*self.inch])
        summary_table.setStyle(self.TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), self.colors.HexColor('#f3f4f6')),
            ('BACKGROUND', (1, 2), (1, 2), severity_color),
            ('TEXTCOLOR', (0, 0), (-1, -1), self.colors.black),
            ('TEXTCOLOR', (1, 2), (1, 2), self.colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, self.colors.grey)
        ]))
        
        story.append(summary_table)
        story.append(self.Spacer(1, 0.5*self.inch))
        
        # Inspection Image
        if inspection_data.get('image'):
            story.append(self.Paragraph("INSPECTION IMAGE", heading_style))
            try:
                # Handle base64 image
                image_data = inspection_data['image']
                if image_data.startswith('data:image'):
                    image_data = image_data.split(',')[1]
                
                img_buffer = io.BytesIO(base64.b64decode(image_data))
                img = self.Image(img_buffer, width=5*self.inch, height=4*self.inch)
                story.append(img)
                story.append(self.Spacer(1, 0.3*self.inch))
            except Exception as e:
                story.append(self.Paragraph(f"Image could not be loaded: {str(e)}", styles['Normal']))
        
        # Detailed Analysis
        story.append(self.Paragraph("DETAILED ANALYSIS", heading_style))
        
        analysis_text = f"""
        <b>Description:</b> {severity.get('description', 'N/A')}<br/>
        <br/>
        <b>Model Used:</b> {inspection_data.get('model', 'N/A')}<br/>
        <b>Timestamp:</b> {inspection_data.get('timestamp', 'N/A')}<br/>
        """
        
        if inspection_data.get('crack_width'):
            analysis_text += f"<br/><b>Estimated Crack Width:</b> {inspection_data['crack_width']} mm<br/>"
        
        if inspection_data.get('notes'):
            analysis_text += f"<br/><b>Inspector Notes:</b> {inspection_data['notes']}<br/>"
        
        story.append(self.Paragraph(analysis_text, styles['Normal']))
        story.append(self.Spacer(1, 0.3*self.inch))
        
        # Repair Recommendations
        if inspection_data.get('repair_recommendations'):
            story.append(self.Paragraph("REPAIR RECOMMENDATIONS", heading_style))
            
            repair = inspection_data['repair_recommendations']
            
            repair_data = [
                ['Repair Type:', repair.get('repair_type', 'N/A')],
                ['Urgency:', repair.get('urgency', 'N/A')],
                ['Estimated Cost:', repair.get('estimated_cost', 'N/A')],
                ['Timeline:', repair.get('timeline', 'N/A')],
            ]
            
            repair_table = self.Table(repair_data, colWidths=[2*self.inch, 4*self.inch])
            repair_table.setStyle(self.TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), self.colors.HexColor('#f3f4f6')),
                ('TEXTCOLOR', (0, 0), (-1, -1), self.colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, self.colors.grey)
            ]))
            
            story.append(repair_table)
            story.append(self.Spacer(1, 0.3*self.inch))
            
            # Repair methods
            if repair.get('methods'):
                story.append(self.Paragraph("<b>Recommended Methods:</b>", styles['Normal']))
                for method in repair['methods']:
                    story.append(self.Paragraph(f"• {method}", styles['Normal']))
                story.append(self.Spacer(1, 0.3*self.inch))
        
        # Compliance Status
        if inspection_data.get('compliance'):
            story.append(self.Paragraph("COMPLIANCE STATUS", heading_style))
            
            compliance = inspection_data['compliance']
            
            compliance_data = [
                ['Standard', 'Status'],
                ['AASHTO', compliance.get('aashto', 'N/A')],
                ['ACI', compliance.get('aci', 'N/A')],
                ['Eurocode', compliance.get('eurocode', 'N/A')],
                ['IS Code', compliance.get('is_code', 'N/A')],
                ['Overall', compliance.get('overall', 'N/A')],
            ]
            
            compliance_table = self.Table(compliance_data, colWidths=[3*self.inch, 3*self.inch])
            compliance_table.setStyle(self.TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.colors.HexColor('#667eea')),
                ('TEXTCOLOR', (0, 0), (-1, 0), self.colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, self.colors.grey)
            ]))
            
            story.append(compliance_table)
        
        # Footer
        story.append(self.Spacer(1, 0.5*self.inch))
        footer_text = f"""
        <br/><br/>
        <i>This report was generated by CrackDetect AI on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i><br/>
        <i>For questions or concerns, please contact your structural engineer.</i>
        """
        story.append(self.Paragraph(footer_text, styles['Normal']))
        
        # Build PDF
        doc.build(story)
        
        return output_path
    
    def _generate_html_report(self, inspection_data, output_path='inspection_report.html'):
        """
        Generate HTML report as fallback when reportlab is not available
        """
        
        severity = inspection_data.get('severity', {})
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Inspection Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                h1 {{ color: #667eea; text-align: center; }}
                h2 {{ color: #764ba2; border-bottom: 2px solid #764ba2; padding-bottom: 10px; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
                th {{ background-color: #667eea; color: white; }}
                .severity {{ background-color: {severity.get('color', '#10b981')}; color: white; padding: 10px; border-radius: 5px; }}
                img {{ max-width: 600px; height: auto; }}
            </style>
        </head>
        <body>
            <h1>CONCRETE CRACK INSPECTION REPORT</h1>
            
            <h2>Report Information</h2>
            <table>
                <tr><th>Report ID</th><td>{inspection_data.get('id', 'N/A')}</td></tr>
                <tr><th>Inspection Date</th><td>{inspection_data.get('date', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}</td></tr>
                <tr><th>Inspector</th><td>{inspection_data.get('inspector', 'N/A')}</td></tr>
                <tr><th>Location</th><td>{inspection_data.get('location', 'N/A')}</td></tr>
            </table>
            
            <h2>Executive Summary</h2>
            <table>
                <tr><th>Prediction</th><td>{inspection_data.get('prediction', 'N/A')}</td></tr>
                <tr><th>Confidence</th><td>{inspection_data.get('confidence', 0)}%</td></tr>
                <tr><th>Severity Level</th><td class="severity">{severity.get('level', 'N/A')}</td></tr>
                <tr><th>Action Required</th><td>{severity.get('action', 'N/A')}</td></tr>
            </table>
            
            <h2>Inspection Image</h2>
            <img src="{inspection_data.get('image', '')}" alt="Inspection Image"/>
            
            <p><i>Generated by CrackDetect AI on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i></p>
        </body>
        </html>
        """
        
        with open(output_path, 'w') as f:
            f.write(html_content)
        
        return output_path


# Example usage
if __name__ == '__main__':
    generator = ReportGenerator()
    
    # Sample inspection data
    sample_data = {
        'id': 'INS-2024-001',
        'date': '2024-01-15 10:30:00',
        'inspector': 'John Doe, P.E.',
        'location': 'Main Street Bridge, Column A3',
        'prediction': 'Cracked',
        'confidence': 96.5,
        'model': 'ResNet-50',
        'timestamp': '2024-01-15 10:30:45',
        'severity': {
            'level': 'HIGH',
            'color': '#ef4444',
            'description': 'Significant cracks, structural concern',
            'action': 'Inspect within 7 days, plan repairs'
        },
        'crack_width': 3.2,
        'notes': 'Crack observed on north face of column, extending vertically.',
        'repair_recommendations': {
            'repair_type': 'Structural',
            'urgency': 'High',
            'estimated_cost': '$5,000-8,000',
            'timeline': '2-3 weeks',
            'methods': [
                'Structural epoxy injection',
                'Carbon fiber reinforcement',
                'Load testing required'
            ]
        },
        'compliance': {
            'aashto': 'FAIL',
            'aci': 'FAIL',
            'eurocode': 'FAIL',
            'is_code': 'FAIL',
            'overall': 'NON-COMPLIANT'
        }
    }
    
    print("Report Generator Ready")
    print("="*50)
    print("\nTo generate a report, call:")
    print("generator.generate_inspection_report(inspection_data, 'output.pdf')")
