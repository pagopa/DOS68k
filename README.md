# DOS68K

DOS68K is an open-source, self-hosted, **plug-and-play RAG chatbot platform**.
Bring your own documents; DOS68K ingests them and serves a chat interface that
answers questions grounded in your content, citing the passages it used. Every
piece of infrastructure — database, queue, storage, vector database,
authentication, tracing — is swappable by configuration.

> **New here? Start with [Overview](./docs/overview.md)** for what the platform
> can and cannot do, then follow [Getting started](./docs/getting-started.md) to
> run it.

## Documentation

| Guide | What it covers |
|---|---|
| [Overview](./docs/overview.md) | What DOS68K is, what you can/can't do, architecture, gotchas |
| [Getting started](./docs/getting-started.md) | Prerequisites → providers → env → run → verify, plus using your own documents |
| [Configuration](./docs/configuration.md) | Reference for service-level settings |
| [Provider reference](./dos-utility/docs/features.md) | Infrastructure/provider variables (database, queue, storage, vector DB, auth, tracing) |
| [CONTEXT.md](./CONTEXT.md) | Glossary of platform terms |

## Roles

DOS68K is single-tenant per deployment: one operator runs an instance for one
audience. Two roles are enforced:

- **Admin** — the operator. Manages **Indexes** and **Documents**, and can chat.
- **User** — the audience the Admin opens the deployment to. Can only chat.

How many identities exist and how they sign in is decided by the identity
provider you connect, not by DOS68K. See
[Overview: authentication model](./docs/overview.md#authentication-model).

## Services

| Service | Path | Description |
|---|---|---|
| Chatbot API | [chatbot-api](./chatbot-api/README.md) | Core chatbot. Manages sessions and queries; runs the RAG agent |
| Chatbot Index API | [chatbot-index/api](./chatbot-index/api/README.md) | Accepts document uploads and manages Indexes |
| Chatbot Index Worker | [chatbot-index/worker](./chatbot-index/worker/README.md) | Processes uploads asynchronously into embeddings |
| Chatbot Evaluate API | [chatbot-evaluate/api](./chatbot-evaluate/api/README.md) | Accepts feedback and evaluation requests |
| Chatbot Evaluate Worker | [chatbot-evaluate/worker](./chatbot-evaluate/worker/README.md) | Runs RAGAS evaluation jobs |
| Auth | [auth](./auth/README.md) | Validates identity for the gateway (AWS Cognito or local mock) |
| Masking | [masking](./masking/README.md) | Optional PII detection and masking (Presidio + spaCy) |
| Frontend | [frontend](./frontend/README.md) | Demo web UI for chat and administration |
| API Gateway | [api-gateway](./traefik/README.md) | Single entry point: forward-auth, routing, rate limiting, CORS |
| DOS Utility | [dos-utility](./dos-utility/README.md) | Shared package with all infrastructure abstractions (not a running service) |

## Quick start

```bash
# 1. Copy and fill the env files (see Getting started for the full list)
# 2. Set your Google API key in the three services that call Google
# 3. Build and run everything
docker compose up -d --build
```

The full walkthrough — including verifying with the bundled demo data — is in
[Getting started](./docs/getting-started.md).
</content>
