FROM python:3.14@sha256:97aa8cc0b87a4a312a294d2d4d7b20f6e2a21ed6d4e64ef08c03088c4aa9890f as service

RUN pip install poetry==2.2.1

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN poetry install --without dev --no-root

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"
COPY src .
