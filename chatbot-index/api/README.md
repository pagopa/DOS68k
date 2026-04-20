# Chatbot Index API

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

This service uses a queue to send messages to a worker and a storage service. In order to use them correctly you have to set an `.env` file with the correct configuration. Follow below links for instructions:
- [queue](../../dos-utility/docs/features.md#3-queue-interface)
- [storage](../../dos-utility/docs/features.md#4-storage-interface)

## Start service

If you want to independently start this service, run the following commands.

```bash
cd .. # Make sure to be at the repo root level
docker compose up -d --build chatbot-index-api
```

Now you can access the service OpenAPI specification at `http://localhost:8003`.

## Post-start activities

This service interacts with external storage. The bucket specified in `BUCKET_NAME` must exist before the service can upload or retrieve documents — it is not created automatically.

- **MinIO (default in `.env.template`)**: access the MinIO web console at `http://localhost:9001` (default credentials: `admin` / `minioadmin`) and create the bucket from the UI, or use the AWS CLI:
  ```bash
  aws --endpoint-url http://localhost:9000 s3 mb s3://chatbot-index \
    --region us-east-1
  ```
- **AWS S3**: create the bucket through the AWS console or CLI as you normally would.