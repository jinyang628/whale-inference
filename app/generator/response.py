from typing import Optional
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from app.config import InferenceConfig
from app.llm.base import LLMBaseModel
from app.llm.model import LLM, LLMType
from app.models.inference import ApplicationContent
from app.models.message import Message
from app.prompts.open_ai import (
    generate_openai_system_message,
    generate_openai_user_message,
)
from pathlib import Path
import os
import logging

log = logging.getLogger(__name__)

CHROMA_PATH = Path(os.path.abspath("app/data/chroma"))
RELEVANCE_SCORE_CEILING = 0.7

class ResponseGenerator:

    _llm_type: LLMType
    _model: LLMBaseModel
    _max_tokens: int

    def __init__(self, config: InferenceConfig):
        self._llm_type = config.llm_type
        self._model = LLM(model_type=self._llm_type).model
        self._max_tokens = self._model.model_config.max_tokens

    def generate_system_message(self) -> str:
        match self._llm_type:
            case LLMType.OPENAI_GPT4:
                return generate_openai_system_message()
            case LLMType.OPENAI_GPT3_5:
                return generate_openai_system_message()
            case _:
                raise ValueError(f"Unsupported LLM type: {self._llm_type})")

    def generate_user_message(
        self, 
        applications: list[ApplicationContent], 
        message: str, 
        chat_history: list[Message]
    ) -> str:
        match self._llm_type:
            case LLMType.OPENAI_GPT4:
                return generate_openai_user_message(
                    applications=applications,
                    message=message,
                    chat_history=chat_history
                )
            case LLMType.OPENAI_GPT3_5:
                return generate_openai_user_message(
                    applications=applications,
                    message=message,
                    chat_history=chat_history
                )
            case _:
                raise ValueError(f"Unsupported LLM type: {self._llm_type})")

    async def generate(
        self, applications: list[ApplicationContent], message: str, chat_history: list[Message]
    ) -> str:
        print(applications)
        print(message)
        print(chat_history)
        system_message: str = self.generate_system_message()
        print(system_message)
        user_message = self.generate_user_message(
            applications=applications, 
            message=message, 
            chat_history=chat_history   
        )
        print(user_message)
            
    #     try:
    #         response: str = await self._model.send_message(
    #             system_message=system_message,
    #             user_message=user_message,
    #         )
    #         return MessageResponse(content=response, agent=agent, is_rag=(context is not None))
    #     except Exception as e:
    #         log.error(f"Error in generating response: {e}")
    #         raise e
