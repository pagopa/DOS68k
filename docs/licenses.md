# Licenses

This file is intended as a guide about how to collect licenses for a service/micro-service.

```bash
cd <service-folder> # es. cd auth
uv add --dev pip-licenses # If already installed nothing happens
uv run pip-licenses --format=json > licenses.json # Produce a file licenses.json with licenses of each dependency
```