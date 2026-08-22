# ragna-civis

An open-source civic-tech project built in the hopes of doing something useful while learning, experimenting, and fighting boredom.

The repository is in its foundation stage. It currently contains a Django backend in [`api/`](api/README.md); a frontend application has not been added yet.

## Run the backend

```bash
cp api/.env.example api/.env
docker compose up --build
```

The backend is available at `http://localhost:8000`, with a health endpoint at `http://localhost:8000/health/`.

For migrations, tests, and local development details, see the [backend README](api/README.md).
