from app.generator.base import Generator
from app.llm.model import LLMType
from app.models.inference import ApplicationContent, InferenceResponse, SelectionResponse
from app.models.message import Message
from app.prompts.http_request.open_ai import (
    generate_openai_http_request_system_message,
    generate_openai_http_request_user_message,
)
import logging

log = logging.getLogger(__name__)

class HttpRequestGenerator(Generator):
    def generate_system_message(self) -> str:
        match self._llm_type:
            case LLMType.OPENAI_GPT4:
                return generate_openai_http_request_system_message()
            case LLMType.OPENAI_GPT3_5:
                return generate_openai_http_request_system_message()
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
                return generate_openai_http_request_user_message(
                    applications=applications,
                    message=message,
                    chat_history=chat_history
                )
            case LLMType.OPENAI_GPT3_5:
                return generate_openai_http_request_user_message(
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
        chat_history: list[Message],
        selection_response: SelectionResponse
    ) -> InferenceResponse:
        target 
        for application_name, http_method in selection_response.relevant_pairs:
            
        system_message: str = self.generate_system_message()
        user_message = self.generate_user_message(
            applications=applications, 
            message=message, 
            chat_history=chat_history   
        )
            
        try:
            response: InferenceResponse = await self._model.send_http_request_message(
                system_message=system_message,
                user_message=user_message,
                applications=applications
            )
            return response
        except Exception as e:
            log.error(f"Error in generating response: {e}")
            raise e
