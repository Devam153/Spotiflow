"""
WSGI config for spotiflow project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
import sys
from pathlib import Path

# Add the project root directory to the Python path
current_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(current_path))

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spotiflow.settings')

application = get_wsgi_application()