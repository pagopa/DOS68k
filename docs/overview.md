# Overview

This page explains what DOS68K is, what it can and cannot do, and how its
pieces fit together — enough to decide whether it fits your use case before you
install anything. For vocabulary, see [`CONTEXT.md`](../CONTEXT.md). To set it
up, see [Getting started](./getting-started.md).

## What DOS68K is

DOS68K is a **self-hosted, single-tenant RAG (Retrieval-Augmented Generation)
chatbot platform**. You bring your own documents; DOS68K ingests them into
searchable indexes and serves a chat interface where users ask questions and get
answers grounded in those documents, with the source passages shown alongside.

"Single-tenant per deployment" means one operator runs one instance for one
audience. The platform does not host multiple isolated customers — you deploy
your own copy and decide who gets in.

It is built as a set of small services that talk through a single API gateway,
and every piece of infrastructure (database, queue, storage, vector database,
authentication, tracing) is swappable by configuration rather than code. See
[Architecture](#architecture) below.

The chatbot is a **ReAct agent**: for each question it reasons in steps,
deciding when to call a retrieval tool to pull relevant passages from your
documents before it writes an answer. Because this pattern depends on the
language model reliably following its reasoning format, the *choice of model is
load-bearing* — see [the model limitation below](#what-you-cannot-do-current-limitations).

## Roles

DOS68K enforces exactly two roles:

- **Admin** — the operator. Creates and manages **Indexes** and **Documents**,
  and can also chat with the deployment (e.g. to test it).
- **User** — the audience the Admin opens the deployment to. Can only chat with
  the documents the Admin has indexed.

DOS68K does not manage user accounts or issue credentials. *How many* admins and
users exist, and how they log in, is decided by the identity provider you plug
in (see [authentication](#authentication-model) below).

## What you can do

- Stand up a chatbot that answers **only** from documents you provide, citing
  the passages (**Sources**) it used.
- Organise knowledge into multiple isolated **Indexes** (e.g. one per product,
  team, or topic).
- Ingest **PDF, Markdown, and plain-text** documents; processing happens
  asynchronously in the background.
- Hold multi-turn conversations in per-user **Sessions**, including temporary
  sessions that auto-expire.
- Customise the assistant's personality and guardrails (its system prompt) and
  the retrieval prompts, via YAML — no code changes.
- Optionally **mask PII** in questions and answers before they are stored.
- Optionally ship full **traces** of every query to an observability backend
  (Langfuse).
- **Evaluate** answer quality automatically (RAGAS metrics) and collect
  thumbs-up/down feedback from users.
- Swap the underlying infrastructure (vector database, queue, storage, etc.)
  by changing environment variables — see
  [the dos-utility feature reference](../dos-utility/docs/features.md).

## What you cannot do (current limitations)

These are real constraints in the current codebase. Read them before planning a
deployment — several are easy to trip over.

- **LLM and embeddings: Google Gemini only — and only one model is tested.**
  Two separate constraints stack here. First, Google is the only model provider
  *wired* end to end: a Google API key is mandatory, and other providers (OpenAI,
  Azure OpenAI, Bedrock) appear as commented-out stubs that require code changes
  to enable. Second, even within Google, only `gemini-2.5-flash` has been
  *tested* to drive the ReAct agent correctly. These are not the same guarantee:
  wiring a provider makes it run, but the [ReAct pattern](#what-dos68k-is)
  depends on the model emitting a strict reasoning format, so a different or
  weaker model can produce a broken reasoning loop even once wired. Changing
  `MODEL_ID` away from the tested model is unsupported.
- **NoSQL database: DynamoDB only.** No other NoSQL backend is implemented.
- **Document formats: PDF, Markdown, plain text only.** Other file types are
  rejected.
- **No built-in production authentication.** Out of the box the login is a
  *mock* for development and demos (a "Continue as User / Admin" button). For a
  real deployment you must connect an external identity provider (AWS Cognito is
  the wired option). See [authentication](#authentication-model).
- **Creating an Index does not make it answerable.** The chatbot can only
  retrieve from an Index that has a **Tool config** pointing at it, and tool
  configs are read **only at chatbot startup**. After creating an Index and
  uploading documents, you must add a tool config for it and restart the chatbot
  service. See [Getting started](./getting-started.md#6-use-your-own-documents).
- **The frontend is a demo UI**, meant for testing and showcasing the platform —
  not a production-ready application.
- **Temporary-session expiry relies on DynamoDB's native TTL.**

## Architecture

DOS68K is a collection of services behind a single **API gateway**. The gateway
is the only public entry point: it authenticates every protected request and
routes it to the right backend.

| Service | What it does | Page |
|---|---|---|
| API Gateway | Single entry point; authentication, routing, rate limiting, CORS | [traefik](../traefik/README.md) |
| Chatbot | Chat sessions and queries; runs the RAG agent that retrieves and answers | [chatbot-api](../chatbot-api/README.md) |
| Document Indexing | Admin uploads documents; they are processed asynchronously into an Index | [chatbot-index/api](../chatbot-index/api/README.md), [worker](../chatbot-index/worker/README.md) |
| Evaluation | User feedback and automatic answer-quality scoring (RAGAS) | [chatbot-evaluate/api](../chatbot-evaluate/api/README.md), [worker](../chatbot-evaluate/worker/README.md) |
| Authentication | Validates identity for the gateway's forward-auth | [auth](../auth/README.md) |
| PII Masking | Optional anonymisation of personal data | [masking](../masking/README.md) |
| Frontend | Demo web UI (chat + admin) | [frontend](../frontend/README.md) |
| DOS Utility | Shared package providing all infrastructure abstractions; not a running service | [dos-utility](../dos-utility/README.md) |

### How a request flows

Every protected request enters through the gateway, which calls the **auth**
service to validate the caller and then forwards the request to the backend with
the caller's identity attached. Backends never see the raw login token — only
the identity the gateway vouches for. This "forward-auth" pattern is why the
gateway is mandatory and why the frontend talks to the gateway, never to a
backend directly.

### Asynchronous processing

Two capabilities are split into an **API** (accepts the request immediately) and
a **worker** (does the slow work in the background), connected by a queue:

- **Indexing** — uploading a document returns right away; a worker then parses,
  chunks, embeds, and stores it. The document becomes searchable once the worker
  finishes.
- **Evaluation** — requesting an evaluation returns right away; a worker then
  runs the scoring and writes the results back.

Indexing and evaluation use **separate queues** so their jobs never mix.

### Pluggable infrastructure

Every backend dependency is chosen by an environment variable and implemented in
the shared `dos-utility` package:

| Capability | Selector | Options |
|---|---|---|
| Authentication | `AUTH_PROVIDER` | AWS Cognito, Local (mock) |
| NoSQL database | `NOSQL_PROVIDER` | DynamoDB |
| Queue | `QUEUE_PROVIDER` | Redis, AWS SQS |
| Object storage | `STORAGE_PROVIDER` | MinIO, AWS S3 |
| Vector database | `VECTOR_DB_PROVIDER` | Qdrant, Redis |
| Tracing | `TRACING_PROVIDER` | Langfuse, None (default) |

The exact variables for each option live in **one place** —
[the dos-utility feature reference](../dos-utility/docs/features.md). Service-level
settings (models, masking, sessions, etc.) live in
[Configuration](./configuration.md).

## Authentication model

The gateway authenticates every protected request by calling the auth service,
which validates the caller's token and returns their identity (id + role). The
gateway then forwards that identity to the backends.

- **Local (default):** a mock provider for development and demos. The frontend's
  "Continue as User / Admin" buttons issue fake tokens. **It performs no real
  authentication — never use it in production.**
- **AWS Cognito:** the production-grade option. DOS68K validates Cognito-issued
  tokens but does **not** issue them — your users sign in through Cognito (or
  whatever you put in front of it), and you provision admin vs. user identities
  there.

## Things to watch (gotchas)

- **Embedding model and dimension must match everywhere.** The model and
  `EMBED_DIM` used to index documents must match those the chatbot uses to query,
  or retrieval returns irrelevant results. The defaults are already aligned;
  if you change one, change all. See [Configuration](./configuration.md#embedding-consistency).
- **New Indexes need a tool config + a chatbot restart** before the chatbot can
  use them (explained above).
- **Tracing is off by default** (`TRACING_PROVIDER` defaults to none). You get no
  observability until you configure Langfuse.
- **PII masking is opt-in** (`MASK_PII=false` by default).
- **Indexing and evaluation must stay on separate queues** — the bundled
  configuration already does this; keep it that way if you change queue settings.
</content>
</invoke>
