from typing import List, Self, Annotated, Dict, Any
from uuid import uuid7
from fastapi import Depends
from datetime import datetime
from dos_utility.database.nosql import NoSQLInterface, get_nosql_client, QueryResult, KeyCondition, ConditionOperator

from ..env import get_session_settings, SessionSettings

class QueryRepository():
    def __init__(self: Self, nosql_client: NoSQLInterface):
        self.nosql_client: NoSQLInterface = nosql_client
        self.env: SessionSettings = get_session_settings()

    async def get_queries(self: Self, session_id: str) -> List[Dict[str, Any]]:
        query_result: QueryResult = await self.nosql_client.query(
            table_name="queries",
            key_conditions=[KeyCondition(field="sessionId", operator=ConditionOperator.EQ, value=session_id)],
        )

        return query_result.items

    async def create_query(self: Self, session_id: str, query_data: Dict[str, Any]) -> Dict[str, Any]:
        item: Dict[str, Any] = {
            "id": str(uuid7()),
            "sessionId": session_id,
            "badAnswer": False,
            "createdAt": datetime.now().isoformat(),
            **query_data,
        }

        await self.nosql_client.put_item(table_name="queries", item=item)

        return item

    async def delete_query(self: Self, query_id: str, session_id: str) -> None:
        await self.nosql_client.delete_item(
            table_name="queries",
            key={"id": query_id, "sessionId": session_id},
        )

def get_query_repository(nosql_client: Annotated[NoSQLInterface, Depends(dependency=get_nosql_client)]) -> QueryRepository:
    return QueryRepository(nosql_client=nosql_client)