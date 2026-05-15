# Configuration Guide

This guide explains how to configure the Chatbot Index API for different environments and provider backends.

## Overview

The Chatbot Index API uses the **dos-utility** package's provider
abstraction pattern. You can swap backends (e.g. Redis ↔ Qdrant for
vector DB) by changing environment variables — no code changes
required. The provider-specific environment variables, valid value
sets, and connection contracts are owned by `dos-utility`; see its
[features documentation](../../../dos-utility/docs/features.md) for the
authoritative list. The examples below show the values this service is
typically configured with.

## Environment Variables

### Core Settings

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `FRONTEND_URL` | No | `http://localhost` | CORS allowed origin (format: `http://localhost` or `https://example.com`) |
| `INDEX_DOCUMENTS_BUCKET_NAME` | Yes | — | Name of the storage bucket for documents (no default — startup fails if unset) |
| `EMBED_DIM` | No | `768` | Embedding vector dimension used at index creation. Must match the value the worker uses when ingesting chunks. |
| `LOG_LEVEL` | No | `20` | Python logging level (10=DEBUG, 20=INFO, 30=WARNING, 40=ERROR, 50=CRITICAL) |

### Provider Selection

The Index API selects backends at startup using three env vars. Values
are lowercase (the `dos-utility` enums are `StrEnum`).

| Variable | Supported Values |
|----------|------------------|
| `QUEUE_PROVIDER` | `redis`, `sqs` |
| `STORAGE_PROVIDER` | `minio`, `aws_s3` |
| `VECTOR_DB_PROVIDER` | `redis`, `qdrant` |

There is no built-in default for the provider env vars — they must be
set (typically via `.env`).

For the full list of provider-specific env vars and connection details
(`REDIS_HOST`, `SQS_QUEUE_URL`, `MINIO_*`, `QDRANT_HOST`, AWS
credentials, etc.), see the `dos-utility` documentation:

- **Queue** — [dos-utility queue interface](../../../dos-utility/docs/features.md#queue-interface)
- **Storage** — [dos-utility storage interface](../../../dos-utility/docs/features.md#storage-interface)
- **Vector DB** — [dos-utility vector DB interface](../../../dos-utility/docs/features.md#5-vector-db-interface)

The `.env.template` at the root of this service ships with the
defaults used by `compose.yaml` (Redis queue + MinIO storage + Redis
vector DB) and commented-out alternatives.

> **Shared Redis host/port note:** `REDIS_HOST` / `REDIS_PORT` are
> consumed by both the queue and the vector DB providers. If both use
> Redis they must point to the same instance; to use separate Redis
> instances, switch one side to a different provider (SQS or Qdrant).

---

## Common Configuration Profiles

### Local Development (Minimal)

Matches the defaults shipped in `.env.template` / `compose.yaml`.

```bash
export FRONTEND_URL=http://localhost
export INDEX_DOCUMENTS_BUCKET_NAME=chatbot-index
export QUEUE_PROVIDER=redis
export STORAGE_PROVIDER=minio
export VECTOR_DB_PROVIDER=redis
# Provider-specific connection vars (REDIS_HOST, MINIO_*, etc.)
# are documented in the dos-utility features docs.
```

### Production on AWS

```bash
export FRONTEND_URL=https://chatbot.example.com
export INDEX_DOCUMENTS_BUCKET_NAME=chatbot-index-prod
export QUEUE_PROVIDER=sqs
export STORAGE_PROVIDER=aws_s3
export VECTOR_DB_PROVIDER=qdrant
# Plus the AWS / Qdrant connection vars required by dos-utility.
```

### Development with Real AWS (Hybrid)

```bash
export FRONTEND_URL=http://localhost
export INDEX_DOCUMENTS_BUCKET_NAME=chatbot-index-dev
export QUEUE_PROVIDER=redis    # Local Redis for fast iteration
export STORAGE_PROVIDER=aws_s3 # Real AWS for actual document storage
export VECTOR_DB_PROVIDER=qdrant
```

For the connection variables each combination needs (AWS region/keys,
SQS queue URL, MinIO endpoint, Qdrant host, etc.), see the
[dos-utility features documentation](../../../dos-utility/docs/features.md).

---

## Next Steps

- See [INTEGRATION.md](./INTEGRATION.md) for API usage examples
- Refer to the [dos-utility documentation](../../../dos-utility/docs/features.md) for detailed provider specifications and troubleshooting
