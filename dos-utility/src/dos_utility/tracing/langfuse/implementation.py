from contextlib import asynccontextmanager
from logging import Logger
from typing import Self, Optional, Dict, Any, List

from langfuse import Langfuse, propagate_attributes

from dos_utility.utils.logger import get_logger
from dos_utility.tracing.interface import TracingInterface, TraceHandle, SpanHandle
from dos_utility.tracing.models import TraceId
from dos_utility.tracing.instrumentation import (
    install_llamaindex_instrumentation,
    uninstall_llamaindex_instrumentation,
)
from .env import get_langfuse_settings


logger: Logger = get_logger(name=__name__)


class _LangfuseSpanHandle(SpanHandle):
    """Span handle backed by a Langfuse observation.

    All methods swallow exceptions. A tracing fault never propagates
    into the calling task.
    """

    def __init__(self, observation: Any) -> None:
        self._observation = observation

    def set_output(self, output: str) -> None:
        try:
            self._observation.update(output=output)
        except Exception as exc:
            logger.warning("Span.set_output failed (non-fatal): %s", exc)

    def set_metadata(self, metadata: Dict[str, Any]) -> None:
        try:
            self._observation.update(metadata=metadata)
        except Exception as exc:
            logger.warning("Span.set_metadata failed (non-fatal): %s", exc)


class _LangfuseTraceHandle(TraceHandle):
    """Trace handle backed by the Langfuse SDK.

    All methods swallow exceptions. A tracing fault never propagates
    into the calling task.
    """

    def __init__(
        self, client: Langfuse, initial_metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        self._client = client
        self._output: Optional[str] = None
        self._metadata: Dict[str, Any] = dict(initial_metadata or {})

    @property
    def id(self) -> TraceId:
        try:
            return self._client.get_current_trace_id()
        except Exception as exc:
            logger.warning("Trace.id lookup failed (non-fatal): %s", exc)
            return None

    def start_span(
        self,
        name: str,
        input: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        client = self._client

        @asynccontextmanager
        async def _ctx():
            try:
                cm = client.start_as_current_observation(
                    name=name, input=input, metadata=metadata
                )
                observation = cm.__enter__()
            except Exception as exc:
                logger.warning(
                    "Trace.start_span(%s) open failed (non-fatal): %s", name, exc
                )
                yield _LangfuseSpanHandle(observation=_NullObservation())
                return
            try:
                yield _LangfuseSpanHandle(observation=observation)
            finally:
                try:
                    cm.__exit__(None, None, None)
                except Exception as exc:
                    logger.warning(
                        "Trace.start_span(%s) close failed (non-fatal): %s", name, exc
                    )

        return _ctx()

    def set_output(self, output: str) -> None:
        self._output = output

    def set_metadata(self, metadata: Dict[str, Any]) -> None:
        try:
            self._metadata = {**self._metadata, **metadata}
        except Exception as exc:
            logger.warning("Trace.set_metadata merge failed (non-fatal): %s", exc)


class _NullObservation:
    """Fallback observation used when the SDK failed to open one."""

    def update(self, **_kwargs) -> None:
        pass


class LangfuseTracingProvider(TracingInterface):
    """Langfuse tracing provider. Thin adapter over the official langfuse SDK.

    Implementations MUST NOT block the calling task on network I/O.
    The SDK handles batching, retries, and background flushing internally.

    Every public method is non-fatal: tracing exceptions are swallowed
    and logged, never re-raised.
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
        # The Langfuse SDK has now installed its OTel TracerProvider;
        # register OpenInference auto-instrumentation against it so
        # LlamaIndex retrieval / tool / LLM calls appear as nested Spans.
        install_llamaindex_instrumentation()
        return self

    async def __aexit__(self: Self, exc_type, exc_val, exc_tb) -> None:
        uninstall_llamaindex_instrumentation()
        try:
            self._client.flush()
        except Exception as exc:
            logger.warning("Tracer shutdown flush failed (non-fatal): %s", exc)

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
        client = self._client

        @asynccontextmanager
        async def _ctx():
            handle = _LangfuseTraceHandle(client, initial_metadata=metadata)
            propagate_cm = None
            obs_cm = None
            try:
                propagate_cm = propagate_attributes(
                    user_id=user_id, session_id=session_id, tags=tags
                )
                propagate_cm.__enter__()
                obs_cm = client.start_as_current_observation(
                    name=name, input=input, metadata=metadata
                )
                obs_cm.__enter__()
            except Exception as exc:
                logger.warning("Trace open failed (non-fatal): %s", exc)
                if obs_cm is not None:
                    try:
                        obs_cm.__exit__(None, None, None)
                    except Exception:
                        pass
                    obs_cm = None
                if propagate_cm is not None:
                    try:
                        propagate_cm.__exit__(None, None, None)
                    except Exception:
                        pass
                    propagate_cm = None
            try:
                yield handle
            finally:
                if handle._output is not None:
                    try:
                        client.set_current_trace_io(output=handle._output)
                    except Exception as exc:
                        logger.warning("Trace finalize failed (non-fatal): %s", exc)
                if handle._metadata:
                    try:
                        client.update_current_trace(metadata=handle._metadata)
                    except Exception as exc:
                        logger.warning(
                            "Trace.update_current_trace failed (non-fatal): %s", exc
                        )
                if obs_cm is not None:
                    try:
                        obs_cm.__exit__(None, None, None)
                    except Exception as exc:
                        logger.warning("Trace close failed (non-fatal): %s", exc)
                if propagate_cm is not None:
                    try:
                        propagate_cm.__exit__(None, None, None)
                    except Exception as exc:
                        logger.warning("Trace close failed (non-fatal): %s", exc)

        return _ctx()

    async def score(
        self: Self,
        trace_id: TraceId,
        name: str,
        value: float,
        comment: Optional[str] = None,
    ) -> None:
        try:
            self._client.create_score(
                trace_id=trace_id, name=name, value=value, comment=comment
            )
        except Exception as exc:
            logger.warning("Score(%s) failed (non-fatal): %s", name, exc)

    async def flush(self: Self, timeout: Optional[float] = None) -> None:
        try:
            self._client.flush()
        except Exception as exc:
            logger.warning("Tracer flush failed (non-fatal): %s", exc)
