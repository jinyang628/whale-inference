
from enum import StrEnum
from typing import Any, Optional
from pydantic import BaseModel
from app.models.application import ApplicationContent

from app.models.message import Message

class HttpMethod(StrEnum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    
class InferenceRequest(BaseModel):
    applications: list[ApplicationContent]
    message: str
    chat_history: list[Message]

class SelectedGrouping(BaseModel):
    application_name: str
    table_name: str
    http_method: HttpMethod
    
class SelectionResponse(BaseModel):
    relevant_groupings: list[SelectedGrouping]
    
class HttpMethodRequest(BaseModel):
    application: ApplicationContent
    http_method: HttpMethod
    filter_conditions: dict[str, Any]
    
# TODO: Consider splitting this up instead of jumbling all the response shape tgt under one class (but need think about what schema it will be when we return to backend)
class InferenceResponse(BaseModel):
    http_method: HttpMethod
    inserted_row: Optional[dict[str, Any]] = None
    filter_conditions: Optional[list[dict[str, Any]]] = None
    updated_data: Optional[list[dict[str, Any]]] = None
    