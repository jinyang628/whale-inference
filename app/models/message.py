from enum import StrEnum

from pydantic import BaseModel

class Role(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"

class Message(BaseModel):
    role: Role
    content: str
