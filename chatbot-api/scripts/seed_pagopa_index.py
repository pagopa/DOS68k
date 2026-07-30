#!/usr/bin/env python3
"""Seed a local Redis with an index shaped like the PagoPA DevPortal one.

Why this exists
---------------
``populate_vector_db.py`` writes JSON documents through ``put_objects`` and has
no ``url`` / ``title``. The production DevPortal index is different: documents
are **HASH**, with ``doc_id`` / ``text`` / ``url`` / ``title`` fields, and
``url`` / ``title`` are *not* indexed attributes. This script reproduces that
shape so the retrieval path (including the ``url`` / ``title`` return fields)
can be exercised locally.

Quick start
-----------
Run from the ``chatbot-api`` directory so its ``.venv`` is active.

    # No API key needed — deterministic fake vectors, enough to check the fields:
    uv run python scripts/seed_pagopa_index.py --fake-embeddings

    # Real embeddings, so semantic search actually matches the question:
    uv run python scripts/seed_pagopa_index.py --google-api-key "$GOOGLE_API_KEY"

Flags & env vars
----------------
    --host HOST              Redis host. Default: localhost (matches compose).
    --port PORT              Redis port. Default: 6379.
    --index NAME             Index name. Default: devportal-index (matches
                             index_id in tool/config/devportal.yaml).
    --dim INT                Vector dim. Must match chatbot-api's EMBED_DIM.
                             Default: 768.
    --fake-embeddings        Skip the embedding API: deterministic vectors
                             derived from the text. Retrieval returns the same
                             chunks for every question, which is fine to verify
                             that url/title flow through.
    --google-api-key KEY     Falls back to GOOGLE_API_KEY. Required unless
                             --fake-embeddings.
    --embed-model ID         Default: gemini-embedding-001 (must match
                             chatbot-api's EMBED_MODEL_ID).
    --drop                   Drop the index and its documents before seeding.
"""

import argparse
import hashlib
import os
import struct
import sys
import uuid
from typing import List

import redis

# Chunks mirroring real DevPortal pages: what matters here is that each one
# carries a title and a url, like the production documents do.
DOCUMENTS: List[dict] = [
    {
        "doc_id": "it/devportal-docs/docs/pdnd-interoperabilita/primo-accesso",
        "title": "First access and initial configuration",
        "url": "https://developer.pagopa.it/pdnd-interoperabilita/guides/manuale-operativo/primo-accesso",
        "text": (
            "Detailed procedures for creating and revoking the operator users of an "
            "institution on PDND Interoperabilità. The legal representative completes "
            "the first access, then assigns the admin role to the operators who will "
            "manage e-services and API keys."
        ),
    },
    {
        "doc_id": "it/devportal-docs/docs/firma-con-io/guida-scelta-firma",
        "title": "Guida alla scelta di Firma con IO",
        "url": "https://developer.pagopa.it/firma-con-io/guides/guida-scelta-firma",
        "text": (
            "Firma con IO è una Firma Elettronica Qualificata one shot con il massimo "
            "valore legale, pari alla firma autografa. Consente ai cittadini di firmare "
            "documenti tramite l'App IO e agli enti di gestire il processo di firma da "
            "un unico canale."
        ),
    },
    {
        "doc_id": "it/devportal-docs/docs/solutions/riscossione-della-tari",
        "title": "Riscossione della TARI",
        "url": "https://developer.pagopa.it/solutions/riscossione-della-tari/details",
        "text": (
            "Per riscuotere la TARI un ente può integrare pagoPA e SEND: i cittadini "
            "ricevono gli avvisi di pagamento sull'app IO, possono salvare i metodi di "
            "pagamento e pagare la prima rata o la rata unica direttamente in app."
        ),
    },
    {
        "doc_id": "it/devportal-docs/docs/send/onboarding-enti",
        "title": "SEND – Onboarding degli enti",
        "url": "https://developer.pagopa.it/send/guides/onboarding",
        "text": (
            "L'onboarding di un ente su SEND richiede l'adesione tramite l'Area "
            "Riservata, la nomina del referente tecnico e la generazione delle API key "
            "per gli ambienti di test e produzione."
        ),
    },
]


