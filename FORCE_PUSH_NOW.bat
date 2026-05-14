@echo off
echo ========================================
echo   FIXING GITHUB LARGE FILE ERROR
echo ========================================
echo.

echo Step 1: Removing large AI models from tracking...
git rm -r --cached checkpoints/best_model.pth

echo.
echo Step 2: Updating .gitignore...
git add .gitignore

echo.
echo Step 3: Re-committing without the large files...
git commit -m "Removed large model files to fix GitHub push error"

echo.
echo Step 4: Pushing code to GitHub...
git push -u origin main --force

echo.
echo ========================================
echo   DONE! Check your GitHub!
echo ========================================
pause
