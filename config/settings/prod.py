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

# No defaults here, unlike dev.py: in production, a missing environment
# variable should crash the app at startup, not silently fall back to
# something insecure or wrong.
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

DATABASES = {
    'default': env.db('DATABASE_URL')
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
