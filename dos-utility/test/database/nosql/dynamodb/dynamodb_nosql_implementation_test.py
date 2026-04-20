import pytest

from typing import List

from dos_utility.utils.aws import get_aws_credentials_settings
from dos_utility.database.nosql.models import KeyCondition, ConditionOperator
from dos_utility.database.nosql.dynamodb import implementation
from dos_utility.database.nosql.env import get_nosql_settings
from dos_utility.database.nosql.dynamodb.implementation import DynamoDBNoSQL, get_dynamodb_nosql
from dos_utility.database.nosql.dynamodb.implementation import boto3

from test.utils.aws.mocks import get_aws_credentials_settings_mock
from test.database.nosql.dynamodb.mocks import (
    get_dynamodb_settings_mock,
    get_dynamodb_settings_mock_no_prefix,
    boto3_dynamodb_resource_mock,
    boto3_dynamodb_resource_not_healthy_mock,
)


def test_dynamodb_nosql_initialization(monkeypatch: pytest.MonkeyPatch):
    get_aws_credentials_settings.cache_clear()
    get_nosql_settings.cache_clear()

    monkeypatch.setattr(implementation, "get_aws_credentials_settings", get_aws_credentials_settings_mock)
    monkeypatch.setattr(implementation, "get_dynamodb_settings", get_dynamodb_settings_mock)

    nosql: DynamoDBNoSQL = DynamoDBNoSQL()

    assert isinstance(nosql, DynamoDBNoSQL)

@pytest.mark.asyncio
async def test_dynamodb_nosql_aenter_aexit(monkeypatch: pytest.MonkeyPatch):
    get_aws_credentials_settings.cache_clear()
    get_nosql_settings.cache_clear()

    monkeypatch.setattr(implementation, "get_aws_credentials_settings", get_aws_credentials_settings_mock)
    monkeypatch.setattr(implementation, "get_dynamodb_settings", get_dynamodb_settings_mock)

    async with DynamoDBNoSQL() as nosql:
        assert isinstance(nosql, DynamoDBNoSQL)

    assert True

@pytest.mark.asyncio
async def test_dynamodb_nosql_is_healthy(monkeypatch: pytest.MonkeyPatch):
    get_aws_credentials_settings.cache_clear()
    get_nosql_settings.cache_clear()

    monkeypatch.setattr(implementation, "get_aws_credentials_settings", get_aws_credentials_settings_mock)
    monkeypatch.setattr(implementation, "get_dynamodb_settings", get_dynamodb_settings_mock)
    monkeypatch.setattr(boto3, "resource", boto3_dynamodb_resource_mock)

    async with DynamoDBNoSQL() as nosql:
        is_healthy: bool = await nosql.is_healthy()

    assert is_healthy is True

@pytest.mark.asyncio
async def test_dynamodb_nosql_is_not_healthy(monkeypatch: pytest.MonkeyPatch):
    get_aws_credentials_settings.cache_clear()
    get_nosql_settings.cache_clear()

    monkeypatch.setattr(implementation, "get_aws_credentials_settings", get_aws_credentials_settings_mock)
    monkeypatch.setattr(implementation, "get_dynamodb_settings", get_dynamodb_settings_mock)
    monkeypatch.setattr(boto3, "resource", boto3_dynamodb_resource_not_healthy_mock)

    async with DynamoDBNoSQL() as nosql:
        is_healthy: bool = await nosql.is_healthy()

    assert is_healthy is False

@pytest.mark.asyncio
async def test_dynamodb_nosql_put_item(monkeypatch: pytest.MonkeyPatch):
    get_aws_credentials_settings.cache_clear()
    get_nosql_settings.cache_clear()

    monkeypatch.setattr(implementation, "get_aws_credentials_settings", get_aws_credentials_settings_mock)
    monkeypatch.setattr(implementation, "get_dynamodb_settings", get_dynamodb_settings_mock)
    monkeypatch.setattr(boto3, "resource", boto3_dynamodb_resource_mock)

    async with DynamoDBNoSQL() as nosql:
        await nosql.put_item(table_name="test_table", item={"id": "123", "name": "Test Item"})

    assert True

@pytest.mark.asyncio
async def test_dynamodb_nosql_put_item_no_table_name_prefix(monkeypatch: pytest.MonkeyPatch):
    get_aws_credentials_settings.cache_clear()
    get_nosql_settings.cache_clear()

    monkeypatch.setattr(implementation, "get_aws_credentials_settings", get_aws_credentials_settings_mock)
    monkeypatch.setattr(implementation, "get_dynamodb_settings", get_dynamodb_settings_mock_no_prefix)
    monkeypatch.setattr(boto3, "resource", boto3_dynamodb_resource_mock)

    async with DynamoDBNoSQL() as nosql:
        await nosql.put_item(table_name="test_table", item={"id": "123", "name": "Test Item"})

    assert True

