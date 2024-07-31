import logging
from typing import Optional

from app.exceptions.exception import InferenceFailure
from app.generator.base import Generator
from app.llm.model import LLMType
from app.models.application import ApplicationContent
from app.models.inference.create import CreateInferenceResponse, CreateMessage
from app.prompts.create.application.open_ai import (
    generate_openai_application_system_message,
    generate_openai_application_user_message,
)

log = logging.getLogger(__name__)


class ApplicationGenerator(Generator):
    def generate_system_message(self) -> str:
        match self._llm_type:
            case LLMType.OPENAI_GPT4:
                return generate_openai_application_system_message()
            case LLMType.OPENAI_GPT3_5:
                return generate_openai_application_system_message()
            case _:
                raise ValueError(f"Unsupported LLM type: {self._llm_type})")

    def generate_user_message(
        self, message: str, chat_history: list[CreateMessage]
    ) -> str:
        match self._llm_type:
            case LLMType.OPENAI_GPT4:
                return generate_openai_application_user_message(
                    message=message, chat_history=chat_history
                )
            case LLMType.OPENAI_GPT3_5:
                return generate_openai_application_user_message(
                    message=message, chat_history=chat_history
                )
            case _:
                raise ValueError(f"Unsupported LLM type: {self._llm_type})")

    async def generate(
        self, message: str, chat_history: list[CreateMessage]
    ) -> CreateInferenceResponse:
        system_message: str = self.generate_system_message()
        user_message = self.generate_user_message(
            message=message, chat_history=chat_history
        )

        try:
            last_application_draft: Optional[ApplicationContent] = None
            if chat_history:
                last_application_draft = chat_history[-1].application_content
            response: CreateInferenceResponse = (
                await self._model.send_application_message(
                    system_message=system_message,
                    user_message=user_message,
                    last_application_draft=last_application_draft,
                )
            )
            return response
        except InferenceFailure as e:
            log.error(f"Inference failure at selection step: {e}")
            raise e
        except Exception as e:
            log.error(f"Error in generating response: {e}")
            raise e
