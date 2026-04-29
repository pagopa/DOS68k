# API Integration Guide

This document describes all HTTP endpoints exposed by the chatbot-api service. The service runs at `http://localhost:8000` by default.

## Authentication

All endpoints (except health checks) require the `X-User-Id` header:

```bash
curl -H "X-User-Id: 550e8400-e29b-41d4-a716-446655440000" \
     http://localhost:8000/sessions/all
```

The `X-User-Id` value should be a UUID representing the current user. In production, this is injected by the API gateway (KrakenD).

## OpenAPI Documentation

Interactive API documentation is available at:

- **Swagger UI**: `http://localhost:8000`
- **ReDoc**: `http://localhost:8000/redoc`

## Base URL

```
http://localhost:8000
```

All paths in this document are relative to the base URL.

---

## Health Endpoints

### Service Health

```
GET /health
```

Returns the service status and version info.

**Response:**
```json
{
  "status": "ok",
  "service": "Chatbot API"
}
```

### Database Health

```
GET /health/db
```

Checks connectivity to the configured NoSQL database and vector DB.

**Response:**
```json
{
  "status": "ok",
  "service": "Chatbot API",
  "database": "connected"
}
```

---

## Session Management

### List All Sessions

```
GET /sessions/all
```

Retrieve all chat sessions for the authenticated user.

**Headers:**
```
X-User-Id: <uuid>
```

**Response (200 OK):**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "userId": "550e8400-e29b-41d4-a716-446655440001",
    "title": "Project discussion",
    "createdAt": "2025-04-29T10:30:00",
    "expiresAt": "2025-06-28T10:30:00"
  }
]
```

Empty array if no sessions exist.

### Get Session

```
GET /sessions/{session_id}
```

Retrieve a specific session by ID.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `session_id` | string (uuid) | The session ID to retrieve |

**Headers:**
```
X-User-Id: <uuid>
```

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "userId": "550e8400-e29b-41d4-a716-446655440001",
  "title": "Project discussion",
  "createdAt": "2025-04-29T10:30:00",
  "expiresAt": "2025-06-28T10:30:00"
}
```

**Response (404 Not Found):**
```json
{
  "detail": "Session not found"
}
```

### Create Session

```
POST /sessions
```

Create a new chat session for the user.

**Headers:**
```
X-User-Id: <uuid>
Content-Type: application/json
```

**Request Body:**
```json
{
  "title": "My new chat",
  "isTemporary": false
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | Yes | Display name for the session |
| `isTemporary` | boolean | No | If `true`, session auto-deletes after `SESSION_EXPIRATION_DAYS`. Default: `false` |

**Response (201 Created):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "userId": "550e8400-e29b-41d4-a716-446655440001",
  "title": "My new chat",
  "createdAt": "2025-04-29T10:30:00",
  "expiresAt": null
}
```

If `isTemporary: true`, `expiresAt` will contain the expiration timestamp.

### Clear Session

```
POST /sessions/{session_id}/clear
```

Delete all queries (messages) in a session, but keep the session itself.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `session_id` | string (uuid) | The session to clear |

**Headers:**
```
X-User-Id: <uuid>
```

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "userId": "550e8400-e29b-41d4-a716-446655440001",
  "title": "My new chat",
  "createdAt": "2025-04-29T10:30:00",
  "expiresAt": null
}
```

### Delete Session

```
DELETE /sessions/{session_id}
```

Permanently delete a session and all its queries.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `session_id` | string (uuid) | The session to delete |

**Headers:**
```
X-User-Id: <uuid>
```

**Response (204 No Content)**

**Response (404 Not Found):**
```json
{
  "detail": "Session not found"
}
```

---

## Queries (Chat Messages)

### List Session Queries

```
GET /queries/{session_id}
```

Retrieve all messages in a session, ordered by creation date.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `session_id` | string (uuid) | The session containing the queries |

**Headers:**
```
X-User-Id: <uuid>
```

**Response (200 OK):**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440010",
    "sessionId": "550e8400-e29b-41d4-a716-446655440000",
    "question": "What is RAG?",
    "answer": "RAG stands for Retrieval-Augmented Generation...",
    "badAnswer": false,
    "topic": ["retrieval", "generation"],
    "context": {
      "rag-guide.pdf": [
        {
          "chunkId": 0,
          "content": "Retrieval-Augmented Generation (RAG) is a technique...",
          "score": 0.95
        }
      ]
    },
    "createdAt": "2025-04-29T10:32:00",
    "expiresAt": null
  }
]
```

**Response (404 Not Found):**
```json
{
  "detail": "Session not found"
}
```

### Send Query (Chat Message)

```
POST /queries/{session_id}
```

Send a message to the chatbot and receive an answer.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `session_id` | string (uuid) | The session to query |

**Headers:**
```
X-User-Id: <uuid>
Content-Type: application/json
```

