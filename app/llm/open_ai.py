import json
from app.exceptions.exception import InferenceFailure
from app.llm.base import LLMBaseModel, LLMConfig
from openai import OpenAI
import os
import logging
from dotenv import load_dotenv
from app.models.application import ApplicationContent
from app.models.inference import SelectionResponse

from app.prompts.functions import HttpMethodFunctions, SelectionFunctions, get_http_method_parameters_function, get_selection_function

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
        
    async def send_selection_message(
        self,
        system_message: str,
        user_message: str,
        applications: list[ApplicationContent]
    ) -> SelectionResponse:
        log.info(f"Sending selection message to OpenAI")
        try:
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
            selection_response = SelectionResponse.model_validate(json_response)
            return selection_response
        except Exception as e:
            log.error(f"Error sending or processing selection message to OpenAI: {str(e)}")
            raise InferenceFailure("Error sending or processing selection message to OpenAI")


    async def send_http_request_message(
        self,
        system_message: str,
        user_message: str,
        applications: list[ApplicationContent]
    ) -> str:
        log.info(f"Sending http meethod message to OpenAI")
        try:
            response = self._client.chat.completions.create(
                model=self._model_name,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message},
                ],
                tools=[get_http_method_parameters_function(applications=applications)],
                tool_choice={
                    "type": "function",
                    "function": {
                        "name": HttpMethodFunctions.GET_HTTP_METHOD_PARAMETERS
                    }
                },
            )
            tool_call = response.choices[0].message.tool_calls[0]
            json_response: dict[str, str] = json.loads(tool_call.function.arguments)
            print("~~~LLM RESPONSE~~~")
            print(json_response)
            return json.dumps(json_response)
        except Exception as e:
            log.error(f"Error sending or processing http method message to OpenAI: {str(e)}")
            raise InferenceFailure("Error sending or processing http method message to OpenAI")
