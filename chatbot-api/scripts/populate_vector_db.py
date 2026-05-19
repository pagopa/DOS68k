#!/usr/bin/env python3
"""Populate the vector database with sample documents for quick chatbot testing.

What it does
------------
Inserts a small set of curated documents — grouped into topics like
``software-dev``, ``zephyr-corp``, ``borgonero-fc`` — into the configured
vector store (Redis or Qdrant). Each topic becomes one index that the
chatbot-api agent can later query via a RAG tool. Embeddings are produced
by Google GenAI (``gemini-embedding-001`` — must match chatbot-api's
EMBED_MODEL_ID) — a Google API key is required.

Quick start
-----------
Run from the ``chatbot-api`` directory so its ``.venv`` is active.

    # Interactive wizard (recommended) — prompts for everything:
    uv run python scripts/populate_vector_db.py

    # Fully scripted — every flag pre-filled, no prompts:
    uv run python scripts/populate_vector_db.py --provider redis --topic all

    # Ollama (uncomment the qdrant service in compose.yaml first)
    uv run python scripts/populate_vector_db.py --provider qdrant --embed-provider ollama

Flags & env vars
----------------
    --provider {redis,qdrant}        Vector DB to populate. Prompted if omitted.
    --topic {<topic>,all}            Topic to populate. Default: all.
    --embed-provider {google|ollama} Embedding source. Only google for now.
    --embed-dim INT                  Vector dim, must match EMBED_DIM. Default: 768.
    --host HOST                      Override REDIS_HOST / QDRANT_HOST.
                                     Defaults to localhost (matches compose).
    --port PORT                      Override REDIS_PORT / QDRANT_PORT.
                                     Defaults to 6379 (redis) / 6333 (qdrant).
    --google-api-key KEY             Required. Falls back to GOOGLE_API_KEY env var.

After running, add a YAML config file in
``chatbot-api/src/modules/chatbot/tool/config/`` (or the directory pointed
to by ``TOOLS_CONFIG_DIR``) for each index you populated. See
``src/modules/chatbot/tool/config/template.yaml`` for the schema.
"""

import argparse
import asyncio
import os
import sys

import questionary
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

# ---------------------------------------------------------------------------
# Topics
# ---------------------------------------------------------------------------

