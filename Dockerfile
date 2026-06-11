FROM python:3.14@sha256:4b45aa26a4ac4c9e0d63c8a9b72c48ea815d8feac9f2dd89d6faf650f64f7500 as service

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