@pytest.mark.asyncio
async def test_dynamodb_nosql_get_item(monkeypatch: pytest.MonkeyPatch):
    get_aws_credentials_settings.cache_clear()
    get_nosql_settings.cache_clear()

    monkeypatch.setattr(implementation, "get_aws_credentials_settings", get_aws_credentials_settings_mock)
    monkeypatch.setattr(implementation, "get_dynamodb_settings", get_dynamodb_settings_mock)
    monkeypatch.setattr(boto3, "resource", boto3_dynamodb_resource_mock)

    async with DynamoDBNoSQL() as nosql:
        item: dict = await nosql.get_item(table_name="test_table", key={"id": "123"})

    assert item is not None

@pytest.mark.asyncio
async def test_dynamodb_nosql_delete_item(monkeypatch: pytest.MonkeyPatch):
    get_aws_credentials_settings.cache_clear()
    get_nosql_settings.cache_clear()

    monkeypatch.setattr(implementation, "get_aws_credentials_settings", get_aws_credentials_settings_mock)
    monkeypatch.setattr(implementation, "get_dynamodb_settings", get_dynamodb_settings_mock)
    monkeypatch.setattr(boto3, "resource", boto3_dynamodb_resource_mock)

    async with DynamoDBNoSQL() as nosql:
        await nosql.delete_item(table_name="test_table", key={"id": "123"})

    assert True

@pytest.mark.asyncio
async def test_dynamodb_nosql_update_item(monkeypatch: pytest.MonkeyPatch):
    get_aws_credentials_settings.cache_clear()
    get_nosql_settings.cache_clear()

    monkeypatch.setattr(implementation, "get_aws_credentials_settings", get_aws_credentials_settings_mock)
    monkeypatch.setattr(implementation, "get_dynamodb_settings", get_dynamodb_settings_mock)
    monkeypatch.setattr(boto3, "resource", boto3_dynamodb_resource_mock)

    async with DynamoDBNoSQL() as nosql:
        updated_item: dict = await nosql.update_item(
            table_name="test_table",
            key={"id": "123"},
            fields_to_update={"name": "Updated Test Item"},
        )

    assert updated_item is not None

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "key_conditions",
    [
        [
            KeyCondition(
                field="id",
                operator=ConditionOperator.EQ,
                value="123",
            ),
            KeyCondition(
                field="name",
                operator=ConditionOperator.BEGINS_WITH,
                value="Test",
            ),
        ],
        [
            KeyCondition(
                field="age",
                operator=ConditionOperator.GT,
                value=30,
            ),
        ],
        [
            KeyCondition(
                field="created_at",
                operator=ConditionOperator.BETWEEN,
                value="2023-01-01",
                second_value="2023-12-31",
            ),
        ],
        [
            KeyCondition(
                field="status",
                operator=ConditionOperator.LTE,
                value="active",
            ),
        ],
        [
            KeyCondition(
                field="score",
                operator=ConditionOperator.GTE,
                value=80,
            ),
        ],
        [
            KeyCondition(
                field="category",
                operator=ConditionOperator.LT,
                value="electronics",
            ),
        ],
    ],
)
async def test_dynamodb_nosql_query(monkeypatch: pytest.MonkeyPatch, key_conditions: List[KeyCondition]):
    get_aws_credentials_settings.cache_clear()
    get_nosql_settings.cache_clear()

    monkeypatch.setattr(implementation, "get_aws_credentials_settings", get_aws_credentials_settings_mock)
    monkeypatch.setattr(implementation, "get_dynamodb_settings", get_dynamodb_settings_mock)
    monkeypatch.setattr(boto3, "resource", boto3_dynamodb_resource_mock)

    async with DynamoDBNoSQL() as nosql:
        query_result = await nosql.query(
            table_name="test_table",
            key_conditions=key_conditions,
            index_name="test",
            limit=10,
            count_only=True,
        )

    assert query_result is not None

@pytest.mark.asyncio
async def test_dynamodb_nosql_scan(monkeypatch: pytest.MonkeyPatch):
    get_aws_credentials_settings.cache_clear()
    get_nosql_settings.cache_clear()

    monkeypatch.setattr(implementation, "get_aws_credentials_settings", get_aws_credentials_settings_mock)
    monkeypatch.setattr(implementation, "get_dynamodb_settings", get_dynamodb_settings_mock)
    monkeypatch.setattr(boto3, "resource", boto3_dynamodb_resource_mock)

    async with DynamoDBNoSQL() as nosql:
        scan_result = await nosql.scan(table_name="test_table", limit=10, start_key={"id": "123"})

    assert scan_result is not None

def test_get_dynamodb_nosql(monkeypatch: pytest.MonkeyPatch):
    get_aws_credentials_settings.cache_clear()
    get_nosql_settings.cache_clear()

    monkeypatch.setattr(implementation, "get_aws_credentials_settings", get_aws_credentials_settings_mock)
    monkeypatch.setattr(implementation, "get_dynamodb_settings", get_dynamodb_settings_mock)

    nosql: DynamoDBNoSQL = get_dynamodb_nosql()

    assert isinstance(nosql, DynamoDBNoSQL)