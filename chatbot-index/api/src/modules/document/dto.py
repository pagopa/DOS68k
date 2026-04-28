from typing import Annotated
from pydantic import BaseModel, Field, ConfigDict


class UploadDocumentResponse(BaseModel):
    model_config: ConfigDict = ConfigDict(
        serialize_by_alias=True, validate_by_name=True
    )

    index_id: Annotated[str, Field(alias="indexId")]
    document_name: Annotated[str, Field(alias="documentName")]
    message: str


class DocumentInfo(BaseModel):
    model_config: ConfigDict = ConfigDict(
        serialize_by_alias=True, validate_by_name=True
    )

    document_name: Annotated[str, Field(alias="documentName")]
