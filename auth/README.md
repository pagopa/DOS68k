# Chatbot API

## Prerequisites

In order to interact locally with this service you need the following softwares:

- uv
- docker

## Test

The following script to run unit tests. Always make sure your coverage % is as close to 100% as possible.

```bash
uv run pytest --cov
```

## Start service

If you want to independently start this service, run the following commands.

```bash
docker build -t chatbot-api-service . # To build the docker image
docker run --rm -p 3000:3000 chatbot-api-service # To run the service and expose it on the port 3000
```

Now you can access the service docs at `http://localhost:3000`.