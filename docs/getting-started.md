# Getting started

This guide takes you from nothing to a running DOS68K with a working chatbot. If
you have never seen the project, follow it top to bottom. For what the platform
is and its limitations, read [Overview](./overview.md) first.

The fastest way to *see it work* is the bundled demo data
([Verify with the demo data](#5-verify-with-the-demo-data)). Using **your own**
documents takes a couple more steps
([Use your own documents](#6-use-your-own-documents)).

## 1. Prerequisites

- **Docker** and **Docker Compose** (v2).
- **A Google (Gemini) API key.** This is mandatory — Google is the only wired
  model provider, used for both answering and embeddings. Get one from
  [Google AI Studio](https://aistudio.google.com/).
- *(Optional, only for the demo-data smoke test below)* **[uv](https://docs.astral.sh/uv/)**,
  to run the seeding script on your machine.

The default setup runs everything locally in containers — DynamoDB, queue,
storage, and vector database are all emulated, so you need no cloud account to
start. The bundled emulator stack uses [LocalStack](https://localstack.cloud/);
the example `.env.localstack` includes a placeholder `LOCALSTACK_AUTH_TOKEN`
which the default services (DynamoDB/S3/SQS) do not require.

## 2. Choose your providers (optional)

DOS68K can run on different infrastructure backends, selected per capability by
environment variable. **The defaults below work out of the box** with the
bundled `compose.yaml`, so you can skip this section on a first run and come
back when you want to point at real infrastructure.

| Capability | Default | Alternatives |
|---|---|---|
| Authentication | Local mock | AWS Cognito |
| NoSQL database | DynamoDB (LocalStack) | — |
| Queue | Redis | AWS SQS |
| Object storage | MinIO | AWS S3 |
| Vector database | Redis | Qdrant |
| Tracing | None | Langfuse |

To change any of these, see the provider variables in
[the dos-utility feature reference](../dos-utility/docs/features.md), and adjust
the matching service `.env` file in the next step. **Non-default backends
(Qdrant, the Langfuse tracing stack, the `dynamodb-admin` debug UI) are kept in
`compose.yaml` but commented out**, so what runs by default matches what is
configured — uncomment the relevant block(s) when you switch a provider. The
top of `compose.yaml` explains exactly what to uncomment for each option.

## 3. Configure environment files

Each service ships an `.env.template`. Copy each one to `.env` in the same
directory and fill in the values. The same applies to the root-level
`.env.*.template` files used by the bundled infrastructure.

```bash
# Service env files
cp auth/.env.template                  auth/.env
cp chatbot-api/.env.template           chatbot-api/.env
cp chatbot-index/api/.env.template     chatbot-index/api/.env
cp chatbot-index/worker/.env.template  chatbot-index/worker/.env
cp chatbot-evaluate/api/.env.template  chatbot-evaluate/api/.env
cp chatbot-evaluate/worker/.env.template chatbot-evaluate/worker/.env

# Root infrastructure env files (defaults)
cp .env.storage.template    .env.storage
cp .env.localstack.template .env.localstack

# Optional — only needed when you enable the Langfuse tracing stack in compose.yaml:
# cp .env.database.template .env.database
# cp .env.langfuse.template .env.langfuse
```

Then set your **Google API key** (`MODEL_API_KEY`) in the three services that
call Google:

- `chatbot-api/.env`
- `chatbot-index/worker/.env`
- `chatbot-evaluate/worker/.env`

The template defaults are otherwise ready for local use. For the meaning of
every service variable, see [Configuration](./configuration.md); for the
infrastructure/provider variables, see
[the dos-utility feature reference](../dos-utility/docs/features.md).

> **Note on the frontend:** under `compose.yaml` the frontend's API URL is set
> for you (it points at the gateway on port `8080`). You do not need a frontend
> `.env` for the bundled setup.

## 4. Start the platform

`compose.yaml` builds every service from source and starts the bundled
infrastructure. From the repository root:

```bash
docker compose up -d --build
```

Bring up **all** services (don't pass a single service name) — this ensures the
one-shot `minio-init` job runs and creates the document storage bucket.

Once everything is healthy:

| What | URL |
|---|---|
| Frontend (demo UI) | http://localhost |
| API gateway | http://localhost:8080 |
| MinIO console | http://localhost:9001 |
| Langfuse | http://localhost:4001 (only when the Langfuse stack is enabled — see [section 2](#2-choose-your-providers-optional)) |

> **Using prebuilt images instead of building from source:** the repository also
> ships `compose-remote.yaml`, which pulls published images rather than building
> them. Use `docker compose -f compose-remote.yaml up -d` in place of the command
> above.

## 5. Verify with the demo data

DOS68K ships a small sample corpus and matching tool configuration so you can
confirm the whole pipeline works before bringing your own documents. The bundled
`compose.yaml` already mounts demo tool configs for three indexes —
`software-dev`, `zephyr-corp`, and `borgonero-fc` — so the chatbot is ready to
answer about them as soon as they contain data.

Seed the data with the bundled script (run on your machine, requires `uv`):

```bash
cd chatbot-api
uv sync
uv run python scripts/populate_vector_db.py --provider redis --topic all --google-api-key <YOUR_GOOGLE_API_KEY>
```

This embeds the sample documents (with the same model the chatbot queries with)
and loads them into the vector database. You do **not** need to restart anything
— the chatbot retrieves live, so the seeded data is searchable on the next
question.

Now open http://localhost, click **Continue as User**, and ask something like
*"What is a REST API?"* or *"What is Borgonero FC's home stadium?"*. You should
get an answer with its **Sources** listed.

> This script is a smoke test only. It writes embeddings straight into the vector
> database, bypassing the normal upload pipeline. For real content, use the
> workflow below.

## 6. Use your own documents

This is the real workflow. There is one step that is easy to miss — **a new
Index is not answerable until a tool config points at it and the chatbot
restarts** — so follow all five steps.

1. **Log in as Admin.** Open http://localhost and click **Continue as Admin**
   (with the default local auth). You land on the admin panel.
2. **Create an Index.** In the admin panel, create a new Index (e.g.
   `handbook`). An Index is an isolated collection of documents.
3. **Upload Documents.** Drag and drop `.pdf`, `.md`, or `.txt` files into the
   Index. Uploading is asynchronous: the file is accepted immediately and a
   background worker parses, chunks, and embeds it. It becomes searchable once
   the worker finishes (watch the worker logs if you want to confirm).
4. **Register a tool config for the Index.** The chatbot only retrieves from an
   Index that has a **Tool config** referencing it. Create a YAML file whose
   `index_id` matches your Index name, describing when the assistant should use
   it. Place it in the chatbot's tool-config directory — under the bundled
   setup that directory is mounted from `chatbot-api/scripts/tool_config/`, so
   drop your file there (you can remove the demo configs). The schema and an
   annotated example live in
   [chatbot-api/src/modules/chatbot/tool/config/template.yaml](../chatbot-api/src/modules/chatbot/tool/config/template.yaml).
   A minimal example:

   ```yaml
   index_id: handbook
   name: HandbookTool
   description: >
     RAG tool that retrieves information from the company handbook.
     Use this tool when the user asks about company policies, processes,
     or internal guidelines.
   ```

5. **Restart the chatbot** so it loads the new tool config:

   ```bash
   docker compose restart chatbot-api
   ```

Now log in as a User and ask a question about your documents.

> You only need to repeat steps 4–5 when you **add or change a tool config**.
> Adding more documents to an *existing* Index (step 3) is picked up
> automatically — no restart needed.

## Next steps

- **Tune the assistant.** Edit the agent's system prompt and behaviour — see
  [chatbot-api](../chatbot-api/README.md#customisation).
- **Turn on observability.** Configure Langfuse tracing — see
  [the tracing reference](../dos-utility/docs/features.md#8-tracing-interface).
- **Turn on PII masking.** Set `MASK_PII=true` — see
  [Configuration](./configuration.md#chatbot) and [masking](../masking/README.md).
- **Measure answer quality.** See [evaluation](../chatbot-evaluate/api/README.md).
- **Go to production.** Replace the mock auth with AWS Cognito and point storage,
  queue, and databases at real infrastructure — see
  [Overview: authentication model](./overview.md#authentication-model) and the
  [provider reference](../dos-utility/docs/features.md).
</content>
