from typing import Annotated
from pydantic import BaseModel, Field

class MaskRequestBody(BaseModel):
    text: Annotated[str, Field(description="Text to mask")]
