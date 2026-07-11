# SecureScan

**Web Security Assessment & Vulnerability Insight Platform**

SecureScan is a Django + Django REST Framework platform that performs
preliminary security analysis of websites (SSL/TLS, HTTP security headers,
cookies, CORS, DNS records, technology fingerprinting, and more) and — unlike
a plain scanner — teaches the user how to fix every issue it finds.

> This project is being built incrementally, phase by phase, as a learning
> exercise in professional Django/DRF backend engineering. See `docs/` (added
> in later phases) for architecture notes and the development roadmap.

## Status

🚧 **Phase 1 — Infrastructure & Auth** (in progress)

## Project Layout

```
config/             # Django project configuration (settings, urls, wsgi/asgi)
  settings/
    base.py          # settings shared by all environments
    dev.py           # development overrides
    prod.py          # production overrides
apps/
  core/              # domain-shared building blocks (abstract models, etc.)
  common/            # generic, domain-agnostic utilities
  accounts/          # custom user, profile, authentication
  scanner/           # the scanning engine (heart of the project)
  reports/           # PDF / Excel report generation
  dashboard/         # user-facing dashboard & analytics
  notifications/     # email / status-change notifications
requirements/        # split pip requirements (base/dev/prod)
docker/              # Dockerfiles and related configuration
```

## Requirements

- Python 3.12+
- PostgreSQL 15+
- Docker & Docker Compose (recommended for local development)

## Local Setup

_Instructions will be added at the end of Milestone 1.1 once the environment
is fully configured._

## Tech Stack

Django · Django REST Framework · PostgreSQL · Redis · Celery · JWT · Docker
