# Configuration Guide

This guide explains how to configure the Chatbot Index API for different environments and provider backends.

## Overview

The Chatbot Index API uses the **dos-utility** package's provider abstraction pattern. This means you can swap backends (e.g., Redis ↔ Qdrant for vector DB) by changing environment variables — no code changes required.

## Environment Variables

### Core Settings

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `FRONTEND_URL` | Yes | — | CORS allowed origin (format: `http://localhost` or `https://example.com`) |
| `INDEX_DOCUMENTS_BUCKET_NAME` | Yes | — | Name of the storage bucket for documents |
| `EMBED_DIM` | No | `768` | Embedding vector dimension. **Must match the worker's setting** |
| `LOG_LEVEL` | No | `20` | Python logging level (10=DEBUG, 20=INFO, 30=WARNING, 40=ERROR, 50=CRITICAL) |

### Provider Selection

| Variable | Supported Values | Default |
|----------|------------------|---------|
| `QUEUE_PROVIDER` | `redis`, `sqs` | `redis` |
| `STORAGE_PROVIDER` | `minio`, `aws_s3` | `minio` |
| `VECTOR_DB_PROVIDER` | `redis`, `qdrant` | `redis` |

---

## Queue Configuration

### Redis Queue

The default and simplest option. Good for local development and small deployments.

```bash
export QUEUE_PROVIDER=redis
export REDIS_HOST=redis-queue          # Redis hostname
export REDIS_PORT=6379                 # Redis port
export REDIS_STREAM=my-stream          # Stream name for messages
export REDIS_GROUP=my-group            # Consumer group name
```

**Docker Compose:**
```yaml
services:
  redis-queue:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

### AWS SQS Queue

For production deployments or AWS-hosted environments.

```bash
export QUEUE_PROVIDER=sqs
export SQS_ENDPOINT_URL=              # Omit for real AWS; set for LocalStack
export SQS_REGION=us-east-1            # AWS region
export SQS_QUEUE_URL=https://sqs.us-east-1.amazonaws.com/123456789/my-queue.fifo
export AWS_ACCESS_KEY_ID=<your-key>
export AWS_SECRET_ACCESS_KEY=<your-secret>
```

**For LocalStack testing:**
```bash
export SQS_ENDPOINT_URL=http://localstack:4566
export SQS_QUEUE_URL=http://sqs.us-east-1.localhost.localstack.cloud:4566/000000000000/my-queue.fifo
export SQS_QUEUE_NAME=my-queue.fifo
```

---

## Storage Configuration

### MinIO Storage

The default and recommended for local development.

```bash
export STORAGE_PROVIDER=minio
export MINIO_ENDPOINT=minio            # Hostname (no protocol)
export MINIO_PORT=9000                 # MinIO API port
export MINIO_ACCESS_KEY=admin          # Access key
export MINIO_SECRET_KEY=minioadmin     # Secret key
export MINIO_REGION=us-east-1          # Region
export MINIO_SECURE=false              # Use HTTPS
```

**Docker Compose:**
```yaml
services:
  minio:
    image: minio/minio:latest
    environment:
      MINIO_ROOT_USER: admin
      MINIO_ROOT_PASSWORD: minioadmin
    ports:
      - "9000:9000"
      - "9001:9001"  # Web console
    command: server /data
```

**Create bucket:**
```bash
aws --endpoint-url http://localhost:9000 s3 mb s3://chatbot-index --region us-east-1
```

### AWS S3 Storage

For production deployments in AWS.

```bash
export STORAGE_PROVIDER=aws_s3
export S3_REGION=us-east-1
export AWS_ACCESS_KEY_ID=<your-key>
export AWS_SECRET_ACCESS_KEY=<your-secret>
# S3_ENDPOINT is optional (used for S3-compatible services)
```

**Permissions needed (IAM policy):**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::chatbot-index",
        "arn:aws:s3:::chatbot-index/*"
      ]
    }
  ]
}
```

---

## Vector DB Configuration

### Redis Vector DB

The default. Works well with Redis queue (can use the same Redis instance).

```bash
export VECTOR_DB_PROVIDER=redis
export REDIS_HOST=redis-vdb            # Hostname
export REDIS_PORT=6379                 # Port
```

