from functools import lru_cache

from .env import TracingProvider, get_tracing_settings
from .interface import TracingInterface, TraceHandle
from .noop import NoopTracer

__all__ = [
    "get_tracer",
    "TracingInterface",
    "TraceHandle",
]


@lru_cache()
def get_tracer() -> TracingInterface:
    """Return the configured tracing provider (lru-cached singleton).

    Provider is selected by the ``TRACING_PROVIDER`` env var.
    Defaults to ``NOOP`` when unset.

    See :mod:`dos_utility.tracing.interface` for the full contract.
    See CONTEXT.md and docs/adr/ for the architectural rationale.
    """
    settings = get_tracing_settings()

    if settings.TRACING_PROVIDER is TracingProvider.NOOP:
        return NoopTracer()

    raise ValueError(f"Unsupported tracing provider: {settings.TRACING_PROVIDER}")
