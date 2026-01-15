FROM python:3.13-slim AS builder
WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY . /app
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
COPY --from=builder --chown=appuser:appuser /app/app app
COPY --from=builder --chown=appuser:appuser /app/main.py .
COPY --from=builder --chown=appuser:appuser /app/.venv .venv

USER appuser

# Niente "source" e usa la exec form
CMD ["python", "main.py"]