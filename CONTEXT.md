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

## Relationships

- An **Admin user** owns zero or more **Indexes**
- An **Index** contains zero or more **Documents**
- A **User** owns zero or more **Sessions**
- A **Session** contains zero or more **Queries**
- A **Query** has an ordered list of zero or more **Sources**, each pointing back to one **Document** (the same **Document** may be referenced by multiple **Sources**)

## Flagged ambiguities

- "context" was overloaded between the LLM prompt context window and the retrieved RAG chunks. The retrieved chunks are now called **Sources** in the UI; the API field name `context` is preserved for wire compatibility.
