# Configuration reference

This is the single reference for **service-level** settings — models, masking,
sessions, evaluation, and the like. Each service reads these from its own `.env`
file (copied from the `.env.template` beside it).

**Infrastructure / provider settings are documented separately**, in
[the dos-utility feature reference](../dos-utility/docs/features.md): which
backend each capability uses (`AUTH_PROVIDER`, `NOSQL_PROVIDER`,
`QUEUE_PROVIDER`, `STORAGE_PROVIDER`, `VECTOR_DB_PROVIDER`, `TRACING_PROVIDER`)
and the per-provider connection variables (DynamoDB, Redis, MinIO, S3, SQS,
Qdrant, Langfuse, AWS credentials, …). This page does not repeat them.

A few variables appear in more than one service. When they do, the values
**must agree** across services — see [Cross-service rules](#cross-service-rules).

---

## Chatbot

Service: [chatbot-api](../chatbot-api/README.md). Runs the RAG agent.

| Variable | Default | Purpose |
|---|---|---|
| `PROVIDER` | `google` | Model provider. Only `google` is wired end to end. |
| `MODEL_ID` | `gemini-2.0-flash` | LLM used to answer. |
| `MODEL_API_KEY` | — (**required**) | Google API key. |
| `MAX_TOKENS` | `1024` | Max tokens generated per answer. |
| `TEMPERATURE_AGENT` | `0.0` | Agent sampling temperature (`0.0` = deterministic). |
| `EMBED_MODEL_ID` | `text-embedding-004` | Embedding model used to embed the **query**. |
| `EMBED_DIM` | `768` | Embedding dimension. |
| `EMBED_TASK` | `RETRIEVAL_QUERY` | Embedding task type for queries. |
| `EMBED_BATCH_SIZE` | `100` | Texts per embedding API call. |
| `EMBED_RETRIES` | `3` | Retry attempts on embedding errors. |
| `EMBED_RETRY_MIN_SECONDS` | `1.0` | Minimum wait between retries. |
| `SIMILARITY_TOPK` | `5` | Chunks retrieved per query (a tool config can override per tool). |
| `MASK_PII` | `false` | Mask PII in questions and answers before storing them. |
| `MASKING_SERVICE_URL` | `http://masking:3000` | Masking service URL (used only when `MASK_PII=true`). |
| `SESSION_EXPIRATION_DAYS` | `90` | Lifetime of a *temporary* session before it auto-expires. |
| `SESSIONS_TABLENAME` | `sessions` | NoSQL table for sessions. |
| `QUERY_TABLENAME` | `queries` | NoSQL table for queries. |
| `TOOLS_CONFIG_DIR` | built-in `tool/config/` | Directory of RAG tool config YAMLs. |
| `AGENT_CONFIG_PATH` | built-in `agent.yaml` | Path to the agent (system prompt) config. |
| `FRONTEND_URL` | `http://localhost` | Allowed CORS origin. |
| `LOG_LEVEL` | `20` (INFO) | Python log level. |

## Document Indexing — API

Service: [chatbot-index/api](../chatbot-index/api/README.md). Accepts uploads
and index management.

| Variable | Default | Purpose |
|---|---|---|
| `INDEX_DOCUMENTS_BUCKET_NAME` | `documents` | Object-storage bucket for uploaded files. |
| `EMBED_DIM` | `768` | Dimension used when creating a new index. |
| `FRONTEND_URL` | `http://localhost` | Allowed CORS origin. |
| `LOG_LEVEL` | `20` (INFO) | Python log level. |

## Document Indexing — Worker

Service: [chatbot-index/worker](../chatbot-index/worker/README.md). Parses,
chunks, embeds, and stores documents.

| Variable | Default | Purpose |
|---|---|---|
| `PROVIDER` | `google` | Embedding provider. Only `google` is wired. |
| `MODEL_API_KEY` | — (**required**) | Google API key. |
| `EMBED_MODEL_ID` | `text-embedding-004` | Embedding model used to embed **documents**. |
| `EMBED_DIM` | `768` | Embedding dimension. |
| `EMBED_TASK` | `RETRIEVAL_DOCUMENT` | Embedding task type for documents. |
| `EMBED_CHUNK_SIZE` | `256` | Chunk size in tokens. |
| `EMBED_CHUNK_OVERLAP` | `20` | Overlapping tokens between chunks. |
| `EMBED_BATCH_SIZE` | `100` | Texts per embedding API call. |
| `EMBED_RETRIES` | `3` | Retry attempts on embedding errors. |
| `EMBED_RETRY_MIN_SECONDS` | `1.0` | Minimum wait between retries. |
| `INDEX_DOCUMENTS_BUCKET_NAME` | `documents` | Object-storage bucket for uploaded files. |
| `LOG_LEVEL` | `20` (INFO) | Python log level. |

## Evaluation — API

Service: [chatbot-evaluate/api](../chatbot-evaluate/api/README.md). Accepts
feedback and evaluation requests.

| Variable | Default | Purpose |
|---|---|---|
| `EVALUATE_UPPER_LIMIT` | `50` | Max queries evaluated per "evaluate all" request. |
| `QUERY_TABLENAME` | `queries` | NoSQL table for queries. |
| `FRONTEND_URL` | `http://localhost` | Allowed CORS origin. |
| `LOG_LEVEL` | `20` (INFO) | Python log level. |

## Evaluation — Worker

Service: [chatbot-evaluate/worker](../chatbot-evaluate/worker/README.md). Runs
RAGAS scoring.

| Variable | Default | Purpose |
|---|---|---|
| `PROVIDER` | `google` | Model/embedding provider. Only `google` is wired. |
| `MODEL_API_KEY` | — (**required**) | Google API key. |
| `MODEL_ID` | `gemini-2.5-flash-lite` | LLM used as the RAGAS judge and to rewrite follow-up questions. |
| `TEMPERATURE` | `0` | LLM temperature. |
| `MAX_TOKENS` | `2048` | Max tokens per LLM call. |
| `EMBED_MODEL_ID` | `gemini-embedding-001` | Embedding model used internally by RAGAS (need not match the chatbot's). |
| `EMBED_DIM` | `768` | Embedding dimension. |
| `EMBED_TASK` | `RETRIEVAL_QUERY` | Embedding task type. |
| `EMBED_BATCH_SIZE` / `EMBED_RETRIES` / `EMBED_RETRY_MIN_SECONDS` | `100` / `3` / `1.0` | Embedding batching and retries. |
| `CONFIG_PATH` | — (**required**) | Path to the follow-up-question prompt YAML. |
| `QUERY_TABLENAME` | — (**required**) | NoSQL table for queries. |
| `SESSION_TABLENAME` | — (**required**) | NoSQL table for sessions. |
| `LOG_LEVEL` | `20` (INFO) | Python log level. |

## Authentication

Service: [auth](../auth/README.md). It has no service-level business variables —
its only configuration is provider selection (`AUTH_PROVIDER`) and the
provider's connection settings, all documented in
[the dos-utility auth reference](../dos-utility/docs/features.md#2-auth-interface).

## PII Masking

Service: [masking](../masking/README.md). It reads **no environment variables** —
its behaviour (languages, detected entity types) is set in a config file shipped
with the service.

## Frontend

Service: [frontend](../frontend/README.md). Demo UI.

| Variable | Default | Purpose |
|---|---|---|
| `VITE_API_BASE_URL` | `http://localhost:8080` | API gateway URL the browser calls. Set for you in `compose.yaml`. |

---

## Cross-service rules

These values appear in multiple services and **must be consistent**, or the
platform breaks in quiet, hard-to-diagnose ways.

### Embedding consistency

The chatbot embeds the user's **query** and compares it against the **document**
embeddings produced during indexing. For the comparison to be meaningful, both
sides must use the **same embedding model and the same `EMBED_DIM`**:

- `chatbot-api` `EMBED_MODEL_ID` / `EMBED_DIM`
- `chatbot-index/worker` `EMBED_MODEL_ID` / `EMBED_DIM`
- the seeding script (`populate_vector_db.py`), if you use it

The shipped defaults already align (`text-embedding-004`, dim `768`). If you
change the model or dimension, change it in **all** of the above. A mismatch does
not raise an error — retrieval simply returns irrelevant results.

> The Evaluation worker's `EMBED_MODEL_ID` is independent: it is used only inside
> RAGAS scoring and never compared against the stored document vectors.

### Shared table names

`chatbot-api`, `chatbot-evaluate/api`, and `chatbot-evaluate/worker` all read and
write the same `queries` table; `chatbot-api` and `chatbot-evaluate/worker` share
the `sessions` table. Keep `QUERY_TABLENAME` / `SESSIONS_TABLENAME` /
`SESSION_TABLENAME` pointing at the same tables in the same NoSQL instance.

### Shared storage bucket

`chatbot-index/api` writes uploaded files to `INDEX_DOCUMENTS_BUCKET_NAME`, and
`chatbot-index/worker` reads them back from it. The two **must match**, and the
bucket must exist (the bundled `compose.yaml` provisions it via a one-shot
`minio-init` job).

### Queue separation

Indexing and Evaluation must use **different** queues so their jobs never mix.
Under the bundled setup, indexing uses the Redis stream `my-stream` and
evaluation uses `evaluate-stream`. If you reconfigure queues, keep them
separate. Within each capability, the **API and worker must use the same**
provider, stream, and group.
</content>
