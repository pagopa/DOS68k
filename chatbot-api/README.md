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

This service uses multiple modules from the dos-utility package. In order to use it correctly you have to set an `.env` file with the correct configuration. Follow below links for instructions:

- [NoSQL database](../dos-utility/docs/features.md#6-nosql-db-interface)
- [Vector db](../dos-utility/docs/features.md#5-vector-db-interface)

Once you've done that, update your .env with these:

```bash
export FRONTEND_URL=<frontend-url> # For CORS origins, with format http(s)://hostname

export SESSIONS_TABLENAME=sessions # DynamoDB table name for sessions. Defaults to "sessions"
export QUERY_TABLENAME=queries # DynamoDB table name for queries. Defaults to "queries"

export SESSION_EXPIRATION_DAYS=30 # Number of days after wich the session will be automatically deleted from DynamoDB (only valid for DynamoDB)

export MASK_PII=true # Boolean. If true, the chatbot-api service will call the masking service to mask PII within user question and agent answer before storing them to the DB.
export MASKING_SERVICE_URL=<masking-url> # With format http(s)://masking-host:<port>. Only populate this variable if MASK_PII is true

export LOG_LEVEL=20 # Python logging level (10=DEBUG, 20=INFO, 30=WARNING, 40=ERROR, 50=CRITICAL). Defaults to 20 (INFO). Set to 10 to enable debug logs across the service, useful for tracing incoming requests, agent reasoning, tool usage, retrieved chunks and generated responses.
```

## Customization

### Custom RAG tools

The chatbot agent discovers its RAG tools at startup by reading YAML config files from a tools directory. Each YAML file registers one tool backed by a vector DB index. See [`src/modules/chatbot/tool/config/template.yaml`](./src/modules/chatbot/tool/config/template.yaml) for the full schema and field descriptions.

To provide your own tools, create one YAML file per tool and make them available to the container using **one** of the following methods:

**Option A — Docker volume mount** (recommended for local development)

Uncomment the volumes section in `compose.yaml` under the `chatbot-api` service:

```yaml
chatbot-api:
  volumes:
    - ./chatbot-api/scripts/tool_config:/app/src/modules/chatbot/tool/config
```

This mounts the local folder into the container, replacing the built-in config directory. Sample tool configs matching the [populate script](#populate-vector-db) topics are available in [`scripts/tool_config/`](./scripts/tool_config/).

**Option B — `TOOLS_CONFIG_DIR` environment variable**

Set the `TOOLS_CONFIG_DIR` env var in your `.env` file to point to a custom directory inside the container:

```bash
export TOOLS_CONFIG_DIR=/app/my-tools
```

### Custom agent configuration

The agent's identity, behavioral rules (`system_prompt`), and reasoning format (`system_header`) are defined in a YAML config file. The default config is [`src/modules/chatbot/agent/agent.yaml`](./src/modules/chatbot/agent/agent.yaml).

To override it:

**Option A — Docker volume mount**

Uncomment the agent volume line in `compose.yaml`:

```yaml
chatbot-api:
  volumes:
    - ./my-agent.yaml:/app/src/modules/chatbot/agent/agent.yaml
```

**Option B — `AGENT_CONFIG_PATH` environment variable**

Set the `AGENT_CONFIG_PATH` env var in your `.env` file:

```bash
export AGENT_CONFIG_PATH=/app/my-agent.yaml
```

The YAML file must contain the fields: `name`, `description`, `system_prompt`, and `system_header`. See the default [`agent.yaml`](./src/modules/chatbot/agent/agent.yaml) for reference.

---

## Scripts

### Populate vector DB

The script [`scripts/populate_vector_db.py`](./scripts/populate_vector_db.py) seeds the vector database with sample documents so you can test the full pipeline (vector DB &rarr; LlamaIndex &rarr; ReAct agent) without a real document ingestion flow.

**Available topics:**

| Topic | Index name | Content |
|---|---|---|
| software-dev | `software-dev` | REST APIs, Docker, FastAPI, asyncio, vector databases, RAG, Pydantic |
| zephyr-corp | `zephyr-corp` | Fictional company HR policies: onboarding, leave, remote work, expenses |
| borgonero-fc | `borgonero-fc` | Fictional football club: history, stadium, seasons, players, transfers |

**Prerequisites:**

- A running vector DB (Redis or Qdrant). Start Redis with: `docker compose up -d redis-vdb`
- Run the script from the `chatbot-api` directory so that `uv` picks up the local `.venv` and `dos-utility` dependency

**Usage:**

```bash
cd chatbot-api

# Use real Google embeddings instead of random vectors
uv run python scripts/populate_vector_db.py --provider redis --embed-provider google --google-api-key YOUR_KEY
```

**Environment variables and CLI flags:**

| Flag / Env var | Default | Description |
|---|---|---|
| `--provider` | (required) | `redis` or `qdrant` |
| `--topic` | `all` | Topic to populate (`software-dev`, `zephyr-corp`, `borgonero-fc`, or `all`) |
| `--embed-dim` | `768` | Embedding vector dimension (must match `EMBED_DIM`) |
| `--host` / `REDIS_HOST` / `QDRANT_HOST` | `localhost` | DB hostname |
| `--port` / `REDIS_PORT` / `QDRANT_PORT` | `6379` / `6333` | DB port |
| `--embed-provider` | `mock` | `mock` (random vectors) or `google` (real embeddings) |
| `--google-api-key` / `GOOGLE_API_KEY` | — | Required when `--embed-provider=google` |

After populating, mount the matching tool configs from [`scripts/tool_config/`](./scripts/tool_config/) as described in [Custom RAG tools](#custom-rag-tools).

---

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
	- Response `200`: `[{ ...session fields... }]`
- `GET /sessions/{session_id}` — Get a session by ID
	- Response `200`: `{ ...session fields... }`
	- Response `404`: Session not found
- `POST /sessions` — Create a new session
	- Request body:
		```json
		{
			"title": "My chat",
			"isTemporary": false
		}
		```
	- Response `201`: `{ ...session fields... }`
- `POST /sessions/{session_id}/clear` — Delete all queries within a session, keeping the session itself
	- Response `200`: `{ ...session fields... }`
- `DELETE /sessions/{session_id}` — Delete a session and all its queries
	- Response `204`: No Content
	- Response `404`: Session not found

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
	- Response `200`: `[{ ...query fields... }]`
	- Response `404`: Session not found
- `POST /queries/{session_id}` — Create a new query (send a question to the chatbot)
	- Request body:
		```json
		{
			"question": "What is the capital of Italy?",
			"sessionHistory": [
				{ "question": "Previous question", "answer": "Previous answer" }
			]
		}
		```
		`sessionHistory` is optional. When provided, the listed question/answer pairs are injected into the agent's context as prior conversation turns.
	- Response `201`: `{ ...query fields... }`
	- Response `404`: Session not found

**Query fields:**
```json
{
	"id": "<uuid>",
	"sessionId": "<uuid>",
	"question": "string",
	"answer": "string",
	"topic": ["string"],
	"context": {
		"<filename>": [
			{ "chunkId": 0, "content": "string", "score": 0.95 }
		]
	},
	"createdAt": "YYYY-MM-DDTHH:MM:SS",
	"expiresAt": "YYYY-MM-DDTHH:MM:SS" | null
}
```

`context` is a map of source filename → list of document chunks retrieved from that file. Each chunk has a `chunkId`, its text `content`, and a similarity `score` (may be `null` depending on the vector DB provider). The map is empty when no RAG tool was invoked.

---

For more details, see the OpenAPI docs at `/` when the service is running.