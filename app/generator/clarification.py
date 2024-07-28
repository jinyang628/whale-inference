from app.exceptions.exception import InferenceFailure
from app.generator.base import Generator
from app.llm.model import LLMType
from app.models.application import ApplicationContent
from app.models.message import Message
from app.prompts.clarification.open_ai import (
    generate_openai_clarification_system_message,
    generate_openai_clarification_user_message,
)
import logging

log = logging.getLogger(__name__)

class ClarificationGenerator(Generator):
    def generate_system_message(self) -> str:
        match self._llm_type:
            case LLMType.OPENAI_GPT4:
                return generate_openai_clarification_system_message()
            case LLMType.OPENAI_GPT3_5:
                return generate_openai_clarification_system_message()
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
                return generate_openai_clarification_user_message(
                    applications=applications,
                    message=message,
                    chat_history=chat_history
                )
            case LLMType.OPENAI_GPT3_5:
                return generate_openai_clarification_user_message(
                    applications=applications,
                    message=message,
                    chat_history=chat_history
                )
            case _:
                raise ValueError(f"Unsupported LLM type: {self._llm_type})")

    async def generate(
        self, 
        applications: list[ApplicationContent], 
        message: str, 
        chat_history: list[Message]
    ) -> str:
        system_message: str = self.generate_system_message()
        user_message = self.generate_user_message(
            applications=applications, 
            message=message, 
            chat_history=chat_history   
        )
            
        try:
            response: str = await self._model.send_clarification_message(
                system_message=system_message,
                user_message=user_message,
            )
            return response
        except InferenceFailure as e:
            log.error(f"Inference failure at selection step: {e}")
            raise e
        except Exception as e:
            log.error(f"Error in generating response: {e}")
            raise e
