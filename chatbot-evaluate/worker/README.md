# Chatbot Evaluate Worker

The background engine that scores answer quality. It runs continuously, with no
public interface.

For the big picture, see [Overview](../../docs/overview.md). For settings, see
[Configuration](../../docs/configuration.md#evaluation--worker).

## Role in the platform

The worker consumes evaluation jobs placed on the queue by the
[evaluate API](../api/README.md). For each answer it:

1. Reconstructs the conversation up to that answer and, for follow-up questions,
   rewrites the question into a standalone form.
2. Runs [RAGAS](https://docs.ragas.io/) scoring, using **Google Gemini** as the
   judge model.
3. Writes the resulting **Scores** back onto the Query record.

It computes three Scores per answer:

| Score | What it measures |
|---|---|
| **Faithfulness** | Whether the answer is supported by the retrieved Sources (no hallucination). |
| **Answer relevancy** | How well the answer addresses the question. |
| **Context utilisation** | How well the retrieved Sources were actually used. |

A Google API key (`MODEL_API_KEY`) is required, since scoring calls the model.

## What to watch

- Evaluation runs on its **own queue**, separate from document indexing — see
  [Configuration: queue separation](../../docs/configuration.md#queue-separation).
- The worker reads Queries from the **same NoSQL tables** the chatbot writes;
  keep the table names aligned — see
  [Configuration: shared table names](../../docs/configuration.md#shared-table-names).
</content>
