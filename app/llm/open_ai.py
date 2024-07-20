import json
from app.exceptions.exception import InferenceFailure
from app.llm.base import LLMBaseModel, LLMConfig
from openai import OpenAI
import os
import logging
from dotenv import load_dotenv
from app.models.application import ApplicationContent, Table
from app.models.inference import HttpMethod, HttpMethodResponse, SelectionResponse

from app.prompts.functions import HttpMethodFunctions, SelectionFunctions, get_http_method_parameters_function, get_selection_function

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

load_dotenv()

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")


class OpenAi(LLMBaseModel):
    """This class handles the interaction with OpenAI API."""

    def __init__(self, model_name: str, model_config: LLMConfig):
        super().__init__(model_name=model_name, model_config=model_config)
        self._client = OpenAI(
            api_key=OPENAI_API_KEY,
        )
        
    # TODO: Ensure that the order of the pairs are correct. Sometimes order matters. E.g. PUT -> GET
    # TODO: Consider splitting the selection step of tables separately. Currently: (Application, Table Name, HTTP Method) -> To consider: (Application, HTTP Method) + (Table Name). This allows us to use enums for the function calling schema for table name.
    async def send_selection_message(
        self,
        system_message: str,
        user_message: str,
        applications: list[ApplicationContent]
    ) -> SelectionResponse:
        log.info(f"Sending selection message to OpenAI")
        try:
            log.info(system_message)
            log.info(user_message)
            response = self._client.chat.completions.create(
                model=self._model_name,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message},
                ],
                tools=[get_selection_function(applications=applications)],
                tool_choice={
                    "type": "function",
                    "function": {
                        "name": SelectionFunctions.SELECT
                    }
                },
            )
            tool_call = response.choices[0].message.tool_calls[0]
            json_response: dict[str, str] = json.loads(tool_call.function.arguments)
            log.info(f"Initial Selection Response: {json_response}")
            if not json_response:
                json_response = {"relevant_groupings": None}

            selection_response = SelectionResponse.model_validate(json_response)
            log.info(selection_response)
            return selection_response
        except Exception as e:
            log.error(f"Error sending or processing selection message to OpenAI: {str(e)}")
            raise InferenceFailure("Error sending or processing selection message to OpenAI")


    async def send_http_request_message(
        self,
        system_message: str,
        user_message: str,
        application: ApplicationContent,
        http_method: HttpMethod,
        table: Table
    ) -> HttpMethodResponse:
        log.info(f"Sending http method message to OpenAI")
        try:
            response = self._client.chat.completions.create(
                model=self._model_name,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message},
                ],
                tools=[get_http_method_parameters_function(http_method=http_method, table=table)],
                tool_choice={
                    "type": "function",
                    "function": {
                        "name": HttpMethodFunctions.GET_HTTP_METHOD_PARAMETERS
                    }
                },
            )
            tool_call = response.choices[0].message.tool_calls[0]
            json_response: dict[str, str] = json.loads(tool_call.function.arguments)
            log.info(f"Initial HTTP Request Response: {json_response}")
            
            json_response["http_method"] = http_method
            json_response["application"] = application.model_dump()
            json_response["table_name"] = table.name
            http_method_response = HttpMethodResponse.model_validate(json_response)
            log.info(http_method_response)
            return http_method_response
        except Exception as e:
            log.error(f"Error sending or processing http method message to OpenAI: {str(e)}")
            raise InferenceFailure("Error sending or processing http method message to OpenAI")

    async def send_clarification_message(
        self,
        system_message: str,
        user_message: str,
    ) -> str:
        log.info(f"Sending clarification message to OpenAI")
        try:
            response = self._client.chat.completions.create(
                model=self._model_name,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message},
                ],
            )
            clarification_response: str = response.choices[0].message.content
            log.info(f"Clarification question: {clarification_response}")
            return clarification_response
        except Exception as e:
            log.error(f"Error sending or processing clarification message to OpenAI: {str(e)}")
            raise InferenceFailure("Error sending or processing clarification message to OpenAI")