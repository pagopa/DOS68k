"""LlamaIndex OpenInference / OpenTelemetry bridge.

Deep module: the rest of the codebase interacts with tracing through
`TracingInterface`. All OpenInference and OpenTelemetry knowledge is
quarantined here behind the two-function interface below. No other
module in this repository should import `openinference` or
`opentelemetry` directly.

The Langfuse provider calls `install_llamaindex_instrumentation()` in
its lifespan `__aenter__` (after the Langfuse SDK has set up its OTel
`TracerProvider`) and `uninstall_llamaindex_instrumentation()` in
`__aexit__`. The NOOP provider does neither and incurs zero
instrumentation overhead.
"""

from logging import Logger
from typing import Any, Optional

from dos_utility.utils.logger import get_logger


logger: Logger = get_logger(name=__name__)


def install_llamaindex_instrumentation(
    tracer_provider: Optional[Any] = None,
) -> None:
    """Install OpenInference auto-instrumentation for LlamaIndex.

    When `tracer_provider` is `None`, the instrumentor uses whatever
    global OTel `TracerProvider` is currently active (Langfuse v4 sets
    one up in its SDK).

    Non-fatal: if instrumentation cannot be installed (missing optional
    dependencies, instrumentor version mismatch, etc.) the failure is
    logged and the caller proceeds without auto-instrumentation.
    """
    try:
        from openinference.instrumentation.llama_index import LlamaIndexInstrumentor

        LlamaIndexInstrumentor().instrument(tracer_provider=tracer_provider)
    except Exception as exc:
        logger.warning(
            "LlamaIndex OpenInference instrumentation install failed (non-fatal): %s",
            exc,
        )


def uninstall_llamaindex_instrumentation() -> None:
    """Remove OpenInference auto-instrumentation for LlamaIndex.

    Idempotent: calling twice (or before any install) is a no-op.

    Non-fatal: failures are logged and never propagate.
    """
    try:
        from openinference.instrumentation.llama_index import LlamaIndexInstrumentor

        LlamaIndexInstrumentor().uninstrument()
    except Exception as exc:
        logger.warning(
            "LlamaIndex OpenInference instrumentation uninstall failed (non-fatal): %s",
            exc,
        )
