"""
Base settings for the SecureScan project.

This file contains configuration shared by EVERY environment (development,
production, testing). Environment-specific overrides live in:
    - dev.py   (local development)
    - prod.py  (production)

Nothing environment-specific (DEBUG, ALLOWED_HOSTS, database credentials,
security headers, etc.) should live here — see the sibling files instead.
"""

from pathlib import Path
from datetime import timedelta

import environ

# Points to the project root: .../securescan/  (three levels up from this file:
# settings/base.py -> settings/ -> config/ -> project root)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# `env` is imported (via `from .base import *`) by dev.py and prod.py, so
# they can each read their own environment variables with env.list()/env.db()
# without re-initializing django-environ themselves.
env = environ.Env()

# Load the .env file from the project root, if present. In real deployments
# (e.g. Docker, a hosting platform) environment variables are typically
# injected directly by the platform and no .env file exists on disk — that's
# fine, read_env() silently does nothing if the file is missing.
environ.Env.read_env(BASE_DIR / '.env')


# ---------------------------------------------------------------------------
# Security
# ---------------------------------------------------------------------------
# No default is provided on purpose: if SECRET_KEY is missing from the
# environment, Django should fail loudly at startup rather than silently
# falling back to an insecure, guessable value.
SECRET_KEY = env('SECRET_KEY')


# ---------------------------------------------------------------------------
# Application definition
# ---------------------------------------------------------------------------
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    # Enables persisting blacklisted refresh tokens in the DB — required
    # for real logout (see accounts/views.py LogoutView) and for token
    # rotation to actually invalidate the token being rotated away from.
    'rest_framework_simplejwt.token_blacklist',
]

LOCAL_APPS = [
    'apps.core',
    'apps.common',
    'apps.accounts',
    'apps.scanner',
    'apps.reports',
    'apps.dashboard',
    'apps.notifications',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'


# ---------------------------------------------------------------------------
# Password validation
# ---------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ---------------------------------------------------------------------------
# Internationalization
# ---------------------------------------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# ---------------------------------------------------------------------------
# Custom user model
# ---------------------------------------------------------------------------
# Must be set before the FIRST migrate ever run against a given database —
# changing it afterwards requires resetting the database, since other
# apps' tables (e.g. admin's LogEntry) have foreign keys pointing at
# whichever model this names.
AUTH_USER_MODEL = 'accounts.User'


# ---------------------------------------------------------------------------
# Static & media files
# ---------------------------------------------------------------------------
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Used by User.avatar (ImageField). Served via config/urls.py in dev only;
# production serves media through a real storage backend/CDN — deferred
# until a later phase actually needs file uploads at scale.
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'


# ---------------------------------------------------------------------------
# Default primary key field type
# ---------------------------------------------------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ---------------------------------------------------------------------------
# Django REST Framework
# ---------------------------------------------------------------------------
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    # Deny-by-default: every view requires authentication unless it
    # explicitly opts out with permission_classes = [AllowAny] (register,
    # login, refresh do this). Safer default than the reverse — a
    # forgotten permission_classes on a new view fails closed, not open.
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

SIMPLE_JWT = {
    # Short-lived access token limits the damage window if one leaks;
    # the longer-lived refresh token is what gets blacklisted on logout.
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    # Every refresh issues a brand-new refresh token AND blacklists the
    # old one — so a stolen refresh token becomes useless the moment the
    # legitimate client refreshes again.
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
}
