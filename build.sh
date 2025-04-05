#!/usr/bin/env bash
# exit on error
set -o errexit

# Install system packages from apt.txt if available
if [ -f apt.txt ]; then
  echo "Installing apt packages from apt.txt..."
  sudo apt-get update
  # Install each package listed in apt.txt
  xargs sudo apt-get install -y < apt.txt
fi

# Debug - print current directory
echo "Current directory: $(pwd)"

# Install dependencies
pip install -r requirements.txt

# Debug - print current directory
echo "Directory after installation: $(pwd)"

# Make sure the current directory is in the Python path
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Debug - print PYTHONPATH
echo "PYTHONPATH: $PYTHONPATH"

# Debug - list files in current directory
echo "Files in current directory:"
ls -la

# Debug - check if spotiflow module exists
echo "Checking for spotiflow module:"
find . -name "*.py" | grep -i spotiflow
echo "Tesseract path: $(which tesseract)"

# Run Django commands
python manage.py collectstatic --no-input
python manage.py migrate
