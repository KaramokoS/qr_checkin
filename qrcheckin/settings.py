import os
import dj_database_url
from decouple import config


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# SECRET_KEY = 'dummy-secret-key'
SECRET_KEY = config("SECRET_KEY", default="unsafe-secret-key")

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
HEROKU_APP = config("HEROKU_APP", default=None)
if HEROKU_APP:
    ALLOWED_HOSTS.append(f"{HEROKU_APP}.herokuapp.com")

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'checkin',
    'channels',
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
ROOT_URLCONF = 'qrcheckin.urls'
TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [],
    'APP_DIRS': True,
    'OPTIONS': {'context_processors': [
        'django.template.context_processors.debug',
        'django.template.context_processors.request',
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
    ],},
}]
WSGI_APPLICATION = 'qrcheckin.wsgi.application'
DATABASES = {
    "default": dj_database_url.config(default=config("DATABASE_URL", default="sqlite:///db.sqlite3"))
}

STATIC_URL = '/static/'

TIME_ZONE = 'Africa/Bamako'
USE_TZ = True

ASGI_APPLICATION = 'qrcheckin.asgi.application'

# Channel layers (dev: InMemory)
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
