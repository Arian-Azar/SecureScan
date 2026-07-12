"""
Development settings.

Activated via: DJANGO_SETTINGS_MODULE=config.settings.dev

Priorities here are DX (developer experience) and fast feedback — not
security hardening. Nothing in this file should ever be used in production.
"""

from .base import *  # noqa: F401,F403

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# NOTE: SQLite is a temporary placeholder so `manage.py check` / `runserver`
# work right now. It will be replaced by PostgreSQL (via django-environ +
# DATABASE_URL) in Task 3, and wired to the Dockerized Postgres service in
# Task 4.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Emails are printed to the console instead of actually being sent —
# convenient for testing registration/password-reset flows locally.
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
