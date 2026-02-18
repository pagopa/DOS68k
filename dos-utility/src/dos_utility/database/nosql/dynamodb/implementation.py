import asyncio
import boto3
import logging

from typing import Any, Dict, List, Optional, Self
from asyncio import AbstractEventLoop
from boto3.dynamodb.conditions import Key
from boto3.resources.factory import ServiceResource

from ....utils.aws import get_aws_credentials_settings, AWSCredentialsSettings
from ..interface import NoSQLInterface
from ..models import ConditionOperator, KeyCondition, QueryResult, ScanResult
from .env import DynamoDBSettings, get_dynamodb_settings


class DynamoDBNoSQL(NoSQLInterface):
    def __init__(self: Self) -> None:
        self._settings: DynamoDBSettings = get_dynamodb_settings()
        self._aws_credentials: AWSCredentialsSettings = get_aws_credentials_settings()

    async def __aenter__(self: Self) -> Self:
        loop: AbstractEventLoop = asyncio.get_event_loop()

        kwargs: Dict[str, Any] = {
            "region_name": self._settings.DYNAMODB_REGION,
            "aws_access_key_id": self._aws_credentials.AWS_ACCESS_KEY_ID,
            "aws_secret_access_key": self._aws_credentials.AWS_SECRET_ACCESS_KEY.get_secret_value(),
        }
        if self._settings.DYNAMODB_ENDPOINT_URL is not None:
            kwargs["endpoint_url"] = self._settings.DYNAMODB_ENDPOINT_URL + (f":{self._settings.DYNAMODB_PORT}" if self._settings.DYNAMODB_PORT else "")

        self._resource: ServiceResource = await loop.run_in_executor(
            None,
            lambda: boto3.resource("dynamodb", **kwargs),
        )

        return self

    async def __aexit__(self: Self, exc_type, exc_val, exc_tb) -> None:
        pass

    def __get_table_name(self: Self, table_name: str) -> str:
        """Prepend table prefix if configured."""
        if self._settings.DYNAMODB_TABLE_PREFIX is not None:
            return f"{self._settings.DYNAMODB_TABLE_PREFIX}{table_name}"

        return table_name

    async def is_healthy(self: Self) -> bool:
        loop: AbstractEventLoop = asyncio.get_event_loop()
        try:
            await loop.run_in_executor(
                None,
                lambda: list(self._resource.tables.limit(1)),
            )
        except Exception as e:
            logging.error(f"DynamoDB health check failed: {e}")

            return False

        return True

    async def put_item(self: Self, table_name: str, item: Dict[str, Any]) -> None:
        loop: AbstractEventLoop = asyncio.get_event_loop()
        table = self._resource.Table(self.__get_table_name(table_name=table_name))

        await loop.run_in_executor(
            None,
            lambda: table.put_item(Item=item),
        )

    async def get_item(self: Self, table_name: str, key: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        loop: AbstractEventLoop = asyncio.get_event_loop()
        table = self._resource.Table(self.__get_table_name(table_name=table_name))
        response = await loop.run_in_executor(
            None,
            lambda: table.get_item(Key=key),
        )

        return response.get("Item")

    async def delete_item(self: Self, table_name: str, key: Dict[str, Any]) -> None:
        loop: AbstractEventLoop = asyncio.get_event_loop()
        table = self._resource.Table(self.__get_table_name(table_name=table_name))
        await loop.run_in_executor(
            None,
            lambda: table.delete_item(Key=key),
        )

    async def update_item(
        self: Self,
        table_name: str,
        key: Dict[str, Any],
        fields_to_update: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        loop: AbstractEventLoop = asyncio.get_event_loop()
        table = self._resource.Table(self.__get_table_name(table_name=table_name))

        # Build UpdateExpression, ExpressionAttributeNames, and ExpressionAttributeValues
        update_parts: List[str] = []
        expression_attribute_names: Dict[str, str] = {}
        expression_attribute_values: Dict[str, Any] = {}

        for i, (field_name, field_value) in enumerate(fields_to_update.items()):
            name_placeholder: str = f"#field{i}"
            value_placeholder: str = f":val{i}"
            update_parts.append(f"{name_placeholder} = {value_placeholder}")
            expression_attribute_names[name_placeholder] = field_name
            expression_attribute_values[value_placeholder] = field_value

        update_expression: str = "SET " + ", ".join(update_parts)

        response = await loop.run_in_executor(
            None,
            lambda: table.update_item(
                Key=key,
                UpdateExpression=update_expression,
                ExpressionAttributeNames=expression_attribute_names,
                ExpressionAttributeValues=expression_attribute_values,
                ReturnValues="ALL_NEW",
            ),
        )

        return response.get("Attributes")

    def __build_key_condition_expression(self: Self, key_conditions: List[KeyCondition]) -> Any:
        """Build a DynamoDB KeyConditionExpression from a list of KeyCondition objects."""
        expression: Any = None

        for condition in key_conditions:
            key: Key = Key(condition.field)

            if condition.operator is ConditionOperator.EQ:
                cond_expr = key.eq(condition.value)
            elif condition.operator is ConditionOperator.GT:
                cond_expr = key.gt(condition.value)
            elif condition.operator is ConditionOperator.LT:
                cond_expr = key.lt(condition.value)
            elif condition.operator is ConditionOperator.GTE:
                cond_expr = key.gte(condition.value)
            elif condition.operator is ConditionOperator.LTE:
                cond_expr = key.lte(condition.value)
            elif condition.operator is ConditionOperator.BEGINS_WITH:
                cond_expr = key.begins_with(condition.value)
            elif condition.operator is ConditionOperator.BETWEEN:
                cond_expr = key.between(condition.value, condition.second_value)

            if expression is None:
                expression = cond_expr
            else:
                expression = expression & cond_expr

        return expression

    async def query(
        self: Self,
        table_name: str,
        key_conditions: List[KeyCondition],
        index_name: Optional[str] = None,
        sort_ascending: bool = True,
        limit: Optional[int] = None,
        count_only: bool = False,
    ) -> QueryResult:
        loop: AbstractEventLoop = asyncio.get_event_loop()
        table = self._resource.Table(self.__get_table_name(table_name))

        kwargs: Dict[str, Any] = {
            "KeyConditionExpression": self.__build_key_condition_expression(key_conditions),
            "ScanIndexForward": sort_ascending,
        }

        if index_name is not None:
            kwargs["IndexName"] = index_name

        if limit is not None:
            kwargs["Limit"] = limit

        if count_only is True:
            kwargs["Select"] = "COUNT"

        response = await loop.run_in_executor(
            None,
            lambda: table.query(**kwargs),
        )

        return QueryResult(
            items=response.get("Items", []),
            count=response.get("Count", 0),
        )

    async def scan(
        self: Self,
        table_name: str,
        limit: Optional[int] = None,
        start_key: Optional[Dict[str, Any]] = None,
    ) -> ScanResult:
        loop: AbstractEventLoop = asyncio.get_event_loop()
        table = self._resource.Table(self.__get_table_name(table_name))

        kwargs: Dict[str, Any] = {}

        if limit is not None:
            kwargs["Limit"] = limit

        if start_key is not None:
            kwargs["ExclusiveStartKey"] = start_key

        response = await loop.run_in_executor(
            None,
            lambda: table.scan(**kwargs),
        )

        return ScanResult(
            items=response.get("Items", []),
            last_evaluated_key=response.get("LastEvaluatedKey"),
        )


def get_dynamodb_nosql() -> DynamoDBNoSQL:
    return DynamoDBNoSQL()
