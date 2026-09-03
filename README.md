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
