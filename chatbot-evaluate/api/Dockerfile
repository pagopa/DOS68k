ARG PYTHON_VERSION=3.13-slim@sha256:3de9a8d7aedbb7984dc18f2dff178a7850f16c1ae7c34ba9d7ecc23d0755e35f
FROM python:${PYTHON_VERSION} AS builder

WORKDIR /app/chatbot-evaluate

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest@sha256:94a23af2d50e97b87b522d3cea24aaf8a1faedec1344c952767434f69585cbf9 /uv /uvx /bin/
# Copy the application into the container
COPY ./chatbot-evaluate/api .
COPY ./dos-utility ../../dos-utility

# Install the application dependencies
RUN uv sync --no-cache


FROM python:${PYTHON_VERSION}

WORKDIR /app/chatbot-evaluate

# Create a non-root user to run the application
RUN useradd -m fastapi \
    && chown -R fastapi:fastapi /app/chatbot-evaluate

# Change ownership of the application files to the non-root user
# Switch to the non-root user
USER fastapi

# Copy the application into the container
COPY --from=builder /app/chatbot-evaluate/.venv .venv
COPY ./chatbot-evaluate/api/src ./src
COPY ./chatbot-evaluate/api/README.md .

EXPOSE 8000

# Run the application.
CMD .venv/bin/fastapi run src/main.py --port 8000 --host 0.0.0.0