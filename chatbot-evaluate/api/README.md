# Chatbot Evaluate API

## Prerequisites

In order to work locally with this service you need the following softwares:

- uv
- docker

## Test

The following script to run unit tests. Always make sure your coverage % is as close to 100% as possible.

```bash
uv run pytest --cov=src --cov-report=term-missing
```

## Env config

This service uses a queue to send messages to a worker. In order to use it correctly you have to set an `.env` file with the correct queue configuration. Follow instructions [here](../../dos-utility/docs/features.md#2-queue-interface).

## Start service

If you want to independently start this service, run the following commands.

```bash
cd .. # Make sure to be at the repo root level
docker compose up -d --build chatbot-evaluate-api
```

Now you can access the service OpenAPI specification at `http://localhost:8002`.