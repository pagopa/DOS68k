# Authentication service

## Overview

This service provides authentication and authorization functionality using an adaptive authentication layer that supports multiple JWT providers (AWS Cognito, Keycloak, or local development mode).

## Prerequisites

In order to work locally with this service you need the following softwares:

- **uv** - Python package manager
- **docker** - For containerization

## Installation

Install dependencies using uv:

```bash
uv sync
```

## Test

Run unit tests with coverage:

```bash
uv run pytest --cov=src --cov-report=term-missing
```

Always make sure your coverage % is as close to 100% as possible.

## Start service

### Standalone mode

If you want to independently start this service, run the following commands:

```bash
cd .. # Make sure to be at the root level of the repo
docker compose up -d --build auth
```

Now you can access the service OpenAPI specification at `http://localhost:3000`.

### Development mode

For local development without Docker:

```bash
# Set AUTH_PROVIDER=local in your .env file
uv run fastapi dev src/main.py
```

The service will be available at `http://localhost:8000`.

## Configuration

Configure the authentication provider by setting the `AUTH_PROVIDER` environment variable. See [README.AUTH_PROVIDERS.md](README.AUTH_PROVIDERS.md) for detailed configuration options.

## API Endpoints

- **GET /health** - Health check endpoint
- **GET /protected/jwt-check** - JWT token verification endpoint
- **GET /** - OpenAPI documentation (Swagger UI)
