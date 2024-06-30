from app.config import InferenceConfig
from app.llm.base import LLMBaseModel
from app.llm.model import LLM, LLMType
from app.models.inference import ApplicationContent, InferenceResponse
from app.models.message import Message
from app.prompts.http_REQUEST.open_ai import (
    generate_openai_http_method_system_message,
    generate_openai_http_method_user_message,
)
import logging

log = logging.getLogger(__name__)

class HttpMethodGenerator:

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
                return generate_openai_http_method_system_message()
            case LLMType.OPENAI_GPT3_5:
                return generate_openai_http_method_system_message()
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
                return generate_openai_http_method_user_message(
                    applications=applications,
                    message=message,
                    chat_history=chat_history
                )
            case LLMType.OPENAI_GPT3_5:
                return generate_openai_http_method_user_message(
                    applications=applications,
                    message=message,
                    chat_history=chat_history
                )
            case _:
                raise ValueError(f"Unsupported LLM type: {self._llm_type})")

    async def generate(
        self, applications: list[ApplicationContent], message: str, chat_history: list[Message]
    ) -> InferenceResponse:
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
