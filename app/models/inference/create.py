from typing import Optional
from pydantic import BaseModel
from app.models.application import Table

from app.models.message import Message

class CreateInferenceRequest(BaseModel):
    message: str
    chat_history: list[Message]

class CreateInferenceResponse(BaseModel):
    name: Optional[str] = None
    tables: Optional[list[Table]] = None
    overview: Optional[str] = None
    clarification: Optional[str] = None
