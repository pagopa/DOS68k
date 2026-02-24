from typing import List, Self, Annotated, Dict, Any, Optional
from fastapi import Depends
from datetime import datetime, timedelta
from uuid import uuid4
from dos_utility.database.nosql import NoSQLInterface, get_nosql_client, QueryResult, KeyCondition, ConditionOperator

from ..env import get_settings, Settings

class SessionRepository():
    def __init__(self: Self, nosql_client: NoSQLInterface):
        self.nosql_client: NoSQLInterface = nosql_client
        self.env: Settings = get_settings()

    async def get_session(self: Self, session_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        query_result: QueryResult = await self.nosql_client.query(
            table_name="sessions",
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
            table_name="sessions",
            key_conditions=[KeyCondition(field="userId", operator=ConditionOperator.EQ, value=user_id)],
        )

        return query_result.items

    async def create_session(self: Self, user_id: str, session_data: Dict[str, Any]) -> None:
        now: datetime = datetime.now()

        await self.nosql_client.put_item(
            table_name="sessions",
            item={
                "id": str(uuid4()),
                "userId": user_id,
                "createdAt": now.isoformat(),
                "expiresAt": int((now + timedelta(days=self.env.session_expiration_days)).timestamp()),
                **session_data,
            },
        )
        #! Restituire la risorsa creata

    async def delete_session(self: Self, session_id: str, user_id: str) -> None:
        await self.nosql_client.delete_item(
            table_name="sessions",
            key={"userId": user_id, "id": session_id},
        )

def get_session_repository(nosql_client: Annotated[NoSQLInterface, Depends(dependency=get_nosql_client)]) -> SessionRepository:
    return SessionRepository(nosql_client=nosql_client)