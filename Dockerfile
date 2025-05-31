FROM python:3.12@sha256:45d13f5cba9b0f9bdfaed658d3e4fcfb1694ce49a6d70ec07c9f3980a7dc8b26 as service

RUN pip install poetry==1.6.1

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN poetry install --without dev --no-root

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"
COPY src .
