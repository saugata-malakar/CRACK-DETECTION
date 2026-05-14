@echo off
echo ========================================
echo  CrackDetect AI - Installation Script
echo ========================================
echo.

echo Step 1: Installing dependencies...
pip install -r requirements.txt
echo.

echo Step 2: Initializing database tables...
python -c "from project_manager import ProjectManager; ProjectManager()"
python -c "from comparison_tracker import ComparisonTracker; ComparisonTracker()"
python -c "from image_annotator import ImageAnnotator; ImageAnnotator()"
python -c "from alert_system import AlertSystem; AlertSystem()"
echo.

echo Step 3: Creating reports directory...
if not exist "reports" mkdir reports
echo.

echo ========================================
echo  Installation Complete!
echo ========================================
echo.
echo New Features Added:
echo   1. Severity Classification (5 levels)
echo   2. Project Management
echo   3. PDF Report Generation
echo   4. Before/After Comparison
echo   5. Image Annotations
echo   6. Crack Measurements
echo   7. Alert System
echo   8. GPS Tagging
echo   9. Team Collaboration
echo  10. Compliance Reports
echo.
echo ========================================
echo  Starting Application...
echo ========================================
echo.
echo Local URL: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.

python app_commercial.py

pause
