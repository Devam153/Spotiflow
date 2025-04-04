"""
WSGI config for spotiflow project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the Python path
current_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(current_dir))

# Print debug info
print(f"WSGI startup - current directory: {current_dir}")
print(f"WSGI startup - Python path: {sys.path}")

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spotiflow.settings')

application = get_wsgi_application()