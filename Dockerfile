FROM python:3.10-buster as builder

RUN pip install poetry==1.4.2

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY . .

RUN poetry install --without dev && \
    rm -rf $POETRY_CACHE_DIR

# L'image d'exécution utilisée pour exécuter le code dans son environnement virtuel.
FROM python:3.10-slim-buster as runtime

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

# COPY Dockerfile et docker-compose.yaml
COPY Dockerfile docker-compose.yaml /app/

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY --from=builder /app/yimba_api /app/yimba_api

WORKDIR /app
