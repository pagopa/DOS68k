# Configuration Guide

This guide covers all configuration options for the chatbot-api service. Environment variables should be set in a `.env` file at the service root.

## Overview

The chatbot-api requires configuration for three main areas:
- **Database & Storage** — where to persist sessions and queries
- **Vector DB & Retrieval** — where to store and retrieve document embeddings
- **LLM & Embedding Models** — which AI models to use for generation and embeddings

All providers are swappable and can be configured via environment variables. Start with the [Quick Setup](#quick-setup) section, then dive into provider-specific details.

## Quick Setup

Copy `.env.template` to `.env` and fill in these essential variables:

```bash
# Frontend URL (for CORS)
FRONTEND_URL=http://localhost

# NoSQL Database (sessions and queries storage)
NOSQL_PROVIDER=dynamodb  # or: none (for testing only)
DYNAMODB_ENDPOINT_URL=http://localstack
DYNAMODB_PORT=4566
DYNAMODB_REGION=us-east-1
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test

# Vector Database (embeddings and retrieval)
VECTOR_DB_PROVIDER=redis  # or: qdrant
REDIS_HOST=redis-vdb
REDIS_PORT=6379

# LLM Provider
PROVIDER=google  # or: mock (for testing without API keys)
MODEL_ID=gemini-2.0-flash
MODEL_API_KEY=your-api-key

# Embedding Model
EMBED_MODEL_ID=text-embedding-004
EMBED_DIM=768

# Database tables
SESSION_TABLENAME=sessions
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

For documentation on alternative NoSQL providers, see [`dos-utility` database configuration](../../dos-utility/docs/features.md#6-nosql-db-interface).

### Table Names

```bash
SESSION_TABLENAME=sessions   # Override default table name for sessions
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

For documentation on alternative vector DB providers, see [`dos-utility` vector DB configuration](../../dos-utility/docs/features.md#5-vector-db-interface).

## LLM & Embedding Configuration

The chatbot-api uses pluggable LLM and embedding providers. By default, it uses Google GenAI (Gemini).

### Selecting a Provider

#### Google GenAI (Default)

```bash
PROVIDER=google
MODEL_ID=gemini-2.0-flash      # Check Google's available models
MODEL_API_KEY=your-api-key      # Get from https://aistudio.google.com
MAX_TOKENS=1024                # Max output tokens per response

EMBED_MODEL_ID=text-embedding-004
EMBED_DIM=768                  # Must match dimension used during indexing
EMBED_BATCH_SIZE=100           # Texts per API call
EMBED_TASK=RETRIEVAL_QUERY     # RETRIEVAL_QUERY | RETRIEVAL_DOCUMENT | SEMANTIC_SIMILARITY
EMBED_RETRIES=3                # Retry attempts on API errors
EMBED_RETRY_MIN_SECONDS=1.0    # Min wait between retries
```

#### Mock Provider (Testing)

For local testing without API keys:

```bash
PROVIDER=mock

# No MODEL_ID, MODEL_API_KEY, or embedding keys needed
# Returns deterministic placeholder responses
```

### Swapping Providers

To use OpenAI, Azure OpenAI, or Bedrock:

1. **Uncomment the dependency** in `pyproject.toml`:
   ```toml
   # llama-index-llms-openai>=0.4.0
   # llama-index-embeddings-openai>=0.3.0
   ```

2. **Set the provider** in `.env`:
   ```bash
   PROVIDER=openai
   MODEL_ID=gpt-4o
   MODEL_API_KEY=sk-...
   ```

3. **Rebuild the container** (if running in Docker):
   ```bash
   docker compose up -d --build chatbot-api
   ```

See `src/modules/chatbot/models.py` for the complete list of supported providers and their configuration.

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
USE_ASYNC=true                 # Run retrieval asynchronously
```

Increasing `SIMILARITY_TOPK` provides more context but uses more tokens and may degrade answer quality if irrelevant chunks are included.

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

If not set, defaults to built-in configs in `src/modules/chatbot/tool/config/`. Tools must be YAML files defining:
- Tool name and description
- Vector index name (must exist in vector DB)
- Retrieval settings

See [`src/modules/chatbot/tool/config/template.yaml`](../src/modules/chatbot/tool/config/template.yaml) for the schema.

#### Agent System Prompt

```bash
AGENT_CONFIG_PATH=/app/my-agent.yaml
```

If not set, uses the default `src/modules/chatbot/agent/agent.yaml`. The YAML file must contain:
- `name` — Agent name
- `description` — Agent description
- `system_prompt` — System instructions
- `system_header` — Reasoning header format

See the [default agent.yaml](../src/modules/chatbot/agent/agent.yaml) for reference.

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

## Runtime Health Checks

After starting, verify the service is healthy:

```bash
# Service status
curl http://localhost:8000/health

# Database connectivity
curl http://localhost:8000/health/db
```

If database health check fails, verify:
- NoSQL DB connection details in `.env`
- Tables exist and have correct schema
- Network connectivity to DB endpoint
