from typing import Optional
from pydantic import BaseModel
from app.models.application import ApplicationContent

from app.models.message import Message

class CreateMessage(Message):
    application_content: Optional[ApplicationContent] = None
    
class CreateInferenceRequest(BaseModel):
    message: str
    chat_history: list[CreateMessage]

class CreateInferenceResponse(BaseModel):
    application_content: Optional[ApplicationContent] = None
    overview: Optional[str] = None
    clarification: Optional[str] = None
