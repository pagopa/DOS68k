from typing import Any, Dict, Self, Optional

from dos_utility.database.nosql.dynamodb.env import DynamoDBSettings


def get_dynamodb_settings_mock() -> DynamoDBSettings:
    return DynamoDBSettings(
        DYNAMODB_REGION="us-east-1",
        DYNAMODB_TABLE_PREFIX="test_",
        DYNAMODB_ENDPOINT_URL="http://localhost:8000",
        DYNAMODB_PORT=8000,
    )


def get_dynamodb_settings_mock_no_prefix() -> DynamoDBSettings:
    return DynamoDBSettings(
        DYNAMODB_REGION="us-east-1",
        DYNAMODB_TABLE_PREFIX=None,
        DYNAMODB_ENDPOINT_URL="http://localhost:8000",
        DYNAMODB_PORT=8000,
    )


class _MockBoto3Tables:
    def limit(self: Self, limit: int):
        return ["table1"]


class _MockBoto3TablesNotHealthy:
    def limit(self: Self, limit: int):
        raise Exception("Mocked exception")


class _MockBoto3Table:
    def put_item(self: Self, Item: Dict[str, Any]) -> None:
        pass

    def get_item(self: Self, Key: Dict[str, Any]) -> Dict[str, Any]:
        return {"Item": {"id": "123", "name": "Test Item"}}

    def delete_item(self: Self, Key: Dict[str, Any]) -> None:
        pass

    def update_item(
        self: Self,
        Key: Dict[str, Any],
        UpdateExpression: str,
        ExpressionAttributeNames: Dict[str, str],
        ExpressionAttributeValues: Dict[str, Any],
        ReturnValues: Optional[str] = None,
    ) -> Dict[str, Any]:
        return {"Attributes": {"id": "123", "name": "Updated Test Item"}}

    def query(
        self: Self,
        KeyConditionExpression: Any,
        ScanIndexForward: bool = True,
        Limit: Optional[int] = None,
        IndexName: Optional[str] = None,
        Select: Optional[str] = None,
    ) -> Dict[str, Any]:
        return {"Items": [{"id": "123", "name": "Test Item"}], "Count": 1}

    def scan(
        self: Self,
        Limit: Optional[int] = None,
        ExclusiveStartKey: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        return {"Items": [{"id": "123", "name": "Test Item"}], "LastEvaluatedKey": None}


class MockBoto3DynamoDBResource:
    def __init__(self, *args, **kwargs):
        self.tables: _MockBoto3Tables = _MockBoto3Tables()

    def Table(self: Self, table_name: str) -> _MockBoto3Table:
        return _MockBoto3Table()


class MockBoto3DynamoDBResourceNotHealthy:
    def __init__(self, *args, **kwargs):
        self.tables: _MockBoto3TablesNotHealthy = _MockBoto3TablesNotHealthy()


def boto3_dynamodb_resource_mock(*args, **kwargs) -> MockBoto3DynamoDBResource:
    return MockBoto3DynamoDBResource()


def boto3_dynamodb_resource_not_healthy_mock(
    *args, **kwargs
) -> MockBoto3DynamoDBResourceNotHealthy:
    return MockBoto3DynamoDBResourceNotHealthy()