TOPICS: dict[str, list[dict]] = {
    "software-dev": [
        {
            "filename": "rest_api.md",
            "chunk_id": 0,
            "content": (
                "A REST API (Representational State Transfer) is an architectural style for "
                "building web services. It uses standard HTTP methods such as GET, POST, PUT, "
                "PATCH, and DELETE to perform CRUD operations on resources identified by URLs. "
                "REST APIs are stateless: each request contains all the information needed to "
                "process it, without relying on server-side session state."
            ),
        },
        {
            "filename": "rest_api.md",
            "chunk_id": 1,
            "content": (
                "REST API best practices include: using nouns for resource names (e.g. /users "
                "instead of /getUsers), returning appropriate HTTP status codes (200 OK, 201 "
                "Created, 404 Not Found, 400 Bad Request), versioning the API via the URL path "
                "(e.g. /v1/users), and using JSON as the default content type."
            ),
        },
        {
            "filename": "docker.md",
            "chunk_id": 0,
            "content": (
                "Docker is a platform for building, shipping, and running applications inside "
                "lightweight containers. A container packages an application together with its "
                "dependencies and runtime, ensuring consistent behaviour across development, "
                "staging, and production environments."
            ),
        },
        {
            "filename": "docker.md",
            "chunk_id": 1,
            "content": (
                "A Dockerfile defines how to build a Docker image. Key instructions include "
                "FROM (base image), COPY (copy files into the image), RUN (execute commands "
                "during the build), EXPOSE (document the port the app listens on), and CMD or "
                "ENTRYPOINT (specify the default command to run when the container starts)."
            ),
        },
        {
            "filename": "docker.md",
            "chunk_id": 2,
            "content": (
                "Docker Compose is a tool for defining and running multi-container applications. "
                "A compose.yaml file declares services, their images or build contexts, "
                "environment variables, ports, volumes, and inter-service dependencies. "
                "Run 'docker compose up' to start all services and 'docker compose down' to "
                "stop and remove them."
            ),
        },
        {
            "filename": "python_async.md",
            "chunk_id": 0,
            "content": (
                "Python's asyncio library enables writing concurrent code using the async/await "
                "syntax. An async function (coroutine) is defined with 'async def' and suspended "
                "with 'await'. The event loop schedules and runs coroutines cooperatively, making "
                "asyncio ideal for I/O-bound workloads such as network requests and database calls."
            ),
        },
        {
            "filename": "python_async.md",
            "chunk_id": 1,
            "content": (
                "asyncio.gather() runs multiple coroutines concurrently and returns their results "
                "as a list. asyncio.run() is the top-level entry point that creates an event loop, "
                "runs the given coroutine to completion, and closes the loop. For long-running "
                "servers, the loop is typically managed by the framework (e.g. FastAPI, aiohttp)."
            ),
        },
        {
            "filename": "fastapi.md",
            "chunk_id": 0,
            "content": (
                "FastAPI is a modern, high-performance Python web framework for building APIs. "
                "It is based on standard Python type hints and uses Pydantic for data validation. "
                "FastAPI automatically generates interactive OpenAPI documentation (Swagger UI) "
                "and ReDoc pages from your route definitions."
            ),
        },
        {
            "filename": "fastapi.md",
            "chunk_id": 1,
            "content": (
                "Dependency injection in FastAPI is handled with the Depends() function. "
                "Dependencies can be plain functions, async functions, or classes. They are "
                "executed before the route handler and their return values are injected as "
                "parameters. This pattern is commonly used for database sessions, authentication, "
                "and shared configuration."
            ),
        },
        {
            "filename": "vector_databases.md",
            "chunk_id": 0,
            "content": (
                "A vector database stores high-dimensional embedding vectors and supports "
                "approximate nearest-neighbour (ANN) search. Unlike relational databases, "
                "vector databases retrieve documents by semantic similarity rather than exact "
                "keyword matching. Common algorithms include HNSW (Hierarchical Navigable Small "
                "World) and IVF (Inverted File Index)."
            ),
        },
        {
            "filename": "vector_databases.md",
            "chunk_id": 1,
            "content": (
                "Qdrant is an open-source vector database written in Rust. It supports named "
                "vector fields, payload filtering, and on-disk storage. Collections in Qdrant "
                "are equivalent to indexes; each point consists of a vector, an optional "
                "payload (arbitrary JSON), and a unique ID."
            ),
        },
        {
            "filename": "vector_databases.md",
            "chunk_id": 2,
            "content": (
                "Redis Stack extends Redis with the RediSearch module, enabling vector similarity "
                "search directly inside Redis. Indexes are defined with a schema that declares "
                "the vector field dimensions and distance metric (COSINE, L2, or IP). "
                "The redisvl library provides a Python client for creating schemas and running "
                "vector queries against Redis."
            ),
        },
        {
            "filename": "llm_rag.md",
            "chunk_id": 0,
            "content": (
                "Retrieval-Augmented Generation (RAG) is a technique that augments large language "
                "model (LLM) responses with relevant documents retrieved from a knowledge base. "
                "A RAG pipeline typically involves: (1) embedding the user query, (2) searching "
                "a vector store for the most similar document chunks, (3) injecting the retrieved "
                "chunks into the LLM prompt as context, and (4) generating the final answer."
            ),
        },
        {
            "filename": "llm_rag.md",
            "chunk_id": 1,
            "content": (
                "LlamaIndex is a Python framework that simplifies building RAG applications on "
                "top of LLMs. It provides abstractions for document ingestion, chunking, "
                "embedding, vector store integration, query engines, and agents. The "
                "VectorStoreIndex class wraps any BasePydanticVectorStore implementation and "
                "exposes it as a retriever or query engine."
            ),
        },
        {
            "filename": "pydantic.md",
            "chunk_id": 0,
            "content": (
                "Pydantic is a Python library for data validation using Python type annotations. "
                "Models are defined as subclasses of BaseModel. Pydantic v2 uses a Rust-based "
                "core for fast validation and serialisation. PrivateAttr() declares private "
                "instance attributes that are excluded from the model schema and serialisation, "
                "and are typically used for runtime state such as database connections."
            ),
        },
    ],
    "zephyr-corp": [
        {
            "filename": "onboarding.md",
            "chunk_id": 0,
            "content": (
                "Zephyr Corp runs a structured 3-week onboarding programme called 'Project Ignite' "
                "for all new hires. Week 1 is dedicated to company orientation: new employees "
                "receive a welcome kit (including a branded Zephyr Corp mechanical keyboard and a "
                "€50 Notion credits voucher), complete mandatory security and GDPR training on the "
                "internal LMS platform ZephyrLearn, and attend a live 90-minute session with the "
                "People & Culture team. Week 2 is team immersion: the new hire shadows their squad "
                "lead for two days, completes tool setup for Linear (project tracking), Slack "
                "(communication), and Notion (documentation), and submits their first 30-60-90 day "
                "plan for manager review by end of day Friday."
            ),
        },
        {
            "filename": "onboarding.md",
            "chunk_id": 1,
            "content": (
                "Week 3 of Project Ignite focuses on independent contribution. Each new hire is "
                "assigned a dedicated onboarding buddy — a colleague from a different team who has "
                "been at Zephyr Corp for at least 12 months and has completed the internal Buddy "
                "Certification Workshop (BCW-2). The buddy holds three structured 45-minute check-in "
                "calls during weeks 1–3, is available on Slack for ad-hoc questions, and submits a "
                "brief buddy feedback form to People & Culture at the end of week 3. New hires who "
                "have not completed all ZephyrLearn modules by the end of week 3 will have their "
                "Notion workspace access restricted until completion."
            ),
        },
        {
            "filename": "leave_policy.md",
            "chunk_id": 0,
            "content": (
                "All full-time Zephyr Corp employees accrue 28 days of annual leave per calendar "
                "year, prorated for partial years. In addition, employees receive 3 'ZephyrDays' "
                "per year — fully discretionary paid days that can be used for personal wellness, "
                "volunteering, or any purpose without requiring manager approval or documentation. "
                "ZephyrDays do not carry over to the following year and must be booked through the "
                "HR portal (ZephyrPeople) at least 48 hours in advance. Annual leave requests of "
                "5 or more consecutive working days require manager approval at least 15 calendar "
                "days before the leave start date."
            ),
        },
        {
            "filename": "leave_policy.md",
            "chunk_id": 1,
            "content": (
                "Zephyr Corp offers 10 days of paid sick leave per rolling 12-month period. "
                "Absences of more than 3 consecutive days require a medical certificate uploaded "
                "to ZephyrPeople within 5 working days of returning to work. For parental leave, "
                "Zephyr Corp provides 20 weeks of fully paid leave for the primary caregiver, "
                "regardless of gender or the nature of parental responsibility (birth, adoption, "
                "or surrogacy). Secondary caregivers receive 6 weeks of fully paid leave. Both "
                "allowances are available from the employee's first day of employment and are not "
                "subject to length-of-service thresholds. Parental leave must be notified to "
                "People & Culture at least 8 weeks before the intended start date."
            ),
        },
        {
            "filename": "remote_work.md",
            "chunk_id": 0,
            "content": (
                "Zephyr Corp is a fully remote-first company. All employees are expected to work "
                "from their own home or a co-working space of their choice. The company does not "
                "maintain permanent offices; instead, it operates two hub locations — Milan (Via "
                "Tortona 37, 20144) and Lisbon (Rua Rodrigues Faria 103, 1300-501) — which are "
                "used exclusively for quarterly on-site weeks. On-site weeks are scheduled four "
                "times per year (typically the second week of March, June, September, and December) "
                "and attendance is mandatory for all employees whose role is classified as 'Core' "
                "in ZephyrPeople. Travel and accommodation costs for on-site weeks are covered in "
                "full by the company and do not count against the employee's personal expense "
                "budget. Each employee receives an annual home office stipend of €600, paid in "
                "January, to cover equipment, internet upgrades, or ergonomic furniture. The "
                "stipend is taxable and appears on the January payslip."
            ),
        },
        {
            "filename": "expense_policy.md",
            "chunk_id": 0,
            "content": (
                "Zephyr Corp employees may incur business expenses within the following approval "
                "tiers. Expenses up to €150 (inclusive) per transaction are self-approved: the "
                "employee submits the receipt through the Zephyr Wallet app within 30 calendar "
                "days of the purchase and the amount is reimbursed in the next payroll run. "
                "Expenses between €150.01 and €500 require line-manager approval before purchase "
                "whenever possible, or within 5 working days after purchase in urgent cases; "
                "submit via Zephyr Wallet with the manager tagged for digital sign-off. Expenses "
                "above €500 require VP-level approval (VP of Finance or the employee's divisional "
                "VP) prior to the purchase; retroactive approval for amounts above €500 is not "
                "permitted except in documented emergencies. All receipts must be itemised; "
                "credit-card statements alone are not accepted as proof of purchase. Receipts "
                "submitted more than 30 calendar days after the transaction date will be declined "
                "and reimbursement will not be issued regardless of approval status."
            ),
        },
    ],
    "borgonero-fc": [
        {
            "filename": "history.md",
            "chunk_id": 0,
            "content": (
                "Borgonero FC was founded on 14 April 1923 by a group of 11 textile workers "
                "employed at the Lanificio Meretti wool mill in Borgonero, a small town in the "
                "Canavese area of Piedmont, northern Italy. The club's original name was Unione "
                "Sportiva Borgonero; it adopted the current name in 1948 after merging with the "
                "local cycling association. The club colours — burgundy and ash grey — were chosen "
                "to match the livery of the Lanificio Meretti company vans. Borgonero FC spent "
                "most of its early decades in the regional amateur leagues (Prima Categoria and "
                "Promozione Piemonte) before winning promotion to Serie D in 1971 under coach "
                "Aldo Farabegoli, who managed the club for a record 9 consecutive seasons."
            ),
        },
        {
            "filename": "history.md",
            "chunk_id": 1,
            "content": (
                "Borgonero FC's most celebrated achievement is the Serie C title won in the "
                "1986–87 season under coach Renato Spinazzola, finishing with 61 points from "
                "34 matches (18 wins, 7 draws, 9 losses), with striker Luca Patanello top-scoring "
                "with 19 league goals. The club repeated the feat in 2008–09, claiming the Serie C "
                "Group B title with 74 points (23 wins, 5 draws, 6 losses), this time under "
                "Argentinian coach Marcelo Viedma. The 2009 promotion sent Borgonero FC to Serie B "
                "for the first time in the club's history. After a difficult decade struggling "
                "against relegation, the club was eventually relegated back to Serie C at the end "
                "of the 2018–19 Serie B season, finishing 19th out of 22 with only 31 points."
            ),
        },
        {
            "filename": "stadium.md",
            "chunk_id": 0,
            "content": (
                "Borgonero FC plays its home matches at the Stadio delle Valli, located on Via "
                "Circonvallazione Nord 8 in Borgonero. The stadium was originally built in 1962 "
                "with a capacity of 8,200. A major renovation project completed in August 2011 "
                "expanded the capacity to 12,400 seats (9,800 covered), added two new hospitality "
                "lounges (Lounge Patanello and Lounge Viedma), and replaced the original cinder "
                "track with a modern athletics lane configuration. In July 2022 the natural grass "
                "pitch was replaced with a FIFA Quality Pro certified synthetic turf surface "
                "supplied by SportField Italia, making Borgonero FC one of only three Serie C "
                "clubs in Piedmont to use synthetic grass as of the 2023–24 season."
            ),
        },
        {
            "filename": "season_2023_24.md",
            "chunk_id": 0,
            "content": (
                "In the 2023–24 Serie C Group A season, Borgonero FC finished 3rd in the "
                "standings with 68 points from 36 matches: 22 wins, 2 draws, and 12 losses. "
                "The 3rd-place finish qualified the club for the Serie C playoff semi-finals, "
                "where they were eliminated by Alessandria Calcio over two legs (1–0 away, "
                "0–1 home, eliminated on away goals). Head coach for the season was Davide "
                "Furlotti, appointed on 28 June 2023 on a two-year contract. The club's home "
                "record at Stadio delle Valli was particularly strong: 14 wins, 1 draw, and "
                "3 losses in 18 home league matches, with 41 goals scored and only 14 conceded."
            ),
        },
        {
            "filename": "season_2023_24.md",
            "chunk_id": 1,
            "content": (
                "The top scorer for Borgonero FC in the 2023–24 season was centre-forward "
                "Marco Dellanave, who netted 24 goals across all competitions (21 in Serie C, "
                "2 in Coppa Italia Serie C, 1 in the playoff semi-final). Dellanave, born in "
                "Ivrea on 3 February 1997, joined the club on a free transfer in July 2022 from "
                "Pro Vercelli and signed a contract extension in November 2023 keeping him at "
                "Borgonero FC until June 2026. Second-highest scorer was attacking midfielder "
                "Sébastien Kourouma (born Abidjan, 11 September 1999, French-Ivorian nationality) "
                "with 11 goals and 9 assists, earning him a place in the Serie C Group A "
                "Team of the Season as voted by Lega Pro technical observers."
            ),
        },
        {
            "filename": "transfers.md",
            "chunk_id": 0,
            "content": (
                "During the January 2024 transfer window, Borgonero FC made two significant "
                "moves. On 12 January 2024, the club signed Portuguese central midfielder "
                "Tomás Ferreira (born Braga, 7 May 2001) from Sporting Clube de Braga B on a "
                "permanent deal for a reported fee of €180,000, with Ferreira signing a contract "
                "through June 2027. Ferreira had made 14 appearances in the Portuguese Segunda "
                "Liga (second division) prior to the transfer. On 19 January 2024, right-back "
                "Gennaro Sisto (born Salerno, 22 March 1996) was sold to Palermo FC for €220,000. "
                "Sisto had been at Borgonero FC since 2020 and made 112 appearances for the club "
                "across all competitions. The net transfer balance for the January window was "
                "therefore +€40,000 in favour of Borgonero FC."
            ),
        },
    ],
}

