# GitHub Deployment Script
# Run this in PowerShell: .\deploy.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   GitHub Deployment Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Get GitHub username
$username = Read-Host "Enter your GitHub username"
if ([string]::IsNullOrWhiteSpace($username)) {
    Write-Host "ERROR: Username cannot be empty!" -ForegroundColor Red
    exit 1
}

$repoName = "concrete-crack-detection"
$repoUrl = "https://github.com/$username/$repoName.git"

Write-Host ""
Write-Host "Repository will be created at:" -ForegroundColor Yellow
Write-Host $repoUrl -ForegroundColor Green
Write-Host ""

# Confirm
$confirm = Read-Host "Continue? (yes/no)"
if ($confirm -ne "yes" -and $confirm -ne "y") {
    Write-Host "Deployment cancelled." -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "Step 1: Initializing Git repository..." -ForegroundColor Cyan
git init
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to initialize Git" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Git initialized" -ForegroundColor Green

Write-Host ""
Write-Host "Step 2: Adding all files..." -ForegroundColor Cyan
git add .
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to add files" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Files added" -ForegroundColor Green

Write-Host ""
Write-Host "Step 3: Creating initial commit..." -ForegroundColor Cyan
git commit -m "Initial commit: AI-powered concrete crack detection system with 97% accuracy"
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to create commit" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Commit created" -ForegroundColor Green

Write-Host ""
Write-Host "Step 4: Renaming branch to main..." -ForegroundColor Cyan
git branch -M main
Write-Host "✓ Branch renamed" -ForegroundColor Green

Write-Host ""
Write-Host "Step 5: Adding remote repository..." -ForegroundColor Cyan
git remote add origin $repoUrl
if ($LASTEXITCODE -ne 0) {
    Write-Host "WARNING: Remote might already exist, removing and re-adding..." -ForegroundColor Yellow
    git remote remove origin
    git remote add origin $repoUrl
}
Write-Host "✓ Remote added" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Yellow
Write-Host "   IMPORTANT: Create GitHub Repository" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "Before pushing, you need to create the repository on GitHub:" -ForegroundColor White
Write-Host ""
Write-Host "1. Go to: https://github.com/new" -ForegroundColor Cyan
Write-Host "2. Repository name: $repoName" -ForegroundColor Cyan
Write-Host "3. Description: AI-powered crack detection (97% accuracy)" -ForegroundColor Cyan
Write-Host "4. Choose: Public" -ForegroundColor Cyan
Write-Host "5. DO NOT initialize with README" -ForegroundColor Red
Write-Host "6. Click 'Create repository'" -ForegroundColor Cyan
Write-Host ""

$created = Read-Host "Have you created the repository? (yes/no)"
if ($created -ne "yes" -and $created -ne "y") {
    Write-Host ""
    Write-Host "Please create the repository first, then run this script again." -ForegroundColor Yellow
    Write-Host "Or manually run: git push -u origin main" -ForegroundColor Cyan
    exit 0
}

Write-Host ""
Write-Host "Step 6: Pushing to GitHub..." -ForegroundColor Cyan
git push -u origin main
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERROR: Failed to push to GitHub" -ForegroundColor Red
    Write-Host ""
    Write-Host "Possible reasons:" -ForegroundColor Yellow
    Write-Host "1. Repository doesn't exist on GitHub" -ForegroundColor White
    Write-Host "2. Authentication failed (need to login)" -ForegroundColor White
    Write-Host "3. Wrong username" -ForegroundColor White
    Write-Host ""
    Write-Host "Try manually:" -ForegroundColor Cyan
    Write-Host "git push -u origin main" -ForegroundColor Green
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "   ✓ DEPLOYMENT SUCCESSFUL!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Your project is now on GitHub!" -ForegroundColor White
Write-Host ""
Write-Host "Repository URL:" -ForegroundColor Cyan
Write-Host "https://github.com/$username/$repoName" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Enable GitHub Pages:" -ForegroundColor White
Write-Host "   - Go to: https://github.com/$username/$repoName/settings/pages" -ForegroundColor Cyan
Write-Host "   - Source: main branch" -ForegroundColor Cyan
Write-Host "   - Click Save" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Your website will be live at:" -ForegroundColor White
Write-Host "   https://$username.github.io/$repoName/" -ForegroundColor Green
Write-Host ""
Write-Host "3. Add topics/tags:" -ForegroundColor White
Write-Host "   - deep-learning, pytorch, computer-vision, crack-detection" -ForegroundColor Cyan
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
