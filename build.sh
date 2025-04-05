#!/usr/bin/env bash

# Exit on error
set -o errexit

# Debugging information
echo "Starting build process..."
echo "Python version:"
python --version

# Note: On Render, we cannot use apt-get to install system packages during the build phase
# Instead, we'll check if we're on Render and handle OCR differently
if [ "$RENDER" = "true" ]; then
    echo "Running on Render.com - skipping system package installation"
    echo "OCR functionality will be handled via alternative methods in the application"
else
    # For local development environments where apt-get is available
    echo "Running in local environment - installing system dependencies..."
    if command -v apt-get &> /dev/null; then
        apt-get update
        apt-get install -y tesseract-ocr tesseract-ocr-all
    else
        echo "apt-get not available - skipping Tesseract installation"
        echo "Please install Tesseract OCR manually for local development"
    fi
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

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --no-input

# Run migrations
echo "Running migrations..."
python manage.py migrate

echo "Build completed successfully!"
