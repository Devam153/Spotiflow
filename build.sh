#!/usr/bin/env bash
# exit on error
set -o errexit

# Debug - print current directory
echo "Current directory: $(pwd)"

# Install dependencies
pip install -r requirements.txt

# Navigate to the Spotiflow directory where manage.py is located
cd Spotiflow

# Debug - print current directory after cd
echo "Changed to directory: $(pwd)"

# Make sure the Spotiflow directory is in the Python path
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Debug - print PYTHONPATH
echo "PYTHONPATH: $PYTHONPATH"

# Debug - list files in current directory
echo "Files in current directory:"
ls -la

# Debug - check if spotiflow module exists
echo "Checking for spotiflow module:"
find . -name "*.py" | grep -i spotiflow

# Run Django commands
python manage.py collectstatic --no-input
python manage.py migrate
