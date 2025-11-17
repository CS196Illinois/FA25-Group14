#!/bin/bash
# Build script for Render deployment
# This script is automatically run by Render during deployment

echo "=================================================="
echo "🚀 Course Compass - Build Script"
echo "=================================================="

# Display Python version
echo ""
echo "📍 Python Version:"
python --version

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip install --no-cache-dir -r requirements.txt

# Verify critical packages
echo ""
echo "✅ Verifying installations..."
python -c "import flask; print('Flask:', flask.__version__)"
python -c "import supabase; print('Supabase: installed')"
python -c "import gunicorn; print('Gunicorn: installed')"
python -c "import psycopg2; print('psycopg2: installed')"

# Check environment variables
echo ""
echo "🔧 Environment Configuration:"
if [ -n "$FLASK_ENV" ]; then
    echo "  ✓ FLASK_ENV: $FLASK_ENV"
else
    echo "  ⚠️  FLASK_ENV not set"
fi

if [ -n "$SUPABASE_URL" ]; then
    echo "  ✓ SUPABASE_URL: configured"
else
    echo "  ⚠️  SUPABASE_URL not set"
fi

if [ -n "$DATABASE_URL" ]; then
    echo "  ✓ DATABASE_URL: configured"
else
    echo "  ⚠️  DATABASE_URL not set"
fi

if [ -n "$SECRET_KEY" ]; then
    echo "  ✓ SECRET_KEY: configured"
else
    echo "  ⚠️  SECRET_KEY not set"
fi

echo ""
echo "=================================================="
echo "✅ Build completed successfully!"
echo "=================================================="
