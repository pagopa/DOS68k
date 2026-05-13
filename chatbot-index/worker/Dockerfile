FROM python:3.13-slim@sha256:dc1546eefcbe8caaa1f004f16ab76b204b5e1dbd58ff81b899f21cd40541232f AS builder
WORKDIR /app/worker

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest@sha256:1025398289b62de8269e70c45b91ffa37c373f38118d7da036fb8bb8efc85d97 /uv /uvx /bin/
COPY ./chatbot-index/worker .
COPY ./dos-utility ../../dos-utility
RUN uv sync   # crea .venv

FROM python:3.13-slim@sha256:dc1546eefcbe8caaa1f004f16ab76b204b5e1dbd58ff81b899f21cd40541232f AS runner
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