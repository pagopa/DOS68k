# Masking Service

A FastAPI microservice that detects and masks **Personally Identifiable Information (PII)** in text, powered by [Microsoft Presidio](https://microsoft.github.io/presidio/) and [spaCy](https://spacy.io/).

---

## How it works

The service auto-detects the language of the input text (English, Italian, German, French) and runs it through Presidio's NLP pipeline. Detected PII entities are replaced with structured placeholders in the format `<ENTITY_TYPE_N>` — e.g. `<PERSON_1>`, `<EMAIL_ADDRESS_1>`.

**Detected entities (global):** `CREDIT_CARD`, `CRYPTO`, `DATE_TIME`, `EMAIL_ADDRESS`, `IBAN_CODE`, `IP_ADDRESS`, `LOCATION`, `MEDICAL_LICENSE`, `NRP`, `PERSON`, `PHONE_NUMBER`

**Italian-specific entities:** `IT_FISCAL_CODE`, `IT_DRIVER_LICENSE`, `IT_VAT_CODE`, `IT_PASSPORT`, `IT_IDENTITY_CARD`, `IT_PHYSICAL_ADDRESS`

---

## Run with Docker

> **Note:** The Docker build context is the **repository root** (`DOS68k/`), because the service depends on the shared `dos-utility` package.

### Using Docker Compose (recommended)

From the repository root:

```bash
docker compose up -d --build masking
```

The service will be available at `http://localhost:3001`.

### Standalone Docker build

From the repository root:

```bash
docker build -f masking/Dockerfile -t masking-service .
docker run -p 3000:3000 masking-service
```

The service will be available at `http://localhost:3000`.

---

## API

### `POST /mask/`

Masks PII in the provided text. Returns the anonymized string.

**Request**

```http
POST /mask/
Content-Type: application/json

{
  "text": "My name is Mario Rossi and my email is mario.rossi@example.com"
}
```

**Response**

```
"My name is <PERSON_1> and my email is <EMAIL_ADDRESS_1>"
```

---

### `GET /health`

Returns the service health status.

**Response**

```json
{
  "status": "ok",
  "service": "Masking Service"
}
```

---

## OpenAPI docs

Interactive Swagger UI is available at the root path:

```
http://localhost:3000/
```

---

## Configuration

The NLP pipeline is configured via `config/presidio.yaml`.

| Field | Description |
|---|---|
| `nlp_engine_name` | NLP backend (default: `spacy`) |
| `models` | spaCy models to load per language |
| `ner_model_configuration` | Entity mapping and scoring tuning |
| `allow_list` | Terms that are never masked (e.g. `PagoPA`, `IO`, `SEND`) |

To add a term to the allow list or tune entity recognition, edit `config/presidio.yaml` and rebuild the image.

---

## Local development

Requires [uv](https://docs.astral.sh/uv/) and Python 3.13.

```bash
# Install dependencies
uv sync

# Run in dev mode (hot reload)
uv run fastapi dev src/main.py --port 3000

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src --cov-report=term-missing
```
