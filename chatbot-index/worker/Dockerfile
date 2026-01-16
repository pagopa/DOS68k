FROM python:3.13-slim AS builder
WORKDIR /app/worker

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY ./chatbot-index/worker .
COPY ./dos-utility ../../dos-utility
RUN uv sync   # crea .venv

FROM python:3.13-slim AS runner
WORKDIR /app

# 👉 USA LA VENV DI DEFAULT PER L'IMMAGINE
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="${VIRTUAL_ENV}/bin:${PATH}"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN useradd -m appuser

# Copia tutto già con i permessi giusti
COPY --from=builder --chown=appuser:appuser /app/worker .

USER appuser

# Niente "source" e usa la exec form
CMD [".venv/bin/python", "src/worker/main.py"]