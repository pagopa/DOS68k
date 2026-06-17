from typing import TypeAlias, Optional, Dict, Any, List
from pydantic import BaseModel

TraceId: TypeAlias = str


class Trace(BaseModel):
    id: TraceId
    name: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    input: Optional[str] = None
    output: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None


class Span(BaseModel):
    trace_id: TraceId
    name: str
    input: Optional[str] = None
    output: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class Score(BaseModel):
    trace_id: TraceId
    name: str
    value: float
    comment: Optional[str] = None
