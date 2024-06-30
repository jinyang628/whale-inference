
from enum import StrEnum
from typing import Any
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

class SelectedPair(BaseModel):
    application_name: str
    http_method: HttpMethod
    
class SelectionResponse(BaseModel):
    relevant_pairs: list[SelectedPair]
    
class HttpMethodRequest(BaseModel):
    application: ApplicationContent
    http_method: str
    filter_conditions: dict[str, Any]
    
class InferenceResponse(BaseModel):
    content: str