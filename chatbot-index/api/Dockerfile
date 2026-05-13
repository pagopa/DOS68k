ARG PYTHON_VERSION=3.13-slim@sha256:dc1546eefcbe8caaa1f004f16ab76b204b5e1dbd58ff81b899f21cd40541232f
FROM python:${PYTHON_VERSION} AS builder

WORKDIR /app/chatbot-index

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest@sha256:1025398289b62de8269e70c45b91ffa37c373f38118d7da036fb8bb8efc85d97 /uv /uvx /bin/
# Copy the application into the container
COPY ./chatbot-index/api .
# It must be 2 levels up to match the import paths in the pyproject.toml
COPY ./dos-utility ../../dos-utility

# Install the application dependencies
RUN uv sync --no-cache


FROM python:${PYTHON_VERSION}

WORKDIR /app/chatbot-index

# Create a non-root user to run the application
RUN useradd -m fastapi \
    && chown -R fastapi:fastapi /app/chatbot-index

# Change ownership of the application files to the non-root user
# Switch to the non-root user
USER fastapi

# Copy the application into the container
COPY --from=builder --chown=fastapi:fastapi /app/chatbot-index/.venv .venv
COPY ./chatbot-index/api/src ./src
COPY ./chatbot-index/api/README.md .

EXPOSE 8000

# Run the application.
CMD .venv/bin/fastapi run src/main.py --port 8000 --host 0.0.0.0