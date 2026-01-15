ARG PYTHON_VERSION=3.13-slim
FROM python:${PYTHON_VERSION} AS builder

WORKDIR /app

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
# Copy the application into the container
COPY ./chatbot-evaluate/api .

# Install the application dependencies
RUN uv sync --no-cache


FROM python:${PYTHON_VERSION}

WORKDIR /app

# Create a non-root user to run the application
RUN useradd -m fastapi \
    && chown -R fastapi:fastapi /app

# Change ownership of the application files to the non-root user
# Switch to the non-root user
USER fastapi

# Copy the application into the container
COPY --from=builder /app/.venv .venv
COPY ./chatbot-evaluate/api/src ./src
COPY ./chatbot-evaluate/api/README.md .

EXPOSE 8000

# Run the application.
CMD .venv/bin/fastapi run src/main.py --port 8000 --host 0.0.0.0