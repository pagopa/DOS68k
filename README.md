# DOS68k

DOS68k is a modular, microservice-based platform that provides a RAG-powered chatbot with document indexing, PII masking, evaluation, and authentication capabilities.

## Services

| Service | Path | Description |
|---|---|---|
| Chatbot API | [chatbot-api](./chatbot-api/README.md) | Core chatbot service. Manages user sessions and queries, generates answers via LLM |
| Chatbot Evaluate API | [chatbot-evaluate/api](./chatbot-evaluate/api/README.md) | Accepts evaluation requests and dispatches them to the evaluate worker via queue |
| Chatbot Evaluate Worker | [chatbot-evaluate/worker](./chatbot-evaluate/worker/README.md) | Processes evaluation jobs consumed from the queue |
| Chatbot Index API | [chatbot-index/api](./chatbot-index/api/README.md) | Accepts document indexing requests and dispatches them to the index worker via queue |
| Chatbot Index Worker | [chatbot-index/worker](./chatbot-index/worker/README.md) | Processes indexing jobs consumed from the queue, interacts with external storage |
| Auth | [auth](./auth/README.md) | Authentication and authorization service. Supports AWS Cognito, Keycloak, and local development mode |
| Masking | [masking](./masking/README.md) | PII detection and masking service powered by Microsoft Presidio and spaCy |
| DOS Utility | [dos-utility](./dos-utility/README.md) | Shared internal package providing common abstractions (auth, queue, storage, NoSQL, vector DB). Not a standalone service — used as a dependency by all other services |

## Customization

The chatbot agent can be fully customized without modifying source code:

- **RAG tools** — Define custom tools as YAML config files and mount them into the `chatbot-api` container. See [Custom RAG tools](./chatbot-api/README.md#custom-rag-tools).
- **Agent configuration** — Override the agent's identity and behavior by providing a custom `agent.yaml`. See [Custom agent configuration](./chatbot-api/README.md#custom-agent-configuration).
- **Test data** — A populate script seeds the vector DB with sample documents for end-to-end testing. See [Populate vector DB](./chatbot-api/README.md#populate-vector-db).

## Documentation

- [Build & setup guide](./docs/build.md)
- [Licenses](./docs/licenses.md)
