# DOS68K

Shared language for the DOS68K platform — a plug 'n play, microservice RAG chatbot. Terms below are the ones that recur across services and have caused ambiguity; general programming concepts are intentionally omitted.

## Language

### Conversation

**Session**:
A bounded conversation between a user and the chatbot, owned by exactly one user.
_Avoid_: chat, thread, conversation

**Query**:
A single turn within a Session — one user question and the chatbot's answer, together with the retrieved context and topic tags. Persisted as one row in the `queries` NoSQL table.
_Avoid_: message, exchange, turn

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

- A **Session** contains one or more **Queries**.
- A **Query** has exactly one **Trace**, linked by **Tracing Trace ID**.
- A **Trace** has zero or more **Scores**.
- `chatbot-api` produces **Traces**. `chatbot-evaluate-worker` produces **Scores**. Both write through the same **Tracing Provider**.

## Example dialogue

> **Dev:** "When a user sends a question, do we wait for the **Trace** to be shipped before responding?"
> **Maintainer:** "No — the **Tracing Provider** is contractually non-blocking. The SDK buffers in-process and ships in the background. The response goes out as soon as the **Query** is persisted with its **Tracing Trace ID**."
>
> **Dev:** "And the Ragas numbers — those are **Scores**?"
> **Maintainer:** "Right. `chatbot-evaluate-worker` runs Ragas off a queued task and calls `tracer.score(tracing_trace_id, ...)`. They show up under the same **Trace** in the dashboard, so the admin sees prompt, answer, latency, and faithfulness together."

## Flagged ambiguities

- **"Metrics"** was used loosely early on to mean three different things (Prometheus-style aggregates, discrete events, and LLM traces). Resolved: in DOS68K, the observability data we ship is **Traces** (with nested spans) and **Scores** attached to them — *not* Prometheus-style metrics. If aggregate metrics are ever introduced, they need a distinct term.
- **"Monitoring service"** was used early to mean both the external sink (Langfuse) and a hypothetical internal ingest service. Resolved: the sink is the **Tracing Provider**; there is no internal ingest service — `chatbot-api` and `chatbot-evaluate-worker` write directly via the provider in-process.
