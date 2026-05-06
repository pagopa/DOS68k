# Configuration

This guide covers all configuration options for the index worker.

## Environment variables

All variables are read from `.env`. Copy `.env.template` to `.env` and fill in the values.

### Provider selection

| Variable | Required | Accepted values | Description |
|---|---|---|---|
| `QUEUE_PROVIDER` | yes | `sqs`, `redis` | Queue backend for consuming indexing jobs |
| `STORAGE_PROVIDER` | yes | `aws_s3`, `minio` | Object storage backend for downloading documents |
| `VECTOR_DB_PROVIDER` | yes | `redis`, `qdrant` | Vector database backend for storing embeddings |
| `PROVIDER` | yes | `google` | Embedding provider |

### Embedding configuration

| Variable | Required | Default | Description |
|---|---|---|---|
| `MODEL_API_KEY` | yes | — | API key for the embedding provider |
| `EMBED_MODEL_ID` | yes | — | Embedding model identifier (e.g. `text-embedding-004` for Google) |
| `EMBED_CHUNK_SIZE` | yes | — | Chunk size in tokens for splitting documents |
| `EMBED_CHUNK_OVERLAP` | yes | — | Overlapping tokens between consecutive chunks |
| `EMBED_DIM` | no | `768` | Vector dimension. **Must match your vector DB index configuration.** |
| `EMBED_BATCH_SIZE` | no | `100` | Number of chunks embedded per API call |
| `EMBED_TASK` | no | `RETRIEVAL_DOCUMENT` | Embedding task type passed to the provider |
| `EMBED_RETRIES` | no | `3` | Number of retry attempts on embedding API failure |
| `EMBED_RETRY_MIN_SECONDS` | no | `1.0` | Minimum wait between retries (seconds) |

### Storage

| Variable | Required | Description |
|---|---|---|
| `INDEX_DOCUMENTS_BUCKET_NAME` | yes | Object storage bucket where uploaded documents are stored |

### Logging

| Variable | Required | Default | Description |
|---|---|---|---|
| `LOG_LEVEL` | no | `20` | Python logging level: `10`=DEBUG, `20`=INFO, `30`=WARNING |

### Provider-specific variables

Additional variables for each provider backend are documented in [dos-utility features](../../dos-utility/docs/features.md):
- [Queue interface](../../dos-utility/docs/features.md#3-queue-interface) — SQS/Redis variables
- [Storage interface](../../dos-utility/docs/features.md#4-storage-interface) — S3/MinIO variables
- [Vector DB interface](../../dos-utility/docs/features.md#5-vector-db-interface) — Redis/Qdrant variables

## Customization

### Switching providers

All three external dependencies (queue, storage, vector DB) are accessed through `dos-utility` interfaces. Switching providers requires **only configuration changes — no code changes**:

- **Queue**: `SQS` ↔ `Redis` — change `QUEUE_PROVIDER` and provider-specific env vars
- **Storage**: `AWS S3` ↔ `MinIO` — change `STORAGE_PROVIDER` and provider-specific env vars
- **Vector DB**: `Redis` ↔ `Qdrant` — change `VECTOR_DB_PROVIDER` and provider-specific env vars

See [dos-utility features](../../dos-utility/docs/features.md) for available providers and their configuration.

### Embedding provider

The worker currently supports Google GenAI as the embedding provider. To add a new provider:

1. Implement the provider in `src/worker/models.py:get_embed_model()`
2. No other changes are needed — the rest of the pipeline is provider-agnostic

### Chunking strategy

Chunk size and overlap are controlled by `EMBED_CHUNK_SIZE` and `EMBED_CHUNK_OVERLAP` (both in tokens):

- **Smaller chunks**: Improve retrieval precision, reduce context per result
- **Larger chunks**: Preserve more context per result, may reduce precision

Changes take effect on the next indexing job. **Existing chunks in the vector DB are not retroactively re-chunked** — only new documents use the updated settings.

### Vector dimension alignment

The `EMBED_DIM` variable must match the dimension configured in your vector DB index:

- For Google GenAI models: typically 768 dimensions
- For other providers: consult the provider's documentation
- **Mismatch will cause insertion errors** — verify before production

## Testing

Run tests with quick mode (no coverage threshold):
```bash
task test:quick
```

Run tests with 80% minimum coverage threshold:
```bash
task test
```

Override the threshold:
```bash
task test COV_THREASHOLD=90
```
