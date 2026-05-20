# DOS68K

DOS68K is a microservice RAG chatbot platform. End users query documents through a chat interface; admins ingest documents into per-tenant indexes that the chat retrieves from.

## Language

**Index**:
A named, isolated collection of ingested documents that the chatbot retrieves from. Created and owned by an admin.
_Avoid_: Knowledge base, corpus, collection

**Document**:
A file (`.pdf`, `.md`, `.txt`) uploaded into an **Index**. Processed asynchronously by the index worker into chunks and embeddings.
_Avoid_: File, doc, asset

**Session**:
A conversational thread between a user and the chatbot, identified by `sessionId` and persisted with a title. Holds an ordered series of **Queries**.
_Avoid_: Chat, conversation, thread

**Query**:
One question/answer turn within a **Session**. Carries the answer plus its **Sources**, auto-tagged topics, and a `badAnswer` flag.
_Avoid_: Message, prompt, exchange

**Sources**:
An ordered list of retrieved chunks returned alongside an answer. Each **Source** is one chunk (text + score + originating **Document** filename); the same **Document** may appear in multiple **Sources**. The canonical UI label for what the API returns as `context` on a `Query`.
_Avoid_: Citations, references, context (overloaded with LLM prompt context)

**Admin user** / **User**:
Two roles enforced server-side by `get_admin_user` / `get_user`. Admins manage **Indexes** and **Documents**; both roles can chat.
_Avoid_: Owner, tenant, member

### Observability

**Trace**:
The full execution record of one **Query**: prompt, retrieved context, tool calls, generation, latency, token usage. One Trace per Query, produced by `chatbot-api`, shipped to the configured Tracing Provider.
_Avoid_: log, event, metric (a Span is a part of a Trace — see below)

**Span**:
A timed sub-step within a **Trace** — has a name, start/end timestamps, optional input/output, and metadata. Two sources: *outer spans* recorded manually by `chatbot-api` around steps it owns (input sanitisation, PII masking, history load); *inner spans* auto-captured inside the LlamaIndex ReAct loop (retrieval, individual tool calls, LLM generation, embedding).
_Avoid_: step, phase, event (Span is the canonical term; an event has no duration, a Span does)

**Score**:
A named numeric measurement attached to a **Trace** — e.g. Ragas `faithfulness`, `answer_relevancy`. Produced by `chatbot-evaluate-worker`. Multiple Scores per Trace are expected.
_Avoid_: metric, KPI, rating (these are ambiguous — Score is the canonical term)

**Tracing Trace ID**:
The provider-agnostic identifier that links a **Query** row to its **Trace** in the configured Tracing Provider. Stored as `tracingTraceId` on the `queries` row. Used by `chatbot-evaluate-worker` to attach **Scores** to the right Trace.
_Avoid_: langfuse_id, observation_id, telemetry_id

**Tracing Provider**:
A `dos-utility` provider implementing `TracingInterface` (e.g. `LANGFUSE`). Selected at runtime via `TRACING_PROVIDER`. Implementations must not block the request path on network I/O, and must not surface tracing failures to the caller — every interface method swallows its own exceptions and logs them. A tracing fault degrades observability, never the request.
_Avoid_: monitoring backend, observability vendor (these are fine in prose, but `Tracing Provider` is the code-level term)

## Relationships

- An **Admin user** owns zero or more **Indexes**
- An **Index** contains zero or more **Documents**
- A **User** owns zero or more **Sessions**
- A **Session** contains zero or more **Queries**
- A **Query** has an ordered list of zero or more **Sources**, each pointing back to one **Document** (the same **Document** may be referenced by multiple **Sources**)

## Flagged ambiguities

- "context" was overloaded between the LLM prompt context window and the retrieved RAG chunks. The retrieved chunks are now called **Sources** in the UI; the API field name `context` is preserved for wire compatibility.
