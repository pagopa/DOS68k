ARG PYTHON_VERSION=3.14-slim@sha256:5b3879b6f3cb77e712644d50262d05a7c146b7312d784a18eff7ff5462e77033
FROM python:${PYTHON_VERSION} AS builder

WORKDIR /app

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest@sha256:3b7b60a81d3c57ef471703e5c83fd4aaa33abcd403596fb22ab07db85ae91347 /uv /uvx /bin/

# Force uv to use the system Python so .venv/bin/python symlinks remain valid
# in the final stage (uv's managed Python cache is not copied over)
ENV UV_PYTHON_PREFERENCE=only-system

# Copy the application into the container
COPY ./chatbot-api .
COPY ./dos-utility ../dos-utility

# Force uv to use the system Python so the venv symlinks remain valid in the final stage
ENV UV_PYTHON_PREFERENCE=only-system

# Install the application dependencies
RUN rm -f uv.lock && uv sync --no-cache
FROM python:${PYTHON_VERSION}

WORKDIR /app

# Create a non-root user to run the application
RUN useradd -m fastapi \
    && chown -R fastapi:fastapi /app

# Change ownership of the application files to the non-root user
# Switch to the non-root user
USER fastapi

# Copy the application into the container
COPY --from=builder --chown=fastapi:fastapi /app/.venv .venv
COPY --chown=fastapi:fastapi ./chatbot-api/src ./src
COPY --chown=fastapi:fastapi ./chatbot-api/README.md .

EXPOSE 8000

# Run the application.
CMD ["/app/.venv/bin/python", "-m", "fastapi", "run", "src/main.py", "--port", "8000", "--host", "0.0.0.0"]