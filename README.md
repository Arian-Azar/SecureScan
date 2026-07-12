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
- ✅ Milestone 1.1 — Environment & Project Bootstrap
- 🔜 Milestone 1.2 — Custom User Model

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

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd securescan
   ```

2. **Create your local environment file**
   ```bash
   cp .env.example .env
   ```
   Generate a real `SECRET_KEY` and paste it into `.env` (replacing
   `change-me`):
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```
   Leave `DATABASE_URL` as-is — `HOST=db` only resolves inside the
   docker-compose network (see the comments in `.env.example` for why).

3. **Build and start the stack**
   ```bash
   docker-compose up --build
   ```
   This starts two services:
   - `db` — PostgreSQL 16
   - `web` — Django dev server on http://localhost:8000

4. **Run migrations** (in a second terminal, while `docker-compose up` is
   running in the first)
   ```bash
   docker-compose exec web python manage.py migrate
   ```

5. **Create an admin user**
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```
   Then log in at http://localhost:8000/admin/

### Day-to-day workflow

- Start everything: `docker-compose up`
- Run any management command: `docker-compose exec web python manage.py <command>`
- Stop everything: `Ctrl+C`, then `docker-compose down` (add `-v` only if
  you intentionally want to wipe the database)
- Source code changes on your machine hot-reload automatically inside the
  `web` container — no rebuild needed unless `requirements/*.txt` changes,
  in which case run `docker-compose up --build` again.


## Tech Stack

Django · Django REST Framework · PostgreSQL · Redis · Celery · JWT · Docker
