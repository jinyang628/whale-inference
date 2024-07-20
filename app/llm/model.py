from dataclasses import dataclass
from enum import StrEnum
from typing import Optional

from app.llm.base import LLMBaseModel, LLMConfig
from app.llm.open_ai import OpenAi


class LLMType(StrEnum):
    OPENAI_GPT4 = "gpt-4o-mini-2024-07-18"
    OPENAI_GPT3_5 = "gpt-3.5-turbo-0125"

    def default_config(self) -> LLMConfig:
        if self == LLMType.OPENAI_GPT4:
            return LLMConfig(
                temperature=1,
                max_tokens=3000,
            )
        elif self == LLMType.OPENAI_GPT3_5:
            return LLMConfig(
                temperature=1,
                max_tokens=3000,
            )
        raise ValueError(f"Unsupported LLM type: {self}")


@dataclass
class LLM:
    """Wrapper class for the LLM models."""

    _model: LLMBaseModel

    def __init__(
        self,
        model_type: LLMType,
        model_config: Optional[LLMConfig] = None,
    ):
        model_config: LLMConfig = model_config or model_type.default_config()
        match model_type:
            case LLMType.OPENAI_GPT4:
                self._model = OpenAi(
                    model_name=model_type.value, model_config=model_config
                )
            case LLMType.OPENAI_GPT3_5:
                self._model = OpenAi(
                    model_name=model_type.value, model_config=model_config
                )

    @property
    def model(self) -> LLMBaseModel:
        return self._model
