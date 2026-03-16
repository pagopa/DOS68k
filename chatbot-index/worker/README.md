# Chatbot Index worker

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

This service uses a queue to read messages to process. In order to use it correctly you have to set an `.env` file with the correct queue configuration. Follow instructions [here](../../dos-utility/docs/features.md#2-queue-interface).