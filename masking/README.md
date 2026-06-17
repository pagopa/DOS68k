# Masking Service

An optional service that detects and masks **Personally Identifiable Information
(PII)** in text, powered by [Microsoft Presidio](https://microsoft.github.io/presidio/)
and [spaCy](https://spacy.io/).

For the big picture, see [Overview](../docs/overview.md).

## Role in the platform

The masking service is used only by the [chatbot](../chatbot-api/README.md), and
only when `MASK_PII=true`. When enabled, the chatbot sends each question and
answer through this service before storing them, so that personal data is
replaced with structured placeholders (e.g. `<PERSON_1>`, `<EMAIL_ADDRESS_1>`)
in what gets persisted. It is off by default.

The service auto-detects the language of the text (English, Italian, German,
French) and runs the matching detection pipeline.

## What it detects

**All languages:** `CREDIT_CARD`, `CRYPTO`, `DATE_TIME`, `EMAIL_ADDRESS`,
`IBAN_CODE`, `IP_ADDRESS`, `LOCATION`, `MEDICAL_LICENSE`, `NRP`, `PERSON`,
`PHONE_NUMBER`.

**Italian-specific:** `IT_FISCAL_CODE`, `IT_DRIVER_LICENSE`, `IT_VAT_CODE`,
`IT_PASSPORT`, `IT_IDENTITY_CARD`, `IT_PHYSICAL_ADDRESS`.

## Configuration

This service reads **no environment variables**. Its detection behaviour —
languages, entity mappings, scoring, and an allow-list of terms that are never
masked (e.g. `PagoPA`, `IO`, `SEND`) — is set in `config/presidio.yaml`. To tune
recognition or extend the allow-list, edit that file and rebuild the image.
</content>
