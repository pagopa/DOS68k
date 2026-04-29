# Chatbot Index API

## Overview

The **Chatbot Index API** is the document indexing gateway for the DOS68K RAG platform. It provides a simple HTTP API for creating indexes, uploading documents, and managing the documents within each index.

**Key responsibilities:**
- Create, delete, and list document indexes
- Upload documents (PDF, Markdown, plain text) to indexes
- List and delete documents from indexes
- Enqueue documents for asynchronous processing by the [Chatbot Index Worker](../worker/README.md)

The service stores uploaded documents in object storage (MinIO or AWS S3) and sends processing messages to a queue (Redis or SQS). The worker service then asynchronously embeds the documents and ingests them into the vector DB.

## Quick Start

### Prerequisites

- `uv` (Python package manager)
- `docker` and `docker compose`
- `task` (task runner, optional but recommended)

### Start the service

```bash
cd ../..  # Go to repo root
docker compose up -d --build chatbot-index-api
```

The API will be available at `http://localhost:8003`. The OpenAPI specification is at `http://localhost:8003/docs`.

### Create storage bucket

Before uploading documents, create the storage bucket:

**MinIO (default):**
```bash
aws --endpoint-url http://localhost:9000 s3 mb s3://chatbot-index --region us-east-1
```

Or access the MinIO console at `http://localhost:9001` (username: `admin`, password: `minioadmin`) and create the bucket from the UI.

**AWS S3:** Use the AWS console or CLI as normal.

### Health check

Verify all dependencies are connected:

```bash
curl http://localhost:8003/health
curl http://localhost:8003/health/queue
curl http://localhost:8003/health/storage
curl http://localhost:8003/health/vdb
```

## Documentation

- **[Configuration Guide](./docs/CONFIGURATION.md)** — Detailed setup for each provider (Redis, SQS, MinIO, S3, Qdrant)
- **[Integration Guide](./docs/INTEGRATION.md)** — API examples and usage patterns

## API Overview

All endpoints require two headers (except `/health` endpoints):
- `X-User-Id: <uuid>` — Unique user identifier
- `X-User-Role: admin` — User role (currently only `admin` is supported)

**Health checks (no auth required):**
- `GET /health` — Service status
- `GET /health/{queue,storage,vdb}` — Dependency status

**Index management:**
- `POST /index/{index_id}` — Create index
- `DELETE /index/{index_id}` — Delete index
- `GET /index/all` — List all indexes

**Document management:**
- `POST /index/{index_id}/documents` — Upload document
- `GET /index/{index_id}/documents` — List documents
- `DELETE /index/{index_id}/documents/{document_name}` — Delete document

See the [Integration Guide](./docs/INTEGRATION.md) for detailed endpoint documentation and examples.

## Local Development

### Run tests

```bash
task test                   # Run with 80% coverage threshold
task test COV_THREASHOLD=90 # Custom threshold
task test:quick            # No coverage enforcement
```

### Lint and format

```bash
uv run ruff check src
uv run ruff format src
```

## Configuration

Minimal configuration needed to start:

```bash
export FRONTEND_URL=http://localhost          # CORS origin
export QUEUE_PROVIDER=redis                   # Queue backend
export STORAGE_PROVIDER=minio                 # Storage backend
export VECTOR_DB_PROVIDER=redis               # Vector DB backend
export INDEX_DOCUMENTS_BUCKET_NAME=chatbot-index  # Storage bucket name
```

See the [Configuration Guide](./docs/CONFIGURATION.md) for complete provider-specific settings.

---

## API Documentation

Index and Document endpoints require the header:

```
X-User-Id: <uuid>
```

Health endpoints do not require authentication.

### Health

- `GET /health` — Service status
  - Response: `{ "status": "ok", "service": "Chatbot Index API" }`
- `GET /health/queue` — Queue connectivity
  - Response: `{ "status": "ok", "service": "Chatbot Index API", "queue": "connected" }`
- `GET /health/storage` — Storage connectivity
  - Response: `{ "status": "ok", "service": "Chatbot Index API", "storage": "connected" }`
- `GET /health/vdb` — Vector DB connectivity
  - Response: `{ "status": "ok", "service": "Chatbot Index API", "vector_db": "connected" }`

### Indexes

- `POST /index/{index_id}` — Create a new index
  - Response `201`:
    ```json
    { "indexId": "string", "userId": "<uuid>", "createdAt": "YYYY-MM-DDTHH:MM:SS" }
    ```
  - Response `409`: Index already exists

- `DELETE /index/{index_id}` — Delete an index and all its documents
  - Response `200`: `{ "message": "Index '<index_id>' deleted successfully" }`
  - Response `404`: Index not found

- `GET /index/all` — List all indexes
  - Response `200`: `["index-name-1", "index-name-2"]`

### Documents

- `POST /index/{index_id}/documents` — Upload a document into an index
  - Request: multipart form with a `file` field. Accepted formats: `.pdf`, `.md`, `.txt`
  - Response `202`:
    ```json
    { "indexId": "string", "documentName": "string", "message": "string" }
    ```
  - Response `404`: Index not found
  - Response `415`: Unsupported file type

- `GET /index/{index_id}/documents` — List documents in an index
  - Response `200`: `[{ "documentName": "string" }]`
  - Response `404`: Index not found

- `DELETE /index/{index_id}/documents/{document_name}` — Delete a document from an index
  - Response `200`: `{ "message": "Document '<document_name>' deleted from index '<index_id>'" }`
  - Response `404`: Index or document not found

---

For more details, see the OpenAPI docs at `/` when the service is running.
