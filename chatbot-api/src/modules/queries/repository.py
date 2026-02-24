from typing import List, Self, Annotated, Dict, Any
from fastapi import Depends
from dos_utility.database.nosql import NoSQLInterface, get_nosql_client, QueryResult, KeyCondition, ConditionOperator

class QueryRepository():
    def __init__(self: Self, nosql_client: NoSQLInterface):
        self.nosql_client: NoSQLInterface = nosql_client

    async def get_queries(self: Self, session_id: str) -> List[Dict[str, Any]]:
        query_result: QueryResult = await self.nosql_client.query(
            table_name="queries",
            key_conditions=[KeyCondition(field="sessionId", operator=ConditionOperator.EQ, value=session_id)],
            index_name="sessionId-index",
        )

        return query_result.items

    async def delete_query(self: Self, query_id: str) -> None:
        await self.nosql_client.delete_item(
            table_name="queries",
            key={"id": query_id},
        )

def get_query_repository(nosql_client: Annotated[NoSQLInterface, Depends(dependency=get_nosql_client)]) -> QueryRepository:
    return QueryRepository(nosql_client=nosql_client)