# Chatbot API

The chatbot-api is a FastAPI service that provides session-based chat with an LLM, backed by RAG (Retrieval-Augmented Generation) for document-aware answers. Users can create sessions (chats) and send questions; the service retrieves relevant documents from a vector database and generates answers using an LLM.

## Quick Start

### 1. Install Dependencies

```bash
# From the repo root
docker compose up -d --build chatbot-api
```

This starts the chatbot-api, plus its dependencies (LocalStack, Redis, and others).

### 2. Configure Environment

Copy `.env.template` to `.env` and update:

```bash
FRONTEND_URL=http://localhost
VECTOR_DB_PROVIDER=redis
PROVIDER=google
MODEL_API_KEY=your-api-key  # Get from https://aistudio.google.com
```

See [CONFIGURATION.md](./docs/CONFIGURATION.md) for all options.

### 3. Test the Service

```bash
# Health check
curl http://localhost:8000/health

# Create a session and send a query
curl -X POST http://localhost:8000/sessions \
  -H "X-User-Id: 550e8400-e29b-41d4-a716-446655440000" \
  -H "X-User-Role: user" \
  -H "Content-Type: application/json" \
  -d '{"title": "My Chat", "isTemporary": false}'
```

Full API documentation is at `http://localhost:8000`.

---

## Documentation

- **[CONFIGURATION.md](./docs/CONFIGURATION.md)** — Environment variables, provider selection, database setup, customization
- **[INTEGRATION.md](./docs/INTEGRATION.md)** — Complete REST API reference with examples

---

## Development

### Prerequisites

- `uv` (Python package manager)
- `docker` and `docker compose`
- `task` (task runner)

### Run Tests

```bash
task test                # Run with 80% coverage threshold
task test:quick         # Run without coverage threshold
task test COV_THRESHOLD=90  # Override threshold
```

Test files use `.env.test` for configuration and don't require a real database.

### Lint & Format

```bash
uvx ruff check src/       # Lint Python code
uvx ruff format src/      # Format Python code
```

---

## Customization

### Custom RAG Tools

Mount tool configurations from a local directory using Docker volumes in `compose.yaml`:

```yaml
chatbot-api:
  volumes:
    - ./chatbot-api/scripts/tool_config:/app/src/modules/chatbot/tool/config
```

Or set `TOOLS_CONFIG_DIR=/path/to/tools` in `.env`. Each tool is a YAML file defining a vector index namespace. See [`src/modules/chatbot/tool/config/template.yaml`](./src/modules/chatbot/tool/config/template.yaml) for the schema.

### Custom Agent Behavior

Mount a custom agent config using Docker volumes in `compose.yaml`:

```yaml
chatbot-api:
  volumes:
    - ./my-agent.yaml:/app/src/modules/chatbot/agent/agent.yaml
```

Or set `AGENT_CONFIG_PATH=/path/to/agent.yaml` in `.env`. The file must contain `name`, `description`, `system_prompt`, and `system_header` fields.

---

## Populate Vector DB (For Testing)

The script [`scripts/populate_vector_db.py`](./scripts/populate_vector_db.py) seeds sample documents into the vector database:

```bash
cd chatbot-api

uv run python scripts/populate_vector_db.py \
  --provider redis \
  --topic software-dev \
  --embed-provider google \
  --google-api-key YOUR_KEY
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
