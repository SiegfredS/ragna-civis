# Ragna Civis Web

The Ragna Civis web application is a React 19 and TypeScript single-page application built with Vite, Tailwind CSS, and TanStack Router.

## Configuration

Copy the environment example before starting the application:

```bash
cp .env.example .env
```

`VITE_API_BASE_URL` is the browser-visible base URL for the Django API. Its local development default is `http://localhost:8000`. Do not store secrets in `VITE_` variables.

## Run with Docker Compose

From the repository root:

```bash
cp web/.env.example web/.env
docker compose up --build web
```

The application is served at `http://localhost:3000`.

## Run without Docker

Use pnpm 10.4.1 and Node 22:

```bash
pnpm install --frozen-lockfile
pnpm dev
```

## Validation

```bash
pnpm lint
pnpm format:check
pnpm build
```

## Refresh dependencies in Docker

Docker Compose mounts a named `web_node_modules` volume over `/app/node_modules`. If a dependency was added or updated, refresh that volume from the current lockfile:

```bash
docker compose exec web pnpm install --frozen-lockfile
docker compose restart web
```

A rebuild by itself does not update an existing named dependency volume.
