# Ragna Civis API

The backend is a Django 6.1 application backed by PostgreSQL in local Docker Compose development.

## Prerequisites

- Docker with Docker Compose
- Python 3.13 and Poetry for running backend checks outside Docker

## Run with Docker Compose

From the repository root:

```bash
cp api/.env.example api/.env
docker compose up --build
```

The API runs at `http://localhost:8000`; `GET /health/` returns the health response. Apply schema migrations in a second terminal after the services are running:

```bash
docker compose exec api python manage.py migrate
```

`CORS_ALLOWED_ORIGINS` controls browser origins permitted to call the API. The Compose development default permits the web application at `http://localhost:3000`; configure production origins explicitly.

Compose serves the backend with Uvicorn through `config.asgi:application`; the Civic Assistant streaming endpoint depends on this ASGI runtime. Use the existing Compose command rather than starting a second local server.

`OPENAI_API_KEY` and `OPENAI_MODEL` are required backend configuration. Django raises an `ImproperlyConfigured` error during startup when either variable is missing or blank.

The Civic Assistant timeout and completion-token settings are optional; if omitted or blank, Django logs a warning and uses the defaults in the settings module.

Stop the local stack with `docker compose down`. PostgreSQL data is stored in the named `ragna-postgres-data` volume.

## Backend checks

From `api/`:

```bash
poetry install
poetry check --lock
poetry run ruff check .
poetry run ruff format --check .
poetry run mypy .
poetry run pytest
poetry run python manage.py check --settings=config.settings.test
poetry run python manage.py makemigrations --check --dry-run --settings=config.settings.test
```

The local environment file is intentionally untracked. Start from [`.env.example`](.env.example) and keep real credentials out of Git.
