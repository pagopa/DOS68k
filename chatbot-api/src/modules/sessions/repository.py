from typing import List, Self, Annotated, Dict, Any, Optional
from fastapi import Depends
from datetime import datetime
try:
    from uuid import uuid7
except ImportError:  # pragma: no cover
    from uuid6 import uuid7  # backport for Python < 3.14  # pragma: no cover
from dos_utility.database.nosql import NoSQLInterface, get_nosql_client, QueryResult, KeyCondition, ConditionOperator

from .env import get_session_settings, SessionSettings

class SessionRepository():
    def __init__(self: Self, nosql_client: NoSQLInterface):
        self.nosql_client: NoSQLInterface = nosql_client
        self.env: SessionSettings = get_session_settings()

    async def get_session(self: Self, session_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        query_result: QueryResult = await self.nosql_client.query(
            table_name=self.env.SESSIONS_TABLENAME,
            key_conditions=[
                KeyCondition(field="id", operator=ConditionOperator.EQ, value=session_id),
                KeyCondition(field="userId", operator=ConditionOperator.EQ, value=user_id),
            ],
        )

        if len(query_result.items) == 0:
            return None

        return query_result.items[0]

    async def get_sessions(self: Self, user_id: str) -> List[Dict[str, Any]]:
        query_result: QueryResult = await self.nosql_client.query(
            table_name=self.env.SESSIONS_TABLENAME,
            key_conditions=[KeyCondition(field="userId", operator=ConditionOperator.EQ, value=user_id)],
        )

        return query_result.items

    async def create_session(self: Self, user_id: str, session_data: Dict[str, Any]) -> Dict[str, Any]:
        now: datetime = datetime.now()
        session_id: str = str(uuid7())
        item: Dict[str, Any] = {
            "id": session_id,
            "userId": user_id,
            "createdAt": now.isoformat(),
            **session_data,
        }

        await self.nosql_client.put_item(table_name="sessions", item=item)

        return item

    async def delete_session(self: Self, session_id: str, user_id: str) -> None:
        await self.nosql_client.delete_item(
            table_name=self.env.SESSIONS_TABLENAME,
            key={"userId": user_id, "id": session_id},
        )

def get_session_repository(nosql_client: Annotated[NoSQLInterface, Depends(dependency=get_nosql_client)]) -> SessionRepository:
    return SessionRepository(nosql_client=nosql_client)