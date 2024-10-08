import logging

from app.exceptions.exception import InferenceFailure
from app.generator.base import Generator
from app.llm.model import LLMType
from app.models.application import ApplicationContent
from app.models.inference.use import SelectionResponse, UseMessage
from app.prompts.use.selection.open_ai import (
    generate_openai_selection_system_message,
    generate_openai_selection_user_message,
)

log = logging.getLogger(__name__)


class SelectionGenerator(Generator):
    def generate_system_message(self) -> str:
        match self._llm_type:
            case LLMType.OPENAI_GPT4:
                return generate_openai_selection_system_message()
            case LLMType.OPENAI_GPT3_5:
                return generate_openai_selection_system_message()
            case _:
                raise ValueError(f"Unsupported LLM type: {self._llm_type})")

    def generate_user_message(
        self,
        applications: list[ApplicationContent],
        message: str,
        chat_history: list[UseMessage],
    ) -> str:
        match self._llm_type:
            case LLMType.OPENAI_GPT4:
                return generate_openai_selection_user_message(
                    applications=applications,
                    message=message,
                    chat_history=chat_history,
                )
            case LLMType.OPENAI_GPT3_5:
                return generate_openai_selection_user_message(
                    applications=applications,
                    message=message,
                    chat_history=chat_history,
                )
            case _:
                raise ValueError(f"Unsupported LLM type: {self._llm_type})")

    async def generate(
        self,
        applications: list[ApplicationContent],
        message: str,
        chat_history: list[UseMessage],
    ) -> SelectionResponse:
        system_message: str = self.generate_system_message()
        user_message = self.generate_user_message(
            applications=applications, message=message, chat_history=chat_history
        )

        try:
            response: SelectionResponse = await self._model.send_selection_message(
                system_message=system_message,
                user_message=user_message,
                applications=applications,
            )
            return response
        except InferenceFailure as e:
            log.error(f"Inference failure at selection step: {e}")
            raise e
        except Exception as e:
            log.error(f"Error in generating response: {e}")
            raise e
