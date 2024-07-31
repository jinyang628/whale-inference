import logging
from abc import ABC, abstractmethod
from typing import Any

from app.config import InferenceConfig
from app.llm.base import LLMBaseModel
from app.llm.model import LLM, LLMType

log = logging.getLogger(__name__)


class Generator(ABC):

    _llm_type: LLMType
    _model: LLMBaseModel
    _max_tokens: int

    def __init__(self, config: InferenceConfig):
        self._llm_type = config.llm_type
        self._model = LLM(model_type=self._llm_type).model
        self._max_tokens = self._model.model_config.max_tokens

    @abstractmethod
    def generate_system_message(self, *args, **kwargs) -> Any:
        pass

    @abstractmethod
    def generate_user_message(self, *args, **kwargs) -> Any:
        pass

    @abstractmethod
    def generate(self, *args, **kwargs) -> Any:
        pass
