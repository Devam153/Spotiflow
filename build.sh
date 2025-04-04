
#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Navigate to the Spotiflow directory where manage.py is located
cd Spotiflow

# Make sure the current directory is in the Python path
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Run Django commands
python manage.py collectstatic --no-input
python manage.py migrate
