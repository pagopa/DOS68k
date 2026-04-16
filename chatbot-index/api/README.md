# Chatbot Index API

## Overview

The chatbot-index-api service manages document indexes for the RAG pipeline. It lets users create and delete indexes, upload documents (PDF, Markdown, plain text) into an index, and list or remove indexed documents.

When a document is uploaded, the file is stored in object storage (MinIO or AWS S3) and a message is enqueued for asynchronous processing by the chatbot-index worker, which handles the actual embedding and vector DB ingestion.

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

- [Queue](../../dos-utility/docs/features.md#3-queue-interface)
- [Storage](../../dos-utility/docs/features.md#4-storage-interface)
- [Vector DB](../../dos-utility/docs/features.md#5-vector-db-interface)

Once you've done that, update your `.env` with these:

```bash
export FRONTEND_URL=<frontend-url> # For CORS origins, with format http(s)://hostname

export INDEX_DOCUMENTS_BUCKET_NAME=<bucket-name> # Name of the storage bucket for uploaded documents (required, no default)

export EMBED_DIM=768 # Embedding vector dimension. Must match the value configured in the chatbot-index worker. Defaults to 768

export LOG_LEVEL=20 # Python logging level (10=DEBUG, 20=INFO, 30=WARNING, 40=ERROR, 50=CRITICAL). Defaults to 20 (INFO)
```

## Start service

If you want to independently start this service, run the following commands.

```bash
cd ../.. # Make sure to be at the repo root level
docker compose up -d --build chatbot-index-api
```

Now you can access the service OpenAPI specification at `http://localhost:8003`.

## Post-start activities

This service interacts with external storage. The bucket specified in `INDEX_DOCUMENTS_BUCKET_NAME` must exist before the service can upload or retrieve documents — it is not created automatically.

- **MinIO (default in compose.yaml)**: access the MinIO web console at `http://localhost:9001` (default credentials: `admin` / `minioadmin`) and create the bucket from the UI, or use the AWS CLI:
  ```bash
  aws --endpoint-url http://localhost:9000 s3 mb s3://chatbot-index \
    --region us-east-1
  ```
- **AWS S3**: create the bucket through the AWS console or CLI as you normally would.

To verify all external dependencies (queue, storage, vector DB) are reachable after starting:

```
GET http://localhost:8003/health/queue
GET http://localhost:8003/health/storage
GET http://localhost:8003/health/vdb
```

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
