"""
Development settings.

Activated via: DJANGO_SETTINGS_MODULE=config.settings.dev

Priorities here are DX (developer experience) and fast feedback — not
security hardening. Nothing in this file should ever be used in production.
"""

from .base import *  # noqa: F401,F403

DEBUG = True

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])

# `env.db()` parses a DATABASE_URL like postgres://user:pass@host:port/name
# into Django's DATABASES dict. If DATABASE_URL is unset (e.g. you haven't
# started the Postgres container yet), we fall back to SQLite so you can
# still run `manage.py runserver` and `manage.py check` right away — this
# fallback disappears once Task 4's Docker Compose is running.
DATABASES = {
    'default': env.db('DATABASE_URL', default=f'sqlite:///{BASE_DIR / "db.sqlite3"}')
}

# Emails are printed to the console instead of actually being sent —
# convenient for testing registration/password-reset flows locally.
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
