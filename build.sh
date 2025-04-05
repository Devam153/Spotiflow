#!/usr/bin/env bash

# Exit on error
set -o errexit

# Debugging information
echo "Starting build process..."
echo "Python version:"
python --version

# Install system dependencies
echo "Installing system dependencies..."
apt-get update
# Install Tesseract OCR with all language data
apt-get install -y tesseract-ocr tesseract-ocr-all

# Verify Tesseract installation
echo "Verifying Tesseract installation..."
tesseract --version
which tesseract
echo "Tesseract data path:"
echo $(tesseract --list-langs)

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
