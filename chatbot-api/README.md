# Chatbot API

The core of DOS68K. It manages chat **Sessions** and **Queries**, and runs the
RAG agent that retrieves relevant passages from your **Indexes** and generates
grounded answers.

For the big picture, see [Overview](../docs/overview.md). For settings, see
[Configuration](../docs/configuration.md#chatbot).

## Role in the platform

When a User asks a question, this service:

1. Loads the conversation so far (the Session history).
2. Hands the question to the agent, which decides which **RAG tool** to use,
   retrieves the most relevant document chunks from the vector database, and
   writes an answer based **only** on what it retrieved.
3. Optionally masks PII in the question and answer (when enabled).
4. Returns the answer together with its **Sources** (the retrieved passages).
5. Stores the exchange in the Session.

It reads the indexes that the [indexing service](../chatbot-index/api/README.md)
populates; it does not ingest documents itself.

## What it can and can't do

- Answers strictly from retrieved content; it is instructed not to fall back on
  the model's own background knowledge, and to refuse out-of-scope or unsafe
  requests.
- Is a **ReAct agent**: it reasons in steps and decides when to invoke a RAG
  tool before answering. Because ReAct depends on the model following a strict
  reasoning format, the model is load-bearing — only `gemini-2.5-flash` is
  tested. See [Overview: limitations](../docs/overview.md#what-you-cannot-do-current-limitations).
- Uses **Google Gemini** for both reasoning and query embeddings — a Google API
  key (`MODEL_API_KEY`) is required.
- Can only retrieve from an Index that has a **Tool config** pointing at it (see
  [Customisation](#customisation)). Creating an Index alone is not enough.

## Sessions

A Session is one user's conversation thread. Sessions are **permanent** or
**temporary**; temporary Sessions automatically expire after
`SESSION_EXPIRATION_DAYS`. Each Query within a Session carries its answer, its
Sources, optional topic tags, a thumbs feedback value, and — once evaluated —
its quality [Scores](../chatbot-evaluate/api/README.md).

## Customisation

Two things are configurable without touching code.

### RAG tools (which Indexes the chatbot can use)

Each **RAG tool** binds the agent to one Index and tells it when to use that
Index. Tools are defined as YAML files in the tool-config directory
(`TOOLS_CONFIG_DIR`; the bundled setup mounts `scripts/tool_config/`). A tool
config specifies the `index_id` to query, the tool's `name` and `description`
(which the agent reasons over to decide when to use it), and optionally a
per-tool retrieval depth and custom retrieval prompts. The annotated schema is
in
[src/modules/chatbot/tool/config/template.yaml](./src/modules/chatbot/tool/config/template.yaml).

> Tool configs are read **only at startup**. After adding or changing one,
> restart this service (`docker compose restart chatbot-api`). Adding documents
> to an Index that already has a tool does **not** require a restart.

### Agent behaviour (the assistant's personality and guardrails)

The system prompt — the assistant's identity, tone, scope, refusal rules, and
grounding instructions — lives in a YAML file (`AGENT_CONFIG_PATH`; default
[src/modules/chatbot/agent/agent.yaml](./src/modules/chatbot/agent/agent.yaml)).
Edit it to change how the assistant introduces itself and what it will and won't
discuss.

## Sample data

For a quick end-to-end test, the bundled
[`scripts/populate_vector_db.py`](./scripts/populate_vector_db.py) seeds a small
demo corpus that matches the demo tool configs in `scripts/tool_config/`. See
[Getting started: verify with the demo data](../docs/getting-started.md#5-verify-with-the-demo-data).

## PII masking & observability

When `MASK_PII=true`, questions and answers are anonymised by the
[masking service](../masking/README.md) before being stored (off by default).
Every Query can also be traced to an observability backend; tracing is off by
default and never affects answering — see
[the tracing reference](../dos-utility/docs/features.md#8-tracing-interface).
</content>