PROVIDERS = ["redis", "qdrant"]
EMBED_PROVIDERS = ["google"]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def get_embeddings(
        texts: list[str], embed_provider: str, api_key: str | None, embed_dim: int
) -> list[list[float]]:
    """Generates embeddings for a list of texts using the given provider."""
    from google import genai
    from google.genai import types as genai_types

        client = genai.Client(api_key=api_key)
        response = client.models.embed_content(
            model="gemini-embedding-001",
            contents=texts,
            config=genai_types.EmbedContentConfig(
                output_dimensionality=embed_dim,
                task_type="RETRIEVAL_DOCUMENT",
            ),
        )
        return [list(e.values) for e in response.embeddings]
    elif embed_provider == "ollama":
        from llama_index.embeddings.ollama import OllamaEmbedding

        params = {
            'base_url': "http://localhost:11434",
        }

        embed_model: OllamaEmbedding = OllamaEmbedding(
            model_name="qwen3-embedding",
            **{k: v for k, v in params.items() if v is not None}
        )

        return [i[:768] for i in embed_model.get_text_embedding_batch(texts)]

    # mock: random unit vectors
    return [random_unit_vector(embed_dim) for _ in texts]


# ---------------------------------------------------------------------------
# Core populate function
# ---------------------------------------------------------------------------


