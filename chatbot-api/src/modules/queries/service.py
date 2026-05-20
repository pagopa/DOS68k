import nh3

from decimal import Decimal
from logging import Logger
from typing import List, Self, Annotated, Dict, Any, Optional
from fastapi import Depends, HTTPException, status
from httpx import AsyncClient, Response, Timeout
from dos_utility.utils.logger import get_logger
from dos_utility.tracing import TracingInterface, get_tracer

from .repository import QueryRepository, get_query_repository
from ..sessions.repository import get_session_repository, SessionRepository
from ..env import (
    get_masking_settings,
    get_logging_settings,
    MaskingSettings,
    LogSettings,
)
from ..utils import format_expiration_dt
from ..chatbot import Chatbot, get_chatbot
from ..chatbot.chatbot import FALLBACK_RESPONSE
from ..chatbot.config_hash import get_agent_config_hash, get_tool_config_hash
from ..chatbot.version import CHATBOT_API_VERSION


class QueryService:
    def __init__(
        self: Self,
        query_repository: QueryRepository,
        session_repository: SessionRepository,
        chatbot: Chatbot,
        tracer: TracingInterface,
    ):
        self.query_repository: QueryRepository = query_repository
        self.session_repository: SessionRepository = session_repository
        self.chatbot: Chatbot = chatbot
        self.tracer: TracingInterface = tracer
        self.masking_settings: MaskingSettings = get_masking_settings()
        self.__log_settings: LogSettings = get_logging_settings()
        self.logger: Logger = get_logger(
            name=__name__, level=self.__log_settings.log_level
        )

    async def __mask_pii(self: Self, text: str) -> str:
        async with AsyncClient(timeout=Timeout(timeout=20.0)) as client:
            response: Response = await client.post(
                url=f"{self.masking_settings.masking_service_url}/mask",
                json={"text": text},
            )

            if response.status_code != status.HTTP_200_OK:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Masking service error",
                )

        masked_text: str = response.json()

        self.logger.debug("Masked PII")

        return masked_text

    async def get_queries(
        self: Self, session_id: str, user_id: str
    ) -> List[Dict[str, Any]]:
        session: Optional[Dict[str, Any]] = await self.session_repository.get_session(
            session_id=session_id, user_id=user_id
        )

        if session is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
            )

        queries: List[Dict[str, Any]] = await self.query_repository.get_queries(
            session_id=session_id
        )

        return [
            {
                "id": query["id"],
                "session_id": query["sessionId"],
                "question": query["question"],
                "answer": query["answer"],
                "bad_answer": query["badAnswer"],
                "topic": query["topic"],
                "context": query["context"],
                "created_at": query["createdAt"],
                "expires_at": format_expiration_dt(query["expiresAt"]),
                "tracing_trace_id": query.get("tracingTraceId"),
            }
            for query in queries
        ]

    async def create_query(
        self: Self,
        session_id: str,
        user_id: str,
        user_role: str,
        question: str,
        session_history: Optional[List[Dict[str, str]]],
    ) -> Dict[str, Any]:
        session: Optional[Dict[str, Any]] = await self.session_repository.get_session(
            session_id=session_id, user_id=user_id
        )

        if session is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
            )

        tracing_trace_id: Optional[str] = None
        masking_enabled: bool = self.masking_settings.mask_pii is True
        async with self.tracer.trace(
            name="query",
            session_id=str(session_id),
            user_id=str(user_id),
            input=question,
        ) as trace_handle:
            trace_handle.set_metadata(
                {
                    "masking.enabled": masking_enabled,
                    "user.role": user_role,
                    "chatbot_api.version": CHATBOT_API_VERSION,
                    "agent.config_hash": get_agent_config_hash(),
                    "tool.config_hash": get_tool_config_hash(),
                }
            )

            async with trace_handle.start_span(
                name="sanitize_input", input=question
            ) as span:
                question_cleaned: str = nh3.clean(html=question)
                span.set_output(question_cleaned)
            self.logger.debug("Sanitized question: %r", question_cleaned)

            async with trace_handle.start_span(name="load_history"):
                if session_history is None:
                    session_history = await self.query_repository.get_queries(
                        session_id=session_id
                    )

            self.logger.debug("Generating answer with AI agent...")
            response_json: Dict[str, Any] = await self.chatbot.chat_generate(
                query_str=question_cleaned,
                messages=session_history,
            )
            answer: str = response_json["response"]
            trace_handle.set_metadata(
                {"response.fallback": answer == FALLBACK_RESPONSE}
            )

            question_masked: str = question_cleaned
            answer_masked: str = answer

            if masking_enabled:
                async with trace_handle.start_span(
                    name="mask_pii_input", input=question_cleaned
                ) as span:
                    question_masked = await self.__mask_pii(text=question_cleaned)
                    span.set_output(question_masked)
                async with trace_handle.start_span(
                    name="mask_pii_output", input=answer
                ) as span:
                    answer_masked = await self.__mask_pii(text=answer)
                    span.set_output(answer_masked)
                trace_handle.set_metadata(
                    {
                        "masking.input_changed": question_masked != question_cleaned,
                        "masking.output_changed": answer_masked != answer,
                    }
                )

            trace_handle.set_output(answer_masked)
            tracing_trace_id = trace_handle.id

        context = [
            {
                **chunk,
                "score": Decimal(str(chunk["score"]))
                if chunk["score"] is not None
                else None,
            }
            for chunk in response_json["context"]
        ]

        item: Dict[str, Any] = await self.query_repository.create_query(
            session_id=session_id,
            query_data={
                "question": question_masked,
                "answer": answer_masked,
                "expiresAt": session["expiresAt"],
                "context": context,
                "topic": [],
                "tracingTraceId": tracing_trace_id,
            },
        )

        self.logger.debug(
            "Query stored - id=%s, session_id=%s", item["id"], item["sessionId"]
        )

        return {
            "id": item["id"],
            "session_id": item["sessionId"],
            "question": item["question"],
            "answer": item["answer"],
            "bad_answer": item["badAnswer"],
            "topic": item["topic"],
            "context": item["context"],
            "created_at": item["createdAt"],
            "expires_at": format_expiration_dt(item["expiresAt"]),
            "tracing_trace_id": item.get("tracingTraceId"),
        }


def get_query_service(
    query_repository: Annotated[
        QueryRepository, Depends(dependency=get_query_repository)
    ],
    session_repository: Annotated[
        SessionRepository, Depends(dependency=get_session_repository)
    ],
    chatbot: Annotated[Chatbot, Depends(dependency=get_chatbot)],
    tracer: Annotated[TracingInterface, Depends(dependency=get_tracer)],
) -> QueryService:
    return QueryService(
        query_repository=query_repository,
        session_repository=session_repository,
        chatbot=chatbot,
        tracer=tracer,
    )
