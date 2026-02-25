# Chatbot API

## Overview

The chatbot-api service is responsible for generating answers to user questions through an LLM. Each user can create new sessions (chats) and start chatting with the chatbot. Each session can be either temporary or not. If temporary, all queries (messages) within that session will have an expiration date that matches the one of the session.

> !!! IMPORTANT !!! <br>
> If you choose to use DynamoDB as database, temporary session will be automatically deleted after the expiration date. If you choose any other db that doesn't have this feature, you have to manually set a job to delete expired chats. See the [env](#env-config) section for more details.

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

This service uses a NoSQL database to store users chats and queries. In order to use it correctly you have to set an `.env` file with the correct configuration. Follow below links for instructions:
- [NoSQL database](../dos-utility/docs/features.md#6-nosql-db-interface)

Once you've done that, update your .env with these:

```bash
export FRONTEND_URL=<frontend-url> # For CORS origins, with format http(s)://hostname

export SESSION_EXPIRATION_DAYS=30 # Number of days after wich the session will be automatically deleted from DynamoDB (only valid for DynamoDB)

export MASK_PII=true # Boolean. If true, the chatbot-api service will call the masking service to mask PII within user question and agent answer before storing them to the DB.
export MASKING_SERVICE_URL=<masking-url> # With format http(s)://masking-host:<port>. Only populate this variable if MASK_PII is true
```

## Start service

If you want to independently start this service, run the following commands.

```bash
cd .. # Make sure to be at the repo root level
docker compose up -d --build chatbot-api
```

Now you can access the service OpenAPI specification at `http://localhost:8000`.