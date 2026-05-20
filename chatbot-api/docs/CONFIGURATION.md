# Configuration Guide

This guide covers all configuration options for the chatbot-api service. Environment variables should be set in a `.env` file at the service root.

## Overview

The chatbot-api requires configuration for four main areas:
- **Database & Storage** — where to persist sessions and queries
- **Vector DB & Retrieval** — where to store and retrieve document embeddings
- **LLM & Embedding Models** — which AI models to use for generation and embeddings
- **Tracing** — LLM observability backend (optional, default is no-op)

All providers are swappable and can be configured via environment variables. Start with the [Quick Setup](#quick-setup) section, then dive into provider-specific details.

## Authentication

All API endpoints (except health checks) require two headers:

| Header | Description |
|--------|-------------|
| `X-User-Id` | UUID of the authenticated user |
| `X-User-Role` | User's role: `admin` or `user` |

These headers are typically injected by the API gateway (Traefik, via forward-auth to the auth service) in production. For local testing, include them in each request.

## Quick Setup

Copy `.env.template` to `.env` and fill in these essential variables:

```bash
# Frontend URL (for CORS)
FRONTEND_URL=http://localhost

# NoSQL Database (sessions and queries storage)
NOSQL_PROVIDER=dynamodb
DYNAMODB_ENDPOINT_URL=http://localstack
DYNAMODB_PORT=4566
DYNAMODB_REGION=us-east-1
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test

# Vector Database (embeddings and retrieval)
VECTOR_DB_PROVIDER=redis  # or: qdrant
REDIS_HOST=redis-vdb
REDIS_PORT=6379

# LLM Provider (only "google" is fully wired end-to-end)
PROVIDER=google
MODEL_ID=gemini-2.0-flash
MODEL_API_KEY=your-api-key

# Embedding Model
EMBED_MODEL_ID=text-embedding-004
EMBED_DIM=768

# Database tables
SESSIONS_TABLENAME=sessions
QUERY_TABLENAME=queries
```

## Database Configuration

### NoSQL Database

The chatbot-api uses a NoSQL database to persist user sessions and query history. The service supports multiple backends via the `dos-utility` package.

#### DynamoDB (Recommended)

```bash
NOSQL_PROVIDER=dynamodb

# Connection details
DYNAMODB_ENDPOINT_URL=http://localstack  # Use AWS endpoint for production
DYNAMODB_PORT=4566
DYNAMODB_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
```

**Table Schema Required:**

The service expects two pre-existing tables:

| Table | Partition Key | Sort Key | TTL Attribute | Purpose |
|-------|---|---|---|---|
| `sessions` | `userId` (String) | `id` (String) | `expiresAt` | Store user chat sessions |
| `queries` | `sessionId` (String) | `id` (String) | `expiresAt` | Store individual queries/messages |

When using LocalStack (via Docker Compose), tables are created automatically. For external DynamoDB, create them manually.

**Session Expiration:**

```bash
SESSION_EXPIRATION_DAYS=90  # Days before temporary sessions auto-delete (DynamoDB only)
```

Temporary sessions (`isTemporary: true`) automatically expire after this period. If using a non-DynamoDB backend, implement your own cleanup job using `expiresAt` timestamp.

#### Other Backends

For documentation on alternative NoSQL providers and the full set of
backend-specific environment variables, see
[`dos-utility` database configuration](../../dos-utility/docs/features.md#6-nosql-db-interface).

### Table Names

```bash
SESSIONS_TABLENAME=sessions  # Override default table name for sessions
QUERY_TABLENAME=queries      # Override default table name for queries
```

## Vector Database Configuration

The vector database stores document embeddings for RAG retrieval. All tools must target the same vector DB.

### Redis (Recommended)

```bash
VECTOR_DB_PROVIDER=redis

REDIS_HOST=redis-vdb         # Hostname or IP
REDIS_PORT=6379              # Port number
# REDIS_PASSWORD=             # Optional password (uncomment if needed)
```

**Namespace Convention:**

Each tool creates a separate index/namespace using the tool's `indexName` from its YAML config. For example, if your tool config has `indexName: my-docs`, the service queries the `my-docs` namespace in Redis.

### Qdrant

```bash
VECTOR_DB_PROVIDER=qdrant

QDRANT_HOST=localhost        # Hostname or IP
QDRANT_PORT=6333             # Port number
# QDRANT_API_KEY=             # Optional API key (uncomment if needed)
```

### Other Backends

For documentation on alternative vector DB providers and the full set of
backend-specific environment variables, see
[`dos-utility` vector DB configuration](../../dos-utility/docs/features.md#5-vector-db-interface).

## LLM & Embedding Configuration

The chatbot-api currently supports a single fully wired LLM/embedding
provider: **Google GenAI (Gemini)**. The `PROVIDER` setting accepts only
`google`. Other providers (OpenAI, Azure OpenAI, Bedrock) appear as
commented dependencies in `pyproject.toml` but require code changes in
`src/modules/chatbot/models.py` and `src/modules/chatbot/env.py` to be
enabled — they are not selectable purely via configuration.

### Google GenAI

```bash
PROVIDER=google
MODEL_ID=gemini-2.0-flash      # Check Google's available models
MODEL_API_KEY=your-api-key     # Get from https://aistudio.google.com
MAX_TOKENS=1024                # Max output tokens per response

EMBED_MODEL_ID=text-embedding-004
EMBED_DIM=768                  # Must match dimension used during indexing
EMBED_BATCH_SIZE=100           # Texts per API call
EMBED_TASK=RETRIEVAL_QUERY     # RETRIEVAL_QUERY | RETRIEVAL_DOCUMENT | SEMANTIC_SIMILARITY
EMBED_RETRIES=3                # Retry attempts on API errors
EMBED_RETRY_MIN_SECONDS=1.0    # Min wait between retries
```

### Adding a New Provider

To wire up an additional provider:

1. Uncomment the matching dependency in `pyproject.toml`
   (e.g. `llama-index-llms-openai`, `llama-index-embeddings-openai`).
2. Add a branch for the new provider in `get_llm` / `get_embed_model`
   in `src/modules/chatbot/models.py`.
3. Widen the `Literal["google"]` type on `provider` in
   `src/modules/chatbot/env.py`.
4. Rebuild the container: `docker compose up -d --build chatbot-api`.

### Embedding Model Dimension

The `EMBED_DIM` **must match** the dimension used when indexing documents:

- Google Embedding API: `768` or `256`
- OpenAI: `1536` (text-embedding-3-small) or `3072` (text-embedding-3-large)
- Cohere: varies by model

If documents were indexed with dimension 768 but you configure `EMBED_DIM=1536`, retrieval will fail silently (no chunks found).

## Retrieval Configuration

### Similarity Search

```bash
SIMILARITY_TOPK=5              # Number of top chunks to retrieve per query
```

Increasing `SIMILARITY_TOPK` provides more context but uses more tokens
and may degrade answer quality if irrelevant chunks are included.

Async query execution is enabled unconditionally in the tool loader
(`use_async=True`); there is no environment variable to disable it.

## Agent Configuration

### Response Generation

```bash
TEMPERATURE_AGENT=0.0          # 0.0 = deterministic, 1.0 = creative
```

Set to `0.0` for consistent, fact-based responses. Increase toward `1.0` for more varied generation (not recommended for RAG).

### Custom Configurations

#### Tool Configuration

```bash
TOOLS_CONFIG_DIR=/app/custom-tools  # Path to YAML tool configs
```

If not set, defaults to the built-in directory at `src/modules/chatbot/tool/config/`
(which ships with only a `template.yaml`). Each YAML file declares one tool with:
- `name` — unique tool name exposed to the agent
- `description` — tells the agent when to use the tool
- `index_id` — vector DB index/namespace to query (must exist)
- `similarity_top_k` (optional) — per-tool override of `SIMILARITY_TOPK`
- `qa_prompt` (optional) — overrides the default LlamaIndex QA prompt
- `refine_prompt` (optional) — overrides the default refine prompt

See [`src/modules/chatbot/tool/config/template.yaml`](../src/modules/chatbot/tool/config/template.yaml) for the full schema and inline documentation.

#### Agent System Prompt

```bash
AGENT_CONFIG_PATH=/app/my-agent.yaml
```

If not set, uses the default `src/modules/chatbot/agent/agent.yaml`. The YAML file may contain:
- `name` — Agent name
- `description` — Agent description
- `system_prompt` — System instructions
- `system_header` — Reasoning header format (used by the ReAct loop)

All four fields are technically optional at the Pydantic-settings level
(they default to `None`), but a usable agent needs at minimum a
`system_prompt` and a `system_header`. See the
[default agent.yaml](../src/modules/chatbot/agent/agent.yaml) for reference.

## Session Management

### Temporary Sessions

Sessions can be marked temporary at creation time:

```json
{
  "title": "Temporary Chat",
  "isTemporary": true
}
```

**Behavior:**
- All queries inherit the session's `expiresAt` timestamp
- After expiration, DynamoDB auto-deletes the session and all its queries (TTL)
- For non-DynamoDB backends, implement a cleanup job using the `expiresAt` field

### Session Expiration

```bash
SESSION_EXPIRATION_DAYS=90     # Days until temporary sessions expire
```

Temporary sessions expire `SESSION_EXPIRATION_DAYS` after creation. Once expired, they are automatically deleted from DynamoDB.

## PII Masking (Optional)

If you have a masking service deployed, enable PII detection and anonymization:

```bash
MASK_PII=true                                    # Enable PII masking
MASKING_SERVICE_URL=http://masking:3000         # Masking service endpoint
```

When enabled:
- User questions are scanned for PII before being sent to the agent
- Agent responses are scanned for PII before being stored
- Detected PII is replaced with placeholders in stored data

The masking service must implement the masking contract defined in the DOS68K architecture. Disable this feature by setting `MASK_PII=false`.

## Logging

### Log Level

```bash
LOG_LEVEL=20   # 10=DEBUG, 20=INFO, 30=WARNING, 40=ERROR, 50=CRITICAL
```

Set to `10` (DEBUG) to enable detailed logs including:
- Incoming HTTP requests
- Agent reasoning steps
- Tool invocations and results
- Retrieved document chunks
- Generated responses

Useful for troubleshooting retrieval quality and agent behavior.

## CORS Configuration

```bash
FRONTEND_URL=http://localhost  # Frontend origin for CORS (include protocol and port)
```

Only requests from this origin will be allowed. Use the exact URL including protocol (`http://` or `https://`) and port.

## Tracing (Optional)

Each query can be shipped as a **Trace** to an observability backend, carrying the prompt, answer, session and user metadata, and a nested span for the LLM generation step. The feature is opt-in and safe to leave disabled.

### Selecting a Provider

```bash
TRACING_PROVIDER=noop      # Default — no external calls, safe for local dev and tests
# TRACING_PROVIDER=langfuse  # Ship traces to a Langfuse instance
```

### Langfuse

[Langfuse](https://langfuse.com) is an open-source LLM observability platform. Use it to inspect traces, score responses, and monitor latency.

```bash
TRACING_PROVIDER=langfuse
LANGFUSE_PUBLIC_KEY=your-public-key   # From Langfuse project settings
LANGFUSE_SECRET_KEY=your-secret-key   # From Langfuse project settings
LANGFUSE_HOST=https://cloud.langfuse.com  # Or your self-hosted URL
```

After enabling, each successful query appears in Langfuse with:
- Prompt and answer as input/output
- Session ID and user ID as metadata
- An `llm_generation` span for the LLM step

The tracer never blocks the request path — telemetry is buffered in-process and shipped in the background. If the tracing backend is unreachable, the request succeeds and `tracingTraceId` is `null` in the response.

### Trace ID in the Response

When tracing is active, `POST /queries/{session_id}` returns a `tracingTraceId` field:

```json
{
  "answer": "...",
  "tracingTraceId": "abc123"
}
```

Use this ID to look up the trace in your observability backend.

For full provider documentation and advanced settings (`LANGFUSE_FLUSH_AT`, `LANGFUSE_FLUSH_INTERVAL_S`), see [`dos-utility` tracing configuration](../../dos-utility/docs/features.md#8-tracing-interface).

## Runtime Health Checks

After starting, verify the service is healthy:

```bash
# Service status
curl http://localhost:8000/health

# NoSQL connectivity
curl http://localhost:8000/health/db
```

`/health/db` only probes the NoSQL backend (not the vector DB) and
always returns HTTP 200; an unhealthy backend is signalled by
`"database": "NOT connected"` in the JSON body.

If the database health check reports `NOT connected`, verify:
- NoSQL DB connection details in `.env`
- Tables exist and have correct schema
- Network connectivity to the DB endpoint
