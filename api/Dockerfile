FROM python:3.13-slim

# Prevent Python from writing .pyc files and buffer logs.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

WORKDIR /app

# Required for psycopg2 and other packages that may need compilation.
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install poetry separately from app deps
RUN pip install --no-cache-dir poetry


# Copy dependencies
COPY pyproject.toml poetry.lock ./

# install poetry
RUN poetry install --no-root

# Run the application as a non-root user.
RUN useradd --create-home --shell /bin/bash ragna

# copy app
COPY --chown=ragna:ragna . .

USER ragna

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
