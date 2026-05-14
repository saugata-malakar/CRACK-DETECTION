# Vercel Deployment Script
# Run: .\deploy_vercel.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Vercel Deployment Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Node.js is installed
try {
    $nodeVersion = node --version
    Write-Host "✓ Node.js installed: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js is not installed!" -ForegroundColor Red
    Write-Host "Please install Node.js from: https://nodejs.org/" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if Vercel CLI is installed
try {
    $vercelVersion = vercel --version
    Write-Host "✓ Vercel CLI installed: $vercelVersion" -ForegroundColor Green
} catch {
    Write-Host "⚠ Vercel CLI not found. Installing..." -ForegroundColor Yellow
    npm install -g vercel
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install Vercel CLI" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host "✓ Vercel CLI installed successfully" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Yellow
Write-Host "   Deploying to Vercel" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow
Write-Host ""

# Login check
Write-Host "Checking Vercel authentication..." -ForegroundColor Cyan
vercel whoami 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠ Not logged in to Vercel" -ForegroundColor Yellow
    Write-Host "Opening login page..." -ForegroundColor Cyan
    vercel login
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Login failed" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

Write-Host "✓ Authenticated with Vercel" -ForegroundColor Green
Write-Host ""

# Deploy
Write-Host "🚀 Deploying to Vercel..." -ForegroundColor Cyan
Write-Host ""

vercel --prod

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "   ✅ DEPLOYMENT SUCCESSFUL!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Your website is now live!" -ForegroundColor White
    Write-Host ""
    Write-Host "🌐 Production URL:" -ForegroundColor Cyan
    Write-Host "   https://concrete-crack-detection.vercel.app" -ForegroundColor Green
    Write-Host ""
    Write-Host "📊 Dashboard:" -ForegroundColor Cyan
    Write-Host "   https://vercel.com/dashboard" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "   ❌ DEPLOYMENT FAILED" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Common issues:" -ForegroundColor Yellow
    Write-Host "1. Check internet connection" -ForegroundColor White
    Write-Host "2. Verify Vercel account" -ForegroundColor White
    Write-Host "3. Check vercel.json configuration" -ForegroundColor White
    Write-Host ""
    Write-Host "For help, see: VERCEL_DEPLOY.md" -ForegroundColor Cyan
}

Write-Host ""
Read-Host "Press Enter to exit"
