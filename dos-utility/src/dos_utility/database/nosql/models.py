from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Dict, List, Optional


class ConditionOperator(StrEnum):
    EQ = "eq"
    GT = "gt"
    LT = "lt"
    GTE = "gte"
    LTE = "lte"
    BEGINS_WITH = "begins_with"
    BETWEEN = "between"


@dataclass
class KeyCondition:
    field: str
    operator: ConditionOperator
    value: Any
    second_value: Any = None  # Used only for BETWEEN operator


@dataclass
class QueryResult:
    items: List[Dict[str, Any]]
    count: int


@dataclass
class ScanResult:
    items: List[Dict[str, Any]]
    last_evaluated_key: Optional[Dict[str, Any]]