async def populate(
        topic: str,
        docs: list[dict],
        provider: str,
        embed_dim: int,
        embed_provider: str,
        api_key: str | None,
) -> None:
    os.environ["VECTOR_DB_PROVIDER"] = provider

    from dos_utility.vector_db import get_vector_db_ctx
    from dos_utility.vector_db.interface import ObjectData

    index_name = topic

    console.rule(f"[bold cyan]Topic: {index_name}")
    console.print(
        f"[dim]{len(docs)} documents · embed_dim={embed_dim} · "
        f"db={provider} · embeddings={embed_provider}[/dim]"
    )

    with console.status("[bold]Generating embeddings...", spinner="dots"):
        texts = [doc["content"] for doc in docs]
        embeddings = get_embeddings(texts, embed_provider, api_key, embed_dim)
    console.print(
        f"[green]✓[/] Generated {len(embeddings)} vectors (dim={len(embeddings[0])})"
    )

    async with get_vector_db_ctx() as vdb:
        with console.status("[bold]Creating index...", spinner="dots"):
            await vdb.create_index(index_name=index_name, vector_dim=embed_dim)
        console.print(f"[green]✓[/] Index [bold]{index_name}[/] created")

        with console.status("[bold]Inserting documents...", spinner="dots"):
            data = [
                ObjectData(
                    filename=doc["filename"],
                    chunk_id=doc["chunk_id"],
                    content=doc["content"],
                    vector=embeddings[i],
                )
                for i, doc in enumerate(docs)
            ]
            ids = await vdb.put_objects(index_name=index_name, data=data)
        console.print(f"[green]✓[/] Inserted {len(ids)} documents")

        with console.status("[bold]Verifying with semantic search...", spinner="dots"):
            query_text = docs[0]["content"][:80]
            query_embedding = get_embeddings(
                [query_text], embed_provider, api_key, embed_dim
            )[0]
            results = await vdb.semantic_search(
                index_name=index_name,
                embedding_query=query_embedding,
                max_results=3,
                score_threshold=0.0,
            )
        console.print("[green]✓[/] Semantic search returned top 3:\n")

        if results:
            table = Table(show_header=True, header_style="bold magenta", box=None)
            table.add_column("Score", justify="right", style="cyan", width=7)
            table.add_column("Source", style="yellow")
            table.add_column("Preview", style="dim", overflow="fold")
            for r in results:
                preview = r.content[:80].replace("\n", " ") + "…"
                table.add_row(f"{r.score:.3f}", f"{r.filename}:{r.chunk_id}", preview)
            console.print(table)
        else:
            console.print(
                "[yellow]No results returned — check your connection settings.[/]"
            )


