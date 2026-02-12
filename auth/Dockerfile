ARG PYTHON_VERSION=3.13-slim@sha256:3de9a8d7aedbb7984dc18f2dff178a7850f16c1ae7c34ba9d7ecc23d0755e35f
FROM python:${PYTHON_VERSION} AS builder

WORKDIR /app

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest@sha256:94a23af2d50e97b87b522d3cea24aaf8a1faedec1344c952767434f69585cbf9 /uv /uvx /bin/
# Copy the application into the container
COPY ./auth .
COPY ./dos-utility ../dos-utility

# Install the application dependencies
RUN uv sync --no-cache


FROM python:${PYTHON_VERSION}

WORKDIR /app

# Create a non-root user to run the application
# Change ownership of the application files to the non-root user
RUN useradd -m fastapi \
    && chown -R fastapi:fastapi /app 

# Switch to the non-root user
USER fastapi

# Copy the application into the container
COPY --from=builder /app/.venv .venv
COPY ./auth/src ./src
COPY ./auth/README.md .

EXPOSE 3000

# Run the application.
CMD .venv/bin/fastapi run src/main.py --port 3000 --host 0.0.0.0