# Chatbot Index Worker

The index worker is the async document processing engine of DOS68k. It listens to a queue for indexing jobs, downloads documents from object storage, splits them into chunks, generates vector embeddings, and writes them to the vector database — making documents searchable by the chatbot.

## Prerequisites

- [uv](https://docs.astral.sh/uv/)
- [Docker](https://docs.docker.com/get-docker/)
- [task](https://taskfile.dev/)

## Quick start

### 1. Configure environment

Copy `.env.template` to `.env` and fill in the required values:

```bash
cp .env.template .env
```

At minimum, set these providers:
- `QUEUE_PROVIDER` — Queue backend (`sqs` or `redis`)
- `STORAGE_PROVIDER` — Storage backend (`aws_s3` or `minio`)
- `VECTOR_DB_PROVIDER` — Vector DB backend (`redis` or `qdrant`)
- `PROVIDER` — Embedding provider (`google`)
- `MODEL_API_KEY` — API key for the embedding provider

For detailed configuration, see [CONFIGURATION.md](docs/CONFIGURATION.md).

### 2. Run the worker

**Docker (recommended):**
```bash
docker compose up -d --build chatbot-index-worker
```

**Locally:**
```bash
uv run src/worker/main.py
```

## Supported documents

| Format | MIME type |
|---|---|
| PDF | `application/pdf` (text extracted page by page) |
| Plain text | `text/plain` |
| Markdown | `text/markdown` |

## Next steps

- **Configure providers**: See [CONFIGURATION.md](docs/CONFIGURATION.md) for queue, storage, and vector DB setup
- **Customize embeddings**: Learn about chunking and embedding settings in [CONFIGURATION.md](docs/CONFIGURATION.md)
- **Test**: Run `task test` to verify the setup
