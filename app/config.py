from pydantic import BaseModel

from app.llm.model import LLMType


class InferenceConfig(BaseModel):
    """The main class describing the inference configuration."""

    llm_type: LLMType = LLMType.OPENAI_GPT4


SELECTION_CONFIG = InferenceConfig(
    llm_type=LLMType.OPENAI_GPT4,
)

CLARIFICATION_CONFIG = InferenceConfig(
    llm_type=LLMType.OPENAI_GPT4,
)

HTTP_REQUEST_CONFIG = InferenceConfig(
    llm_type=LLMType.OPENAI_GPT4,
)

APPLICATION_CONFIG = InferenceConfig(
    llm_type=LLMType.OPENAI_GPT4,
)
