# Chatbot Index Worker

The background engine that turns uploaded **Documents** into searchable content.
It runs continuously, with no public interface.

For the big picture, see [Overview](../../docs/overview.md). For settings, see
[Configuration](../../docs/configuration.md#document-indexing--worker).

## Role in the platform

The worker consumes indexing jobs placed on the queue by the
[index API](../api/README.md). For each Document it:

1. Downloads the file from object storage.
2. Extracts its text and splits it into chunks.
3. Generates a vector embedding for each chunk (via **Google Gemini**).
4. Writes the chunks into the Index in the vector database.

When a Document is re-indexed, the worker replaces the old chunks with the new
ones. This is why a Google API key (`MODEL_API_KEY`) is required for the worker.

## Supported documents

| Format | Notes |
|---|---|
| PDF | Text extracted page by page |
| Markdown | |
| Plain text | |

## What to watch

- The worker's **embedding model and `EMBED_DIM` must match the chatbot's**, or
  retrieval will return irrelevant results. See
  [Configuration: embedding consistency](../../docs/configuration.md#embedding-consistency).
- The worker must read from the **same storage bucket** the API writes to
  (`INDEX_DOCUMENTS_BUCKET_NAME`) and the **same queue** the API publishes to.
  The bundled templates already line these up.
</content>
