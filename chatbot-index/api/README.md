# Chatbot Index API

The document management entry point for DOS68K. Admins use it to create and
delete **Indexes** and to upload, list, and delete **Documents** within them.

For the big picture, see [Overview](../../docs/overview.md). For settings, see
[Configuration](../../docs/configuration.md#document-indexing--api).

## Role in the platform

This service is the front door for getting content into the platform. When an
Admin uploads a Document, it:

1. Stores the file in object storage.
2. Places a job on the indexing queue.

It then returns immediately — the actual processing (parsing, chunking,
embedding) is done in the background by the
[index worker](../worker/README.md). A Document becomes searchable once the
worker finishes.

Deleting a Document or an Index also removes the corresponding files from
storage and the corresponding vectors from the vector database.

## What it can and can't do

- Accepts **PDF, Markdown, and plain-text** files only; other formats are
  rejected.
- All operations are **Admin-only**.
- Creating an Index here makes it available for documents, but does **not** make
  it answerable by the chatbot on its own — the chatbot also needs a **Tool
  config** for that Index (see
  [chatbot-api](../../chatbot-api/README.md#customisation)).

## Storage bucket

Uploaded files live in the object-storage bucket named by
`INDEX_DOCUMENTS_BUCKET_NAME`. This must match the worker's value and the bucket
must exist; the bundled `compose.yaml` provisions it automatically via a
one-shot `minio-init` job, so no manual bucket creation is needed for the
default setup.
</content>
