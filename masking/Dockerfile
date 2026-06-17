ARG PYTHON_VERSION=3.13-slim@sha256:dc1546eefcbe8caaa1f004f16ab76b204b5e1dbd58ff81b899f21cd40541232f
FROM python:${PYTHON_VERSION} AS builder

WORKDIR /app

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest@sha256:1025398289b62de8269e70c45b91ffa37c373f38118d7da036fb8bb8efc85d97 /uv /uvx /bin/
# Copy the application into the container
COPY ./masking .
COPY ./dos-utility ../dos-utility

# Install the application dependencies
RUN uv sync --no-cache


FROM python:${PYTHON_VERSION}

WORKDIR /app

COPY --from=builder /app/.venv .venv

# Create a non-root user to run the application
# Change ownership of the application files to the non-root user
RUN useradd -m fastapi \
    && chown -R fastapi:fastapi /app \
    && chown -R fastapi:fastapi /app/.venv/lib/python3.13/site-packages/

# Switch to the non-root user
USER fastapi

# Copy the application into the container
COPY ./masking/src ./src
COPY ./masking/README.md .
COPY ./masking/config ./config

EXPOSE 3000

# Run the application.
CMD .venv/bin/fastapi run src/main.py --port 3000 --host 0.0.0.0