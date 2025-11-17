# Build script for Render deployment (Windows version)
# This script can be run locally to verify deployment readiness

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "🚀 Course Compass - Build Verification" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# Display Python version
Write-Host ""
Write-Host "📍 Python Version:" -ForegroundColor Yellow
python --version

# Verify requirements.txt exists
Write-Host ""
if (Test-Path "requirements.txt") {
    Write-Host "✓ requirements.txt found" -ForegroundColor Green
} else {
    Write-Host "✗ requirements.txt not found!" -ForegroundColor Red
    exit 1
}

# Install dependencies
Write-Host ""
Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Verify critical packages
Write-Host ""
Write-Host "✅ Verifying installations..." -ForegroundColor Yellow

try {
    python -c "import flask; print('  ✓ Flask installed')"
    python -c "import supabase; print('  ✓ Supabase installed')"
    python -c "import gunicorn; print('  ✓ Gunicorn installed')"
    python -c "import psycopg2; print('  ✓ psycopg2 installed')"
} catch {
    Write-Host "  ✗ Error verifying packages" -ForegroundColor Red
    exit 1
}

# Check required files
Write-Host ""
Write-Host "📁 Checking required files..." -ForegroundColor Yellow

$requiredFiles = @(
    "run.py",
    "requirements.txt",
    "gunicorn_config.py",
    "render.yaml",
    "Procfile",
    "runtime.txt",
    "DEPLOYMENT.md"
)

$allFilesExist = $true
foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "  ✓ $file" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $file missing!" -ForegroundColor Red
        $allFilesExist = $false
    }
}

# Check .env file (for local development)
Write-Host ""
Write-Host "🔧 Environment Configuration:" -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "  ✓ .env file found (for local development)" -ForegroundColor Green
    Write-Host "  ⚠️  Remember: Set environment variables in Render dashboard for production" -ForegroundColor Yellow
} else {
    Write-Host "  ⚠️  .env file not found (create one for local development)" -ForegroundColor Yellow
}

# Check git status
Write-Host ""
Write-Host "📊 Git Status:" -ForegroundColor Yellow
try {
    git status --short
} catch {
    Write-Host "  Not a git repository or git not installed" -ForegroundColor Yellow
}

# Summary
Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
if ($allFilesExist) {
    Write-Host "✅ Build verification completed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "  1. git add ." -ForegroundColor White
    Write-Host "  2. git commit -m 'Prepare for Render deployment'" -ForegroundColor White
    Write-Host "  3. git push origin master" -ForegroundColor White
    Write-Host "  4. Deploy on Render dashboard" -ForegroundColor White
} else {
    Write-Host "⚠️  Some required files are missing!" -ForegroundColor Red
    Write-Host "Please create missing files before deploying." -ForegroundColor Yellow
}
Write-Host "==================================================" -ForegroundColor Cyan
