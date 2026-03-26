from fastapi import APIRouter, Depends, status
from typing import List, Dict, Any, Annotated


router: APIRouter = APIRouter(prefix="/index", tags=["indices"])