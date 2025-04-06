
from pathlib import Path
import os
from dotenv import load_dotenv
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    'spotiflow.onrender.com',
    '127.0.0.1',
    'localhost',
]

RENDER_EXTERNAL_URL = os.environ.get('RENDER_EXTERNAL_URL')
if RENDER_EXTERNAL_URL:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_URL)
    logger.info(f"Added Render URL to allowed hosts: {RENDER_EXTERNAL_URL}")

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'spotify_app.apps.SpotifyAppConfig',
    'whitenoise.runserver_nostatic',  # Ensure Django uses WhiteNoise in dev & prod
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # WhiteNoise for static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'spotiflow.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'spotiflow.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Tesseract Configuration (Production & Local)
TESSERACT_CMD_PATH = os.getenv("TESSERACT_CMD_PATH", "/usr/bin/tesseract")

# Spotify Configuration
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

# Fix the redirect URI for both local and production environments
if RENDER_EXTERNAL_URL:
    # We're on Render.com - use the RENDER_EXTERNAL_URL
    SPOTIFY_REDIRECT_URI = f"{RENDER_EXTERNAL_URL}/spotify_app/callback/"
    logger.info(f"Using Render URL for Spotify redirect: {SPOTIFY_REDIRECT_URI}")
else:
    # We're in local development - use 127.0.0.1
    SPOTIFY_REDIRECT_URI = "http://127.0.0.1:8000/spotify_app/callback/"
    logger.info(f"Using local URL for Spotify redirect: {SPOTIFY_REDIRECT_URI}")

# Set the correct scope
SPOTIFY_SCOPE = "playlist-modify-public user-library-modify playlist-read-private"

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']  # Ensure local static files work
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files (Uploaded files)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'