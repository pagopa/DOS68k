# Integration Guide

This guide provides practical examples for integrating with the Chatbot Index API.

## Quick Start

### 1. Create an Index

Create a new document index:

```bash
curl -X POST http://localhost:8003/index/my-docs \
  -H "X-User-Id: user-123" \
  -H "X-User-Role: admin"
```

Response (201):
```json
{
  "indexId": "my-docs",
  "userId": "user-123",
  "createdAt": "2026-04-29T10:30:00"
}
```

### 2. Upload a Document

Upload a PDF to the index:

```bash
curl -X POST http://localhost:8003/index/my-docs/documents \
  -H "X-User-Id: user-123" \
  -H "X-User-Role: admin" \
  -F "file=@document.pdf"
```

Response (202 — accepted, async processing):
```json
{
  "indexId": "my-docs",
  "documentName": "document.pdf",
  "message": "Document queued for processing"
}
```

**Supported formats:** `.pdf`, `.md`, `.txt`

### 3. List Documents

Check what's in your index:

```bash
curl http://localhost:8003/index/my-docs/documents \
  -H "X-User-Id: user-123" \
  -H "X-User-Role: admin"
```

Response (200):
```json
[
  { "documentName": "document.pdf" },
  { "documentName": "guide.md" }
]
```

### 4. Delete a Document

Remove a document from the index:

```bash
curl -X DELETE http://localhost:8003/index/my-docs/documents/document.pdf \
  -H "X-User-Id: user-123" \
  -H "X-User-Role: admin"
```

Response (200):
```json
{
  "message": "Document 'document.pdf' deleted from index 'my-docs'"
}
```

---

## Complete API Reference

### Authentication

All endpoints except `/health` require two headers:

```bash
-H "X-User-Id: <uuid>"
-H "X-User-Role: admin"
```

- **X-User-Id:** Any string (UUID, email, user ID) — used to track who owns resources
- **X-User-Role:** Currently only `admin` is supported

### Health Endpoints

#### Get Service Status

```
GET /health
```

Response (200):
```json
{
  "status": "ok",
  "service": "Chatbot Index API"
}
```

#### Check Queue Connectivity

```
GET /health/queue
```

Response (200):
```json
{
  "status": "ok",
  "service": "Chatbot Index API",
  "queue": "connected"
}
```

#### Check Storage Connectivity

```
GET /health/storage
```

Response (200):
```json
{
  "status": "ok",
  "service": "Chatbot Index API",
  "storage": "connected"
}
```

#### Check Vector DB Connectivity

```
GET /health/vdb
```

Response (200):
```json
{
  "status": "ok",
  "service": "Chatbot Index API",
  "vector_db": "connected"
}
```

---

### Index Operations

#### Create Index

Create a new named index for storing documents.

```
POST /index/{index_id}
```

**Parameters:**
- `index_id` (path): Unique identifier for the index (alphanumeric, hyphens allowed)

**Headers:**
- `X-User-Id: <uuid>` (required)

**Response (201):**
```json
{
  "indexId": "string",
  "userId": "string",
  "createdAt": "2026-04-29T10:30:00"
}
```

**Response (409) — Conflict:**
```json
{
  "detail": "Index 'my-docs' already exists"
}
```

**Example:**
```bash
curl -X POST http://localhost:8003/index/customer-docs \
  -H "X-User-Id: user-abc123"
```

#### Delete Index

Delete an index and all its documents. **Warning:** This is permanent.

```
DELETE /index/{index_id}
```

**Parameters:**
- `index_id` (path): Index to delete

**Headers:**
- `X-User-Id: <uuid>` (required)

**Response (200):**
```json
{
  "message": "Index 'my-docs' deleted successfully"
}
```

**Response (404):**
```json
{
  "detail": "Index 'nonexistent' not found"
}
```

**Example:**
```bash
curl -X DELETE http://localhost:8003/index/old-docs \
  -H "X-User-Id: user-abc123" \
  -H "X-User-Role: admin"
```

#### List All Indexes

Get all index names in the system.

