@echo off
echo ========================================
echo   WIPING GIT HISTORY AND PUSHING
echo ========================================
echo.

echo Step 1: Destroying old corrupted Git history...
rmdir /s /q .git

echo Step 2: Starting a fresh Git repository...
git init

echo Step 3: Adding files (including new deployment configs: wsgi.py, runtime.txt, render.yaml)...
git add .

echo Step 4: Committing fresh changes...
git commit -m "Final Commercial Release: Fixed PDF and Render config"

echo Step 5: Setting branch to main...
git branch -M main

echo Step 6: Pushing forcefully to GitHub...
git remote add origin https://github.com/saugata-malakar/CRACK-DETECTION.git
git push -u origin main --force

echo.
echo ========================================
echo   DONE!
echo ========================================
pause
