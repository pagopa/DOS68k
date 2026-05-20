from contextlib import asynccontextmanager
from typing import Self, Optional, Dict, Any, List
from uuid import uuid4

from dos_utility.tracing.interface import TracingInterface, TraceHandle, SpanHandle
from dos_utility.tracing.models import TraceId


class _NoopSpanHandle(SpanHandle):
    def set_output(self, output: str) -> None:
        pass

    def set_metadata(self, metadata: Dict[str, Any]) -> None:
        pass


class _NoopTraceHandle(TraceHandle):
    def __init__(self) -> None:
        self._id: TraceId = str(uuid4())

    @property
    def id(self) -> TraceId:
        return self._id

    def start_span(
        self,
        name: str,
        input: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        @asynccontextmanager
        async def _ctx():
            yield _NoopSpanHandle()

        return _ctx()

    def set_output(self, output: str) -> None:
        pass

    def set_metadata(self, metadata: Dict[str, Any]) -> None:
        pass


class NoopTracer(TracingInterface):
    """No-op tracing provider.  Satisfies the interface contract without
    making any network calls.  Default for local dev and tests.
    """

    async def __aenter__(self: Self) -> Self:
        return self

    async def __aexit__(self: Self, exc_type, exc_val, exc_tb) -> None:
        pass

    async def is_healthy(self: Self) -> bool:
        return True

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
            yield _NoopTraceHandle()

        return _ctx()

    async def score(
        self: Self,
        trace_id: TraceId,
        name: str,
        value: float,
        comment: Optional[str] = None,
    ) -> None:
        pass

    async def flush(self: Self, timeout: Optional[float] = None) -> None:
        pass