```
GET /index/all
```

**Response (200):**
```json
["index-1", "index-2", "customer-docs"]
```

---

### Document Operations

#### Upload Document

Upload a document to an index. The file is stored and a message is enqueued for processing.

```
POST /index/{index_id}/documents
```

**Parameters:**
- `index_id` (path): Target index

**Headers:**
- `X-User-Id: <uuid>` (required)

**Body:** Multipart form data
- `file`: The document file (required). Supported: `.pdf`, `.md`, `.txt`

**Response (202 — Accepted):**
```json
{
  "indexId": "my-docs",
  "documentName": "filename.pdf",
  "message": "Document queued for processing"
}
```

**Response (404):**
```json
{
  "detail": "Index 'nonexistent' not found"
}
```

**Response (415 — Unsupported Media Type):**
```json
{
  "detail": "File type not supported. Supported formats: .pdf, .md, .txt"
}
```

**Example — Upload PDF:**
```bash
curl -X POST http://localhost:8003/index/my-docs/documents \
  -H "X-User-Id: user-abc123" \
  -F "file=@whitepaper.pdf"
```

**Example — Upload Markdown:**
```bash
curl -X POST http://localhost:8003/index/my-docs/documents \
  -H "X-User-Id: user-abc123" \
  -F "file=@README.md"
```

#### List Documents

Get all documents in an index.

```
GET /index/{index_id}/documents
```

**Parameters:**
- `index_id` (path): Target index

**Headers:**
- `X-User-Id: <uuid>` (required)

**Response (200):**
```json
[
  { "documentName": "whitepaper.pdf" },
  { "documentName": "README.md" },
  { "documentName": "guide.txt" }
]
```

**Response (404):**
```json
{
  "detail": "Index 'nonexistent' not found"
}
```

**Example:**
```bash
curl http://localhost:8003/index/my-docs/documents \
  -H "X-User-Id: user-abc123"
```

#### Delete Document

Remove a document from an index and all its vectors from the vector DB.

```
DELETE /index/{index_id}/documents/{document_name}
```

**Parameters:**
- `index_id` (path): Target index
- `document_name` (path): Exact filename to delete

**Headers:**
- `X-User-Id: <uuid>` (required)

**Response (200):**
```json
{
  "message": "Document 'whitepaper.pdf' deleted from index 'my-docs'"
}
```

**Response (404):**
```json
{
  "detail": "Document not found in index 'my-docs'"
}
```

**Example:**
```bash
curl -X DELETE http://localhost:8003/index/my-docs/documents/whitepaper.pdf \
  -H "X-User-Id: user-abc123"
```

---

## Usage Patterns

### Python Client Example

```python
import requests
from pathlib import Path

API_URL = "http://localhost:8003"
USER_ID = "user-123"
HEADERS = {"X-User-Id": USER_ID, "X-User-Role": "admin"}

# Create index
response = requests.post(
    f"{API_URL}/index/my-docs",
    headers=HEADERS
)
print(response.json())

# Upload document
with open("document.pdf", "rb") as f:
    response = requests.post(
        f"{API_URL}/index/my-docs/documents",
        headers=HEADERS,
        files={"file": f}
    )
print(response.json())

# List documents
response = requests.get(
    f"{API_URL}/index/my-docs/documents",
    headers=HEADERS
)
print(response.json())

# Delete document
response = requests.delete(
    f"{API_URL}/index/my-docs/documents/document.pdf",
    headers=HEADERS
)
print(response.json())

# Delete index
response = requests.delete(
    f"{API_URL}/index/my-docs",
    headers=HEADERS
)
print(response.json())
```

### JavaScript/Node.js Client Example

