import os
import environ
from pathlib import Path

env = environ.Env(DEBUG=(bool, False))
BASE_DIR = Path(__file__).resolve().parent.parent
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')

# Set your subdomain for the camp dashboard
ALLOWED_HOSTS = ['mission_control.247-data.com', '127.0.0.1', 'localhost']
CSRF_TRUSTED_ORIGINS = ['https://mission_control.247-data.com']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'eclipse_mission_control', # Make sure this matches your app name
]

# Database pointing to the SSH Tunnel on your AWS Node
DATABASES = {
    'default': env.db(),
}

# Ensure the app knows it's behind a proxy on port 8001
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'