def fake_embedding(text: str, dim: int) -> List[float]:
    """Deterministic pseudo-vector derived from the text (no API call)."""
    digest = hashlib.sha256(text.encode()).digest()
    return [(digest[i % len(digest)] / 255.0) - 0.5 for i in range(dim)]


def real_embeddings(
    texts: List[str], model: str, api_key: str, dim: int
) -> List[List[float]]:
    """Embed with the same model chatbot-api uses, so vectors are comparable."""
    from google.genai import types
    from llama_index.embeddings.google_genai import GoogleGenAIEmbedding

    embed_model = GoogleGenAIEmbedding(
        model_name=model,
        api_key=api_key,
        embedding_config=types.EmbedContentConfig(output_dimensionality=dim),
    )
    return embed_model.get_text_embedding_batch(texts)


def to_bytes(vector: List[float]) -> bytes:
    return struct.pack(f"{len(vector)}f", *vector)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default=os.getenv("REDIS_HOST", "localhost"))
    parser.add_argument(
        "--port", type=int, default=int(os.getenv("REDIS_PORT", "6379"))
    )
    parser.add_argument("--index", default="devportal-index")
    parser.add_argument("--dim", type=int, default=int(os.getenv("EMBED_DIM", "768")))
    parser.add_argument("--fake-embeddings", action="store_true")
    parser.add_argument("--google-api-key", default=os.getenv("GOOGLE_API_KEY"))
    parser.add_argument("--embed-model", default="gemini-embedding-001")
    parser.add_argument("--drop", action="store_true")
    args = parser.parse_args()

    if not args.fake_embeddings and not args.google_api_key:
        print(
            "A Google API key is required for real embeddings "
            "(--google-api-key / GOOGLE_API_KEY), or pass --fake-embeddings.",
            file=sys.stderr,
        )
        return 1

    client = redis.Redis(host=args.host, port=args.port, decode_responses=False)
    prefix = f"{args.index}/vector"

    if args.drop:
        try:
            client.execute_command("FT.DROPINDEX", args.index, "DD")
            print(f"Dropped index '{args.index}' and its documents")
        except redis.ResponseError as e:
            print(f"Nothing to drop: {e}")

    # ON HASH, like production. url and title are stored but NOT indexed: they
    # are still readable through the RETURN clause of a search.
    try:
        client.execute_command(
            "FT.CREATE",
            args.index,
            "ON",
            "HASH",
            "PREFIX",
            "1",
            f"{prefix}:",
            "SCHEMA",
            "id",
            "TAG",
            "doc_id",
            "TAG",
            "text",
            "TEXT",
            "vector",
            "VECTOR",
            "FLAT",
            "6",
            "TYPE",
            "FLOAT32",
            "DIM",
            str(args.dim),
            "DISTANCE_METRIC",
            "COSINE",
        )
        print(
            f"Created index '{args.index}' (ON HASH, prefix '{prefix}:', dim {args.dim})"
        )
    except redis.ResponseError as e:
        if "Index already exists" not in str(e):
            raise
        print(f"Index '{args.index}' already exists, reusing it")

    texts = [document["text"] for document in DOCUMENTS]
    if args.fake_embeddings:
        vectors = [fake_embedding(text, args.dim) for text in texts]
        print(f"Using deterministic fake vectors (dim {args.dim})")
    else:
        vectors = real_embeddings(
            texts, args.embed_model, args.google_api_key, args.dim
        )
        print(f"Embedded {len(vectors)} chunks with {args.embed_model}")

    for document, vector in zip(DOCUMENTS, vectors):
        chunk_id = str(uuid.uuid5(uuid.NAMESPACE_URL, document["url"]))
        client.hset(
            f"{prefix}:{chunk_id}",
            mapping={
                "id": chunk_id,
                "doc_id": document["doc_id"],
                "text": document["text"],
                "url": document["url"],
                "title": document["title"],
                "language": "it",
                "vector": to_bytes(vector),
            },
        )
        print(f"  + {document['title']} → {document['url']}")

    info = client.execute_command("FT.INFO", args.index)
    num_docs = info[info.index(b"num_docs") + 1]
    print(f"\nIndex '{args.index}' now holds {num_docs} documents.")
    print(
        "Make sure a RAG tool config points at this index "
        f"(index_id: {args.index}) and that EMBED_DIM={args.dim} in chatbot-api's .env."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
