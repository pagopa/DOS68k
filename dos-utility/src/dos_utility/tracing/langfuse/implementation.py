from contextlib import asynccontextmanager
from typing import Self, Optional, Dict, Any, List

from langfuse import Langfuse

from dos_utility.tracing.interface import TracingInterface, TraceHandle
from dos_utility.tracing.models import TraceId
from .env import get_langfuse_settings


class _LangfuseTraceHandle(TraceHandle):
    def __init__(self, trace_obj) -> None:
        self._trace_obj = trace_obj
        self._output: Optional[str] = None
        self._metadata: Optional[Dict[str, Any]] = None

    @property
    def id(self) -> TraceId:
        return self._trace_obj.id

    async def add_span(
        self,
        name: str,
        input: Optional[str] = None,
        output: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        self._trace_obj.span(name=name, input=input, output=output, metadata=metadata)

    def set_output(self, output: str) -> None:
        self._output = output

    def set_metadata(self, metadata: Dict[str, Any]) -> None:
        self._metadata = metadata


class LangfuseTracingProvider(TracingInterface):
    """Langfuse tracing provider. Thin adapter over the official langfuse SDK.

    Implementations MUST NOT block the calling task on network I/O.
    The SDK handles batching, retries, and background flushing internally.
    """

    async def __aenter__(self: Self) -> Self:
        settings = get_langfuse_settings()
        self._client = Langfuse(
            public_key=settings.LANGFUSE_PUBLIC_KEY,
            secret_key=settings.LANGFUSE_SECRET_KEY,
            host=settings.LANGFUSE_HOST,
            flush_at=settings.LANGFUSE_FLUSH_AT,
            flush_interval=settings.LANGFUSE_FLUSH_INTERVAL_S,
        )
        return self

    async def __aexit__(self: Self, exc_type, exc_val, exc_tb) -> None:
        self._client.flush()

    async def is_healthy(self: Self) -> bool:
        try:
            return self._client.auth_check()
        except Exception:
            return False

    def trace(
        self: Self,
        name: str,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        input: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
    ):
        @asynccontextmanager
        async def _ctx():
            trace_obj = self._client.trace(
                name=name,
                session_id=session_id,
                user_id=user_id,
                input=input,
                metadata=metadata,
                tags=tags,
            )
            handle = _LangfuseTraceHandle(trace_obj)
            try:
                yield handle
            finally:
                update_kwargs = {}
                if handle._output is not None:
                    update_kwargs["output"] = handle._output
                if handle._metadata is not None:
                    update_kwargs["metadata"] = handle._metadata
                if update_kwargs:
                    trace_obj.update(**update_kwargs)

        return _ctx()

    async def score(
        self: Self,
        trace_id: TraceId,
        name: str,
        value: float,
        comment: Optional[str] = None,
    ) -> None:
        self._client.score(trace_id=trace_id, name=name, value=value, comment=comment)

    async def flush(self: Self, timeout: Optional[float] = None) -> None:
        self._client.flush()
