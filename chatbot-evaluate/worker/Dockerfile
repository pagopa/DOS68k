FROM python:3.13-slim@sha256:a0779d7c12fc20be6ec6b4ddc901a4fd7657b8a6bc9def9d3fde89ed5efe0a3d AS builder
WORKDIR /app/worker

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest@sha256:3b7b60a81d3c57ef471703e5c83fd4aaa33abcd403596fb22ab07db85ae91347 /uv /uvx /bin/
COPY ./chatbot-evaluate/worker .
COPY ./dos-utility ../../dos-utility
RUN uv sync

FROM python:3.13-slim@sha256:a0779d7c12fc20be6ec6b4ddc901a4fd7657b8a6bc9def9d3fde89ed5efe0a3d AS runner
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