# Chatbot Evaluate API

## Prerequisites

In order to work locally with this service you need the following softwares:

- uv
- docker
- [task](https://taskfile.dev/)

## Test

Run unit tests with coverage report, no threshold enforced:

```bash
task test:quick
```

Run unit tests enforcing a minimum coverage threshold (default: 80%):

```bash
task test
```

To override the minimum coverage threshold:

```bash
task test COV_THREASHOLD=90
```

## Env config

This service uses a queue to send messages to a worker. In order to use it correctly you have to set an `.env` file with the correct queue configuration. Follow instructions [here](../../dos-utility/docs/features.md#3-queue-interface).

## Start service

If you want to independently start this service, run the following commands.

```bash
cd .. # Make sure to be at the repo root level
docker compose up -d --build chatbot-evaluate-api
```

Now you can access the service OpenAPI specification at `http://localhost:8002`.