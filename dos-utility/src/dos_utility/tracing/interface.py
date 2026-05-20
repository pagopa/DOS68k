from abc import ABC, abstractmethod
from contextlib import AbstractAsyncContextManager
from typing import Self, Optional, Dict, Any, List

from .models import TraceId


class SpanHandle(ABC):
    """Handle for an open Span, yielded by TraceHandle.start_span().

    Implementations must catch and log their own exceptions; no method
    on a SpanHandle is permitted to raise into the caller.
    """

    @abstractmethod
    def set_output(self, output: str) -> None:
        """Set the output payload of this span."""
        ...

    @abstractmethod
    def set_metadata(self, metadata: Dict[str, Any]) -> None:
        """Attach metadata to this span. Shallow-merge with prior calls."""
        ...


class TraceHandle(ABC):
    """Handle for an open Trace, yielded by TracingInterface.trace().

    Implementations must catch and log their own exceptions; no method
    on a TraceHandle is permitted to raise into the caller.
    """

    @property
    @abstractmethod
    def id(self) -> TraceId:
        """Unique identifier for this trace, assigned by the provider."""
        ...

    @abstractmethod
    def start_span(
        self,
        name: str,
        input: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AbstractAsyncContextManager[SpanHandle]:
        """Open a nested Span with real start/end timing.

        Usage::

            async with trace_handle.start_span(name="sanitize_input", input=q) as span:
                ...
                span.set_output(cleaned)
        """
        ...

    @abstractmethod
    def set_output(self, output: str) -> None:
        """Set the final output for this trace."""
        ...

    @abstractmethod
    def set_metadata(self, metadata: Dict[str, Any]) -> None:
        """Attach metadata to this trace.

        Semantics are shallow-merge: successive calls combine as
        ``{**existing, **new}``, so independent call sites can accumulate
        fields without coordination.
        """
        ...


class TracingInterface(ABC):
    """Abstract interface for all tracing providers.

    Implementations MUST NOT block the calling task on network I/O.
    All provider implementations must buffer telemetry in-process and
    ship it in the background, so the request path is never tied to
    network latency or availability of the tracing backend.

    Implementations are ALSO non-fatal: every method on TracingInterface,
    TraceHandle and SpanHandle catches and logs its own exceptions. A
    tracing fault degrades observability but never fails the request.
    """

    @abstractmethod
    async def __aenter__(self: Self) -> Self:
        """Open the tracer (connect, start background workers, etc.)."""
        ...

    @abstractmethod
    async def __aexit__(self: Self, exc_type, exc_val, exc_tb) -> None:
        """Close the tracer and flush any buffered telemetry."""
        ...

    @abstractmethod
    async def is_healthy(self: Self) -> bool:
        """Return True if the tracing backend is reachable."""
        ...

    @abstractmethod
    def trace(
        self: Self,
        name: str,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        input: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
    ) -> AbstractAsyncContextManager[TraceHandle]:
        """Open a Trace and yield a TraceHandle.

        Usage::

            async with tracer.trace(name="query", session_id=..., user_id=..., input=question) as handle:
                result = await chatbot.chat_generate(...)
                handle.set_output(result)

        The returned context manager assigns a TraceId on entry and
        finalises the trace (timestamps, status) on exit.
        """
        ...

    @abstractmethod
    async def score(
        self: Self,
        trace_id: TraceId,
        name: str,
        value: float,
        comment: Optional[str] = None,
    ) -> None:
        """Attach a numeric Score to an existing Trace."""
        ...

    @abstractmethod
    async def flush(self: Self, timeout: Optional[float] = None) -> None:
        """Drain any in-process buffer.  Called on graceful shutdown."""
        ...
