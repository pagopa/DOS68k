# Chatbot API

## Overview

The chatbot-api service is responsible for generating answers to user questions through an LLM. Each user can create new sessions (chats) and start chatting with the chatbot. Each session can be either temporary or not. If temporary, all queries (messages) within that session will have an expiration date that matches the one of the session.

> ⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️ <br>
> If you choose to use DynamoDB as database, temporary session will be automatically deleted after the expiration date. If you choose any other db that doesn't have this feature, you have to manually set a job to delete expired chats. See the [env](#env-config) section for more details.

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

The OpenAPI docs are available at `http://localhost:8000`.

## Post-start activities

This service requires two DynamoDB tables to operate: `sessions` and `queries`.

When running via Docker Compose (the default setup), LocalStack is started as a dependency and the tables are created automatically by an init script — no manual action is needed.

If you are using an external DynamoDB (real AWS or another local emulator), you must create the tables yourself before the service can store or retrieve data:

- `sessions` — partition key: `userId` (S), sort key: `id` (S), TTL attribute: `expiresAt`
- `queries` — partition key: `sessionId` (S), sort key: `id` (S), TTL attribute: `expiresAt`

To verify the database connection is healthy after starting, call:

```
GET http://localhost:8000/health/db
```

---

## API Documentation

All endpoints require the header:

```
X-User-Id: <uuid>
```

### Health

- `GET /health` — Service status
	- Response: `{ "status": "ok", "service": "Chatbot API" }`
- `GET /health/db` — Database connectivity
	- Response: `{ "status": "ok", "service": "Chatbot API", "database": "connected" }`

### Sessions

- `GET /sessions/all` — List all sessions for the user
	- Response: `[{ ...session fields... }]`
- `GET /sessions/{session_id}` — Get a session by ID
	- Response: `{ ...session fields... }`
- `POST /sessions` — Create a new session
	- Request body:
		```json
		{
			"title": "My chat",
			"isTemporary": false
		}
		```
	- Response: `{ ...session fields... }`
- `DELETE /sessions/{session_id}` — Delete a session
	- Response: `204 No Content`

**Session fields:**
```json
{
	"id": "<uuid>",
	"userId": "<uuid>",
	"title": "string",
	"createdAt": "YYYY-MM-DDTHH:MM:SS",
	"expiresAt": "YYYY-MM-DDTHH:MM:SS" | null
}
```

### Queries

- `GET /queries/{session_id}` — List all queries for a session
	- Response: `[{ ...query fields... }]`
- `POST /queries/{session_id}` — Create a new query (send a question)
	- Request body:
		```json
		{
			"question": "What is the capital of Italy?"
		}
		```
	- Response: `{ ...query fields... }`

**Query fields:**
```json
{
	"id": "<uuid>",
	"sessionId": "<uuid>",
	"question": "string",
	"answer": "string",
	"badAnswer": false,
	"topic": ["string"],
	"createdAt": "YYYY-MM-DDTHH:MM:SS",
	"expiresAt": "YYYY-MM-DDTHH:MM:SS" | null
}
```

---

For more details, see the OpenAPI docs at `/` when the service is running.