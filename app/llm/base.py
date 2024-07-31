from abc import ABC, abstractmethod
from dataclasses import dataclass

from pydantic import BaseModel

from app.models.application import ApplicationContent, Table
from app.models.inference.use import HttpMethod, HttpMethodResponse, SelectionResponse


class LLMConfig(BaseModel):
    temperature: float
    max_tokens: int


@dataclass
class LLMBaseModel(ABC):
    """Base class for all AI models."""

    _model_name: str
    _model_config: LLMConfig

    def __init__(self, model_name: str, model_config: LLMConfig):
        if not model_name:
            raise ValueError("Model name must be provided.")
        if not model_config:
            raise ValueError("Model config must be provided.")

        self._model_name = model_name
        self._model_config = model_config

    @abstractmethod
    async def send_http_request_message(
        self,
        system_message: str,
        user_message: str,
        application: ApplicationContent,
        http_method: HttpMethod,
        table: Table,
    ) -> HttpMethodResponse:
        """Sends a message to the AI and returns the response."""
        pass

    @abstractmethod
    async def send_selection_message(
        self,
        system_message: str,
        user_message: str,
        applications: list[ApplicationContent],
    ) -> SelectionResponse:
        """Sends a message to the AI and returns the response."""
        pass

    @abstractmethod
    async def send_clarification_message(
        self,
        system_message: str,
        user_message: str,
    ) -> str:
        """Sends a message to the AI and returns the response."""
        pass

    @property
    def model_config(self) -> LLMConfig:
        return self._model_config