# ---------------------------------------------------------------------------
# Wizard
# ---------------------------------------------------------------------------


def is_tty() -> bool:
    return sys.stdin.isatty() and sys.stdout.isatty()


def run_wizard(args: argparse.Namespace) -> argparse.Namespace:
    """Prompt for any missing values. Caller guarantees we're on a TTY."""
    if args.provider is None:
        args.provider = questionary.select(
            "Which vector DB do you want to populate?",
            choices=PROVIDERS,
        ).ask()
        if args.provider is None:
            raise KeyboardInterrupt

    if args.topic is None:
        args.topic = questionary.select(
            "Which topic should be populated?",
            choices=[*TOPICS.keys(), "all"],
            default="all",
        ).ask()
        if args.topic is None:
            raise KeyboardInterrupt

    if args.embed_provider is None:
        args.embed_provider = questionary.select(
            "Which embedding provider?",
            choices=EMBED_PROVIDERS,
            default="google",
        ).ask()
        if args.embed_provider is None:
            raise KeyboardInterrupt

    if not args.google_api_key:
        args.google_api_key = questionary.password(
            "Google API key (input hidden):",
        ).ask()
        if not args.google_api_key:
            raise KeyboardInterrupt

    return args


def show_summary(args: argparse.Namespace) -> None:
    host = args.host or os.environ.get(
        "REDIS_HOST" if args.provider == "redis" else "QDRANT_HOST", "<default>"
    )
    port = args.port or os.environ.get(
        "REDIS_PORT" if args.provider == "redis" else "QDRANT_PORT", "<default>"
    )
    body = (
        f"[bold]Provider[/]        {args.provider}\n"
        f"[bold]Topic[/]           {args.topic}\n"
        f"[bold]Embed provider[/]  {args.embed_provider}\n"
        f"[bold]Embed dim[/]       {args.embed_dim}\n"
        f"[bold]Target[/]          {host}:{port}"
    )
    console.print(Panel(body, title="Run configuration", border_style="cyan"))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Populate the vector DB with sample documents for chatbot testing. "
        "Run with no flags to launch the interactive wizard.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--provider",
        choices=PROVIDERS,
        default=None,
        help="Vector DB provider. Prompted if omitted on a TTY.",
    )
    parser.add_argument(
        "--topic",
        choices=[*TOPICS.keys(), "all"],
        default=None,
        help="Topic (index) to populate. Default: all.",
    )
    parser.add_argument(
        "--embed-provider",
        choices=EMBED_PROVIDERS,
        default=None,
        help="Embedding provider. Only 'google' is supported for now. Prompted if omitted.",
    )
    parser.add_argument(
        "--embed-dim",
        type=int,
        default=768,
        help="Embedding vector dimension — must match chatbot-api EMBED_DIM (default: 768).",
    )
    parser.add_argument(
        "--host",
        default=None,
        help="Override the DB host (sets REDIS_HOST or QDRANT_HOST env var).",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="Override the DB port (sets REDIS_PORT or QDRANT_PORT env var).",
    )
    parser.add_argument(
        "--embed-provider",
        choices=["mock", "google", "ollama"],
        default="mock",
        help="Embedding provider (default: mock). Use 'google' for real semantic embeddings.",
    )
    parser.add_argument(
        "--google-api-key",
        default=os.environ.get("GOOGLE_API_KEY"),
        help="Google API key. Falls back to GOOGLE_API_KEY env var.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    interactive = is_tty()

    if interactive:
        try:
            args = run_wizard(args)
        except KeyboardInterrupt:
            console.print("\n[yellow]Aborted.[/]")
            sys.exit(130)
    else:
        if args.provider is None:
            parser.error("--provider is required when not running interactively")
        if args.topic is None:
            args.topic = "all"
        if args.embed_provider is None:
            args.embed_provider = "google"

    if not args.google_api_key:
        parser.error("--google-api-key (or GOOGLE_API_KEY env var) is required")

    if args.host:
        os.environ["REDIS_HOST" if args.provider == "redis" else "QDRANT_HOST"] = (
            args.host
        )
    if args.port:
        os.environ["REDIS_PORT" if args.provider == "redis" else "QDRANT_PORT"] = str(
            args.port
        )

    show_summary(args)

    if interactive:
        proceed = questionary.confirm("Proceed?", default=True).ask()
        if not proceed:
            console.print("[yellow]Aborted.[/]")
            return

    selected: dict[str, list[dict]] = (
        TOPICS if args.topic == "all" else {args.topic: TOPICS[args.topic]}
    )

    async def run_all() -> None:
        for topic, docs in selected.items():
            await populate(
                topic=topic,
                docs=docs,
                provider=args.provider,
                embed_dim=args.embed_dim,
                embed_provider=args.embed_provider,
                api_key=args.google_api_key,
            )

        populated = list(selected.keys())
        console.rule("[bold green]Done")
        console.print(
            f"[green]✓[/] Populated {len(populated)} index(es): "
            f"[bold]{', '.join(populated)}[/]\n"
        )
        console.print("[bold]Next steps[/]")
        console.print(
            "  Add a YAML config file in "
            "[cyan]chatbot-api/src/modules/chatbot/tool/config/[/]"
        )
        console.print(
            "  for each index you populated. See [cyan]template.yaml[/] for the schema."
        )

    asyncio.run(run_all())


if __name__ == "__main__":
    main()
