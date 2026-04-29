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

Available topics: `software-dev`, `zephyr-corp`, `borgonero-fc`, `all`.
