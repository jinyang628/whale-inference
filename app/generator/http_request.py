from app.generator.base import Generator
from app.llm.model import LLMType
from app.models.application import Table
from app.models.inference import ApplicationContent, HttpMethod, InferenceResponse, SelectionResponse
from app.models.message import Message
from app.prompts.http_request.open_ai import (
    generate_openai_http_request_system_message,
    generate_openai_http_request_user_message,
)
import logging

log = logging.getLogger(__name__)

class HttpRequestGenerator(Generator):
    def generate_system_message(self, http_method: HttpMethod) -> str:
        match self._llm_type:
            case LLMType.OPENAI_GPT4:
                return generate_openai_http_request_system_message(http_method=http_method)
            case LLMType.OPENAI_GPT3_5:
                return generate_openai_http_request_system_message(http_method=http_method)
            case _:
                raise ValueError(f"Unsupported LLM type: {self._llm_type})")

    def generate_user_message(
        self, 
        application_name: str, 
        table: Table,
        http_method: HttpMethod,
        message: str, 
        chat_history: list[Message]
    ) -> str:
        match self._llm_type:
            case LLMType.OPENAI_GPT4:
                return generate_openai_http_request_user_message(
                    application_name=application_name,
                    table=table,
                    http_method=http_method,
                    message=message,
                    chat_history=chat_history
                )
            case LLMType.OPENAI_GPT3_5:
                return generate_openai_http_request_user_message(
                    application_name=application_name,
                    table=table,
                    http_method=http_method,
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
    ) -> list[InferenceResponse]:
        response_list = []
        for grouping in selection_response.relevant_groupings:
            application_name = grouping.application_name
            table_name = grouping.table_name
            http_method = grouping.http_method
            
            print(f"Application: {application_name}, Table: {table_name}, HTTP Method: {http_method}")
            
            application: ApplicationContent = next((app for app in applications if app.name == application_name))
            table: Table = next((table for table in application.tables if table.name == table_name))
            
            system_message: str = self.generate_system_message(http_method=http_method)
            user_message = self.generate_user_message(
                application_name=application_name,
                table=table,
                http_method=http_method,
                message=message, 
                chat_history=chat_history,
            )
            
            try:
                response: InferenceResponse = await self._model.send_http_request_message(
                    system_message=system_message,
                    user_message=user_message,
                    http_method=http_method,
                    table=table
                )
                response_list.append(response)
            except Exception as e:
                log.error(f"Error in generating response: {e}")
                raise e
        return response_list