**Request Body:**
```json
{
  "question": "What is the capital of Italy?",
  "sessionHistory": [
    {
      "question": "Tell me about European cities",
      "answer": "Europe has many beautiful cities..."
    }
  ]
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `question` | string | Yes | The user's question |
| `sessionHistory` | array | No | Previous Q&A pairs to inject as context |

**sessionHistory Item:**
```json
{
  "question": "string",
  "answer": "string"
}
```

**Response (201 Created):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440011",
  "sessionId": "550e8400-e29b-41d4-a716-446655440000",
  "question": "What is the capital of Italy?",
  "answer": "Rome is the capital of Italy.",
  "badAnswer": false,
  "topic": [],
  "context": {},
  "createdAt": "2025-04-29T10:33:00",
  "expiresAt": null
}
```

**Response (404 Not Found):**
```json
{
  "detail": "Session not found"
}
```

---

## Response Data Models

### Session Object

```json
{
  "id": "string (uuid)",
  "userId": "string (uuid)",
  "title": "string",
  "createdAt": "string (ISO 8601)",
  "expiresAt": "string (ISO 8601) or null"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `id` | uuid | Unique session identifier |
| `userId` | uuid | Owner of the session |
| `title` | string | Display name |
| `createdAt` | ISO 8601 timestamp | When the session was created |
| `expiresAt` | ISO 8601 timestamp or null | When the session expires (null for permanent sessions) |

### Query Object

```json
{
  "id": "string (uuid)",
  "sessionId": "string (uuid)",
  "question": "string",
  "answer": "string",
  "badAnswer": "boolean",
  "topic": ["string"],
  "context": {
    "<filename>": [
      {
        "chunkId": "number",
        "content": "string",
        "score": "number or null"
      }
    ]
  },
  "createdAt": "string (ISO 8601)",
  "expiresAt": "string (ISO 8601) or null"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `id` | uuid | Unique query identifier |
| `sessionId` | uuid | Parent session |
| `question` | string | User's question |
| `answer` | string | Chatbot's response |
| `badAnswer` | boolean | Whether the user marked this as a poor response |
| `topic` | string[] | Tags from the RAG tools that were invoked |
| `context` | object | Retrieved document chunks by filename |
| `context[filename][]` | array | List of chunks from a source file |
| `context[filename][].chunkId` | number | Sequential chunk index within the file |
| `context[filename][].content` | string | Chunk text content |
| `context[filename][].score` | number or null | Similarity score (0-1, null if not provided by vector DB) |
| `createdAt` | ISO 8601 timestamp | When the query was created |
| `expiresAt` | ISO 8601 timestamp or null | When the query expires (inherits from session) |

---

## Error Handling

All error responses follow this format:

```json
{
  "detail": "Human-readable error message"
}
```

### Common HTTP Status Codes

| Status | Meaning | Example |
|--------|---------|---------|
| `200` | Success | Session retrieved |
| `201` | Created | New session or query created |
| `204` | No Content | Successful deletion (no response body) |
| `400` | Bad Request | Invalid request body |
| `404` | Not Found | Session or query not found |
| `500` | Server Error | Unexpected internal error |

---

## Usage Example

### Python with requests

```python
import requests
import uuid
from datetime import datetime

BASE_URL = "http://localhost:8000"
USER_ID = str(uuid.uuid4())

headers = {"X-User-Id": USER_ID}

# Create a session
session_resp = requests.post(
    f"{BASE_URL}/sessions",
    headers=headers,
    json={"title": "My Chat", "isTemporary": False}
)
session = session_resp.json()
print(f"Created session: {session['id']}")

# Send a query
query_resp = requests.post(
    f"{BASE_URL}/queries/{session['id']}",
    headers=headers,
    json={"question": "What is RAG?"}
)
query = query_resp.json()
print(f"Question: {query['question']}")
print(f"Answer: {query['answer']}")
print(f"Context: {query['context']}")

# List all queries
queries_resp = requests.get(
    f"{BASE_URL}/queries/{session['id']}",
    headers=headers
)
queries = queries_resp.json()
print(f"Total messages: {len(queries)}")

# Delete session
requests.delete(f"{BASE_URL}/sessions/{session['id']}", headers=headers)
```

### JavaScript with fetch

```javascript
const BASE_URL = "http://localhost:8000";
const userId = crypto.randomUUID();

const headers = { "X-User-Id": userId };

// Create a session
const sessionResp = await fetch(`${BASE_URL}/sessions`, {
  method: "POST",
  headers: { ...headers, "Content-Type": "application/json" },
  body: JSON.stringify({ title: "My Chat", isTemporary: false })
});
const session = await sessionResp.json();
console.log(`Created session: ${session.id}`);

// Send a query
const queryResp = await fetch(`${BASE_URL}/queries/${session.id}`, {
  method: "POST",
  headers: { ...headers, "Content-Type": "application/json" },
  body: JSON.stringify({ question: "What is RAG?" })
});
const query = await queryResp.json();
console.log(`Answer: ${query.answer}`);
```

---

## Rate Limiting

The API Gateway (KrakenD) enforces a **100 requests/second** rate limit globally. Requests exceeding this limit will receive a `429 Too Many Requests` response.

---

## Support

For issues or questions:
- Check [CONFIGURATION.md](./CONFIGURATION.md) for setup issues
- See the [main README](../README.md) for overview and local development
- Review the [project architecture](../../CLAUDE.md) for design decisions
