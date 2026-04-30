ARG PYTHON_VERSION=3.13-slim@sha256:a0779d7c12fc20be6ec6b4ddc901a4fd7657b8a6bc9def9d3fde89ed5efe0a3d
FROM python:${PYTHON_VERSION} AS builder

WORKDIR /app/chatbot-index

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest@sha256:3b7b60a81d3c57ef471703e5c83fd4aaa33abcd403596fb22ab07db85ae91347 /uv /uvx /bin/
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