```javascript
const API_URL = "http://localhost:8003";
const USER_ID = "user-123";
const HEADERS = { "X-User-Id": USER_ID, "X-User-Role": "admin" };

// Create index
async function createIndex(indexId) {
  const response = await fetch(`${API_URL}/index/${indexId}`, {
    method: "POST",
    headers: HEADERS
  });
  return response.json();
}

// Upload document
async function uploadDocument(indexId, file) {
  const formData = new FormData();
  formData.append("file", file);
  
  const response = await fetch(
    `${API_URL}/index/${indexId}/documents`,
    {
      method: "POST",
      headers: { "X-User-Id": USER_ID, "X-User-Role": "admin" },
      body: formData
    }
  );
  return response.json();
}

// List documents
async function listDocuments(indexId) {
  const response = await fetch(
    `${API_URL}/index/${indexId}/documents`,
    {
      headers: HEADERS
    }
  );
  return response.json();
}

// Delete document
async function deleteDocument(indexId, documentName) {
  const response = await fetch(
    `${API_URL}/index/${indexId}/documents/${documentName}`,
    {
      method: "DELETE",
      headers: HEADERS
    }
  );
  return response.json();
}

// Delete index
async function deleteIndex(indexId) {
  const response = await fetch(`${API_URL}/index/${indexId}`, {
    method: "DELETE",
    headers: HEADERS
  });
  return response.json();
}
```

---

## Asynchronous Processing

When you upload a document, the API returns **202 Accepted** immediately. The actual processing happens asynchronously:

1. **API receives** → Stores file in object storage (MinIO/S3)
2. **API enqueues** → Pushes message to queue (Redis/SQS)
3. **Worker processes** → Consumes message, embeds document, ingests vectors

To check if processing is complete:

- **Monitor worker logs:** Check the Index Worker service logs for completion messages
- **Query vector DB:** Use the Chatbot API to search — if your document appears in results, processing is done
- **Check index health:** The Health endpoints tell you if vector DB is reachable, but not processing status

There is currently **no polling endpoint** to check individual document processing status. If you need this, consider:
- Adding a simple webhook callback in the worker
- Querying the vector DB directly to verify document chunks exist
- Monitoring CloudWatch/application logs for processing events

---

## Error Handling

### Common HTTP Status Codes

| Status | Meaning | Example |
|--------|---------|---------|
| 200 | Success (GET, DELETE) | Document listed or deleted |
| 201 | Created | Index created successfully |
| 202 | Accepted | Document upload queued for processing |
| 400 | Bad Request | Missing required header or invalid format |
| 401 | Unauthorized | Missing X-User-Id header |
| 404 | Not Found | Index or document doesn't exist |
| 409 | Conflict | Index already exists |
| 415 | Unsupported Media Type | File format not supported |
| 500 | Server Error | Internal error; check logs |

### Retry Strategy

Implement exponential backoff for transient failures:

```python
import time
import requests

def upload_with_retry(index_id, file_path, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.post(
                f"http://localhost:8003/index/{index_id}/documents",
                headers={"X-User-Id": "user-123"},
                files={"file": open(file_path, "rb")}
            )
            if response.status_code == 202:
                return response.json()
            elif response.status_code >= 500:
                # Retry on server errors
                wait = 2 ** attempt
                print(f"Retrying in {wait}s...")
                time.sleep(wait)
            else:
                # Don't retry client errors
                response.raise_for_status()
        except requests.RequestException as e:
            if attempt == max_retries - 1:
                raise
            wait = 2 ** attempt
            time.sleep(wait)
```

---

## Best Practices

1. **Always provide X-User-Id:** Use a stable, unique identifier (UUID, email, user ID from your auth system)
2. **Check health before operations:** Call `/health` endpoints before batch uploads
3. **Handle 202 responses:** Don't assume documents are immediately searchable after upload
4. **Use appropriate index names:** Use meaningful, URL-safe names (alphanumeric, hyphens)
5. **Batch operations carefully:** For many documents, implement rate limiting or async processing on your side
6. **Monitor queue/storage:** Periodically check `/health/queue` and `/health/storage` to catch connectivity issues early
7. **Test error paths:** Always handle 4xx and 5xx responses gracefully

---

## Next Steps

- See [CONFIGURATION.md](./CONFIGURATION.md) for backend setup
- See [Chatbot Index Worker](../worker/README.md) to understand async processing