**Note:** If using Redis for both queue and vector DB, you must either:
1. Use the same Redis instance (same host/port) for both, OR
2. Use different providers (e.g., SQS for queue + Qdrant for vector DB)

### Qdrant Vector DB

For production or when you need separate vector DB infrastructure.

```bash
export VECTOR_DB_PROVIDER=qdrant
export QDRANT_HOST=localhost           # Qdrant hostname
export QDRANT_PORT=6333                # Qdrant API port
```

**Docker Compose:**
```yaml
services:
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - qdrant_storage:/qdrant/storage
volumes:
  qdrant_storage:
```

---

## Common Configuration Profiles

### Local Development (Minimal)

```bash
# .env file
export FRONTEND_URL=http://localhost
export QUEUE_PROVIDER=redis
export STORAGE_PROVIDER=minio
export VECTOR_DB_PROVIDER=redis
export INDEX_DOCUMENTS_BUCKET_NAME=chatbot-index
export REDIS_HOST=localhost
export REDIS_PORT=6379
export MINIO_ENDPOINT=localhost
export MINIO_PORT=9000
```

### Production on AWS

```bash
# .env file
export FRONTEND_URL=https://chatbot.example.com
export QUEUE_PROVIDER=sqs
export STORAGE_PROVIDER=aws_s3
export VECTOR_DB_PROVIDER=qdrant
export INDEX_DOCUMENTS_BUCKET_NAME=chatbot-index-prod

# AWS settings
export SQS_REGION=us-east-1
export SQS_QUEUE_URL=https://sqs.us-east-1.amazonaws.com/123456789/chatbot-queue.fifo
export S3_REGION=us-east-1
export QDRANT_HOST=qdrant.internal.example.com
export QDRANT_PORT=6333

# Credentials (use AWS IAM roles in production, not hardcoded keys)
export AWS_ACCESS_KEY_ID=<key>
export AWS_SECRET_ACCESS_KEY=<secret>
```

### Development with Real AWS (Hybrid)

```bash
# .env file
export FRONTEND_URL=http://localhost
export QUEUE_PROVIDER=redis           # Local Redis for fast iteration
export STORAGE_PROVIDER=aws_s3        # Real AWS for actual document storage
export VECTOR_DB_PROVIDER=qdrant      # Local Qdrant
export INDEX_DOCUMENTS_BUCKET_NAME=chatbot-index-dev

# AWS S3 only
export S3_REGION=us-east-1
export AWS_ACCESS_KEY_ID=<key>
export AWS_SECRET_ACCESS_KEY=<secret>

# Local services
export REDIS_HOST=localhost
export REDIS_PORT=6379
export QDRANT_HOST=localhost
export QDRANT_PORT=6333
```

---

## Troubleshooting Configuration

### Redis Connection Issues

```bash
# Test Redis connectivity
redis-cli -h $REDIS_HOST -p $REDIS_PORT ping
```

Expected output: `PONG`

### MinIO Connection Issues

```bash
# Test MinIO connectivity
curl -I http://$MINIO_ENDPOINT:$MINIO_PORT/minio/health/live
```

Expected output: `HTTP/1.1 200 OK`

### S3 Permissions Issues

```bash
# List buckets to verify credentials
aws s3 ls --region $S3_REGION
```

### Qdrant Connection Issues

```bash
# Check Qdrant API health
curl http://$QDRANT_HOST:$QDRANT_PORT/health
```

Expected output: JSON response with `status: "ok"`

---

## Provider Feature Matrix

| Feature | Redis | SQS | MinIO | S3 | Redis VDB | Qdrant |
|---------|-------|-----|-------|----|-----------| -------|
| Local dev | ✓ | ✗ | ✓ | ✗ | ✓ | ✓ |
| Production ready | ~ | ✓ | ~ | ✓ | ~ | ✓ |
| Scaling | Limited | ✓ | ✓ | ✓ | Limited | ✓ |
| Persistence | Optional | ✓ | ✓ | ✓ | Optional | ✓ |

**Notes:**
- Redis is great for small deployments but not ideal for scaling
- SQS and S3 are AWS-only but highly reliable and scalable
- Qdrant provides better vector search performance at scale
- ~ = works but not recommended for production

---

## Next Steps

- See [INTEGRATION.md](./INTEGRATION.md) for API usage examples
- Refer to [dos-utility documentation](../../dos-utility/docs/features.md) for detailed provider specifications
