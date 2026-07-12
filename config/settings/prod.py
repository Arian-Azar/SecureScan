"""
Production settings.

Activated via: DJANGO_SETTINGS_MODULE=config.settings.prod

Priorities here are security and stability. Every value that differs by
deployment (hosts, database credentials, secret key) will be pulled from
environment variables once django-environ is wired in (Task 3) — for now,
placeholders mark exactly what MUST change before this ever runs for real.
"""

from .base import *  # noqa: F401,F403

DEBUG = False

# TODO (Task 3): read from env, e.g. env.list('ALLOWED_HOSTS')
ALLOWED_HOSTS = []

# TODO (Task 3): read from env via env.db(), backed by the Dockerized
# PostgreSQL service introduced in Task 4.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'CHANGE_ME',
        'USER': 'CHANGE_ME',
        'PASSWORD': 'CHANGE_ME',
        'HOST': 'CHANGE_ME',
        'PORT': '5432',
    }
}

# --- Security hardening ----------------------------------------------------
# These matter especially for a *security assessment platform* — it would be
# embarrassing to ship this project without them.
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
