FROM python:3.14@sha256:5ada2b3e9586c924a8c81d6a35e6016f4fc261429dbd7e5c6ae724431003dcee as service

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
