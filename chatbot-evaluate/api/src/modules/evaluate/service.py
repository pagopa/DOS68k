import json
import random

from logging import Logger
from typing import Self, Annotated, Dict, Any, Optional
from fastapi import Depends, HTTPException, status

from dos_utility.utils import logger
from dos_utility.storage import StorageInterface, get_storage
from dos_utility.database.nosql import NoSQLInterface, get_nosql_client, ScanResult, KeyCondition, ConditionOperator, QueryResult
from dos_utility.queue import QueueInterface, get_queue_client

from ...env import (
    get_settings,
    Settings,
)


class EvaluationService:
    def __init__(self: Self, storage: StorageInterface, nosql: NoSQLInterface, queue: QueueInterface):
        self.storage: StorageInterface = storage
        self.nosql: NoSQLInterface = nosql
        self.queue: QueueInterface = queue
        self.settings: Settings = get_settings()
        self.logger: Logger = logger.get_logger(name=__file__, level=self.settings.LOG_LEVEL)

    async def create_simple_feedback(self: Self, user_id: str, query_id: str, feedback: int) -> Dict[str, Any]:
        self.logger.info(f"Creating simple feedback for query_id: {query_id}, feedback: {feedback}")

        #! usa metodo query
        scan_result: ScanResult = await self.nosql.scan(table_name=self.settings.QUERY_TABLENAME)

        query_item: Optional[Dict[str, Any]] = next(
            (item for item in scan_result.items if item.get("id") == query_id),
            None,
        )

        if query_item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Query with id {query_id} not found",
            )

        updated_item: Optional[Dict[str, Any]] = await self.nosql.update_item(
            table_name=self.settings.QUERY_TABLENAME,
            key={"sessionId": query_item["sessionId"], "id": query_id},
            fields_to_update={"feedback": feedback},
        )

        return updated_item

    async def evaluate(self: Self, query_id: str) -> dict:
        self.logger.info(f"Evaluating query_id: {query_id}")

        scan_result: ScanResult = await self.nosql.scan(table_name=self.settings.QUERY_TABLENAME)

        query_item: Optional[Dict[str, Any]] = next(
            (item for item in scan_result.items if item.get("id") == query_id),
            None,
        )

        if query_item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Query with id {query_id} not found",
            )
        elif query_item.get("isEvaluated", True):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Query with id {query_id} has already been evaluated",
            )

        await self.nosql.update_item(
            table_name=self.settings.QUERY_TABLENAME,
            key={"sessionId": query_item["sessionId"], "id": query_id},
            fields_to_update={"isEvaluated": True},
        )

        msg: bytes = json.dumps({"queryId": query_id}).encode("utf-8")
        msg_id: str = await self.queue.enqueue(msg=msg)

        self.logger.info(f"Message enqueued with id: {msg_id} for query_id: {query_id}")

        return {"query_id": query_id, "status": "queued"}


    async def evaluate_all(self: Self, session_id: str) -> dict:
        self.logger.info(f"Evaluating all queries for session_id: {session_id}")

        query_result: QueryResult = await self.nosql.query(
            table_name=self.settings.QUERY_TABLENAME,
            key_conditions=[KeyCondition(field="sessionId", operator=ConditionOperator.EQ, value=session_id)],
        )

        queries = query_result.items
        self.logger.info(f"Found {len(queries)} queries for session_id: {session_id}")

        # Filter not yet evaluated, sort newest→oldest, keep only those with feedback, apply limit
        pending = [q for q in queries if not q.get("isEvaluated", False)]
        pending.sort(key=lambda q: q.get("createdAt", ""), reverse=True)
        with_feedback = [q for q in pending if q.get("feedback", 0) != 0]
        selected = with_feedback[: self.settings.EVALUATE_UPPER_LIMIT]

        # Fill remaining slots with random queries from the same session
        remaining_slots = self.settings.EVALUATE_UPPER_LIMIT - len(selected)
        if remaining_slots > 0:
            selected_ids = {q.get("id") for q in selected}
            fillable = [q for q in pending if q.get("id") not in selected_ids]
            selected += random.sample(fillable, min(remaining_slots, len(fillable)))

        query_ids = [item.get("id") for item in selected]
        msg: bytes = json.dumps({"queryIds": query_ids}).encode("utf-8")
        msg_id: str = await self.queue.enqueue(msg=msg)

        self.logger.info(f"Message enqueued with id: {msg_id} for {len(query_ids)} queries")


        self.logger.info(f"Marked {len(selected)} queries as evaluated")

        selected_by_id = {item.get("id"): item for item in selected}
        evaluations = [
            {
                "query_id": qid,
                "question": selected_by_id[qid].get("question"),
                "answer": selected_by_id[qid].get("answer"),
                "feedback": int(selected_by_id[qid].get("feedback", 0)),
            }
            for qid in query_ids
        ]

        msg_id: str = await self.queue.enqueue(msg=json.dumps(evaluations).encode("utf-8"))
        self.logger.info(f"Message enqueued with id: {msg_id}")

        for item in selected:
            await self.nosql.update_item(
                table_name=self.settings.QUERY_TABLENAME,
                key={"sessionId": session_id, "id": item.get("id")},
                fields_to_update={"isEvaluated": True},
            )

        return {"evaluations": evaluations}


def get_evaluation_service(
    storage: Annotated[StorageInterface, Depends(dependency=get_storage)],
    nosql: Annotated[NoSQLInterface, Depends(dependency=get_nosql_client)],
    queue: Annotated[QueueInterface, Depends(dependency=get_queue_client)],
) -> EvaluationService:
    return EvaluationService(storage=storage, nosql=nosql, queue=queue)