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
