#!/usr/bin/env bash

# Exit on error
set -o errexit

# Debugging information
echo "Starting build process..."
echo "Python version:"
python --version
echo "Environment variables:"
echo "RENDER: $RENDER"
echo "RENDER_EXTERNAL_URL: $RENDER_EXTERNAL_URL"

# Check for Spotify configuration
echo "Checking Spotify configuration..."
if [ -n "$SPOTIFY_CLIENT_ID" ]; then
    echo "SPOTIFY_CLIENT_ID is set"
else
    echo "WARNING: SPOTIFY_CLIENT_ID is not set"
fi

if [ -n "$SPOTIFY_CLIENT_SECRET" ]; then
    echo "SPOTIFY_CLIENT_SECRET is set"
else
    echo "WARNING: SPOTIFY_CLIENT_SECRET is not set"
fi

# Create virtual environment
echo "Creating virtual environment..."
python -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Debug - List system paths and packages
echo "Current directory: $(pwd)"
echo "Python path: $PYTHONPATH"
echo "Files in current directory:"
ls -la

echo "Checking for spotiflow module:"
find . -name "*.py" | grep -E "spotiflow"

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --no-input

# Run migrations
echo "Running migrations..."
python manage.py migrate

echo "Build completed successfully!"
