# Chatbot Index API

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

This service uses a queue to send messages to a worker and a storage service. In order to use them correctly you have to set an `.env` file with the correct configuration. Follow below links for instructions:
- [queue](../../dos-utility/docs/features.md#2-queue-interface)
- [storage](../../dos-utility/docs/features.md#3-storage-interface)

## Start service

If you want to independently start this service, run the following commands.

```bash
cd .. # Make sure to be at the repo root level
docker compose up -d --build chatbot-index-api
```

Now you can access the service OpenAPI specification at `http://localhost:8003`.

## Post-start activities

This service interact with external storage. In order to make it work be sure the bucket you specified in the `.env` file exists.<br>