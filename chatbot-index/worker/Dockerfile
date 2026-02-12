FROM python:3.13-slim@sha256:3de9a8d7aedbb7984dc18f2dff178a7850f16c1ae7c34ba9d7ecc23d0755e35f AS builder
WORKDIR /app/worker

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest@sha256:94a23af2d50e97b87b522d3cea24aaf8a1faedec1344c952767434f69585cbf9 /uv /uvx /bin/
COPY ./chatbot-index/worker .
COPY ./dos-utility ../../dos-utility
RUN uv sync   # crea .venv

FROM python:3.13-slim@sha256:3de9a8d7aedbb7984dc18f2dff178a7850f16c1ae7c34ba9d7ecc23d0755e35f AS runner
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