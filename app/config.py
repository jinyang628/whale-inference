from pydantic import BaseModel

from app.llm.model import LLMType


class InferenceConfig(BaseModel):
    """The main class describing the inference configuration."""

    llm_type: LLMType = LLMType.OPENAI_GPT3_5
