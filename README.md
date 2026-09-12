# Ragna Civis

Ragna Civis is an open-source civic-tech project for making public governance and community projects easier to follow.

The repository contains a Django REST API in [`api/`](api/README.md) and a Vite React application in [`web/`](web/README.md).

## Run locally with Docker Compose

Create local environment files from the examples, then start the stack from the repository root:

```bash
cp api/.env.example api/.env
cp web/.env.example web/.env
docker compose up --build
```

The web application is available at `http://localhost:3000` and the API is available at `http://localhost:8000`. The API health endpoint is `http://localhost:8000/health/`.

`VITE_API_BASE_URL` configures the API base URL exposed to the browser. Its development default is `http://localhost:8000`; do not place secrets in this variable.

Apply backend migrations after the services are running:

```bash
docker compose exec api python manage.py migrate
```

### Troubleshoot local Compose networking

If the API is healthy inside Docker but `http://localhost:8000/health/` is not
reachable, inspect the rendered configuration and live container state before
changing application settings:

```bash
docker compose config
docker compose ps -a
docker compose port api 8000
docker compose ls
docker network inspect ragna-civis_default
docker compose exec api getent hosts postgres
docker compose exec api cat /etc/resolv.conf
```

The API should show a publication such as `0.0.0.0:8000`, and the API and
Postgres containers should both be attached to `ragna-civis_default`. The
Compose service hostname is `postgres`; do not change the container database
URL to `localhost`.

`BACKEND_PORT` is used when Compose renders the host-port mapping. Compose
reads it from the shell or a repository-root `.env`; values in `api/.env` are
loaded into the API container and do not control host-port interpolation.

If the configuration is correct but the containers or network have stale
runtime state, recreate only the services without removing the database volume:

```bash
docker compose up -d --force-recreate api postgres web
```

Then verify the API, DNS, and Django configuration:

```bash
curl http://localhost:8000/health/
docker compose exec api getent hosts postgres
docker compose exec api python manage.py migrate
docker compose exec api python manage.py check
```

Stop the local stack with:

```bash
docker compose down
```

PostgreSQL data is retained in the named `ragna-postgres-data` volume. See the [backend README](api/README.md) and [web README](web/README.md) for application-specific development and validation commands.

## Refresh web dependencies in Docker

The Compose web service keeps `node_modules` in a named volume so the source bind mount does not replace container dependencies. After pulling a change to `web/package.json` or `web/pnpm-lock.yaml`, install the updated lockfile into that volume:

```bash
docker compose exec web pnpm install --frozen-lockfile
docker compose restart web
```

Rebuilding the image alone does not replace an existing `web_node_modules` volume.

## Install development hooks

From the repository root, install both the file checks and Conventional Commit validation:

```bash
poetry -C api run pre-commit install
poetry -C api run pre-commit install --hook-type commit-msg
```
