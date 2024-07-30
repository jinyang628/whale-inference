import json
from typing import Optional
from app.exceptions.exception import InferenceFailure
from app.llm.base import LLMBaseModel, LLMConfig
from openai import OpenAI
import os
import logging
from dotenv import load_dotenv
from app.models.application import ApplicationContent, Table
from app.models.inference.create import CreateInferenceResponse
from app.models.inference.use import HttpMethod, HttpMethodResponse, SelectionResponse
from app.prompts.create.functions import ApplicationFunction, clarify, conclude, create_application

from app.prompts.use.functions import HttpMethodFunction, SelectionFunction, get_http_method_parameters_function, get_selection_function

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
                        "name": SelectionFunction.SELECT
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
                        "name": HttpMethodFunction.GET_HTTP_METHOD_PARAMETERS
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
    
    async def send_application_message(
        self,
        system_message: str,
        user_message: str,
        last_application_draft: Optional[ApplicationContent]
    ) -> CreateInferenceResponse:
        log.info(f"Sending application message to OpenAI")
        try:
            available_tools = [create_application(), clarify(), conclude()] if last_application_draft else [create_application(), clarify()]
            response = self._client.chat.completions.create(
                model=self._model_name,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message},
                ],
                tools=available_tools,
            )
            log.info(response)
            # TODO: Known issue that sometimes it outputs a clarification question but does not choose the correct tool. Need to handle this case somehow
            # TEMP SOLUTION: If the tool is not selected, then we treat it as a clarification question
            tool_call = response.choices[0].message.tool_calls[0]
                
            tool_name = tool_call.function.name
            log.info(f"Tool called: {tool_name}")
            json_response: dict[str, str] = json.loads(tool_call.function.arguments)
            log.info(f"Initial Application Creation Response: {json_response}")
            match tool_name:
                case ApplicationFunction.CREATE_APPLICATION:
                    # Ensure that the application name is in the correct format
                    if json_response.get(ApplicationFunction.APPLICATION_CONTENT) and json_response.get(ApplicationFunction.APPLICATION_CONTENT).get(ApplicationFunction.NAME):
                        json_response[ApplicationFunction.APPLICATION_CONTENT][ApplicationFunction.NAME] = json_response[ApplicationFunction.APPLICATION_CONTENT][ApplicationFunction.NAME].replace(" ", "_").lower()
                        
                    # Ensure that the table and column names are in the correct format
                    if json_response.get(ApplicationFunction.APPLICATION_CONTENT) and json_response.get(ApplicationFunction.APPLICATION_CONTENT).get(ApplicationFunction.TABLES):
                        for table in json_response[ApplicationFunction.APPLICATION_CONTENT][ApplicationFunction.TABLES]:
                            table[ApplicationFunction.NAME] = table[ApplicationFunction.NAME].replace(" ", "_").lower()
                            for column in table[ApplicationFunction.COLUMNS]:
                                column[ApplicationFunction.NAME] = column[ApplicationFunction.NAME].replace(" ", "_").lower()
                    
                    # LLM keep putting this additional Primary Key column at the application level when it should be a per table parameter
                    if json_response.get(ApplicationFunction.APPLICATION_CONTENT) and json_response.get(ApplicationFunction.APPLICATION_CONTENT).get(ApplicationFunction.PRIMARY_KEY):
                        del json_response[ApplicationFunction.APPLICATION_CONTENT][ApplicationFunction.PRIMARY_KEY]
                        
                    # LLM keep putting this overview at the application level when it should be not nested
                    if json_response.get(ApplicationFunction.APPLICATION_CONTENT) and json_response.get(ApplicationFunction.APPLICATION_CONTENT).get(ApplicationFunction.OVERVIEW):
                        json_response[ApplicationFunction.OVERVIEW] = json_response.get(ApplicationFunction.APPLICATION_CONTENT).get(ApplicationFunction.OVERVIEW)
                        del json_response[ApplicationFunction.APPLICATION_CONTENT][ApplicationFunction.OVERVIEW]
                    
                    # LLM keep putting this clarification at the application level when it should be not nested
                    if json_response.get(ApplicationFunction.APPLICATION_CONTENT) and json_response.get(ApplicationFunction.APPLICATION_CONTENT).get(ApplicationFunction.CLARIFICATION):
                        json_response[ApplicationFunction.CLARIFICATION] = json_response.get(ApplicationFunction.APPLICATION_CONTENT).get(ApplicationFunction.CLARIFICATION)
                        del json_response[ApplicationFunction.APPLICATION_CONTENT][ApplicationFunction.CLARIFICATION]
                case ApplicationFunction.CLARIFY:
                    pass
                case ApplicationFunction.CONCLUDE:
                    json_response[ApplicationFunction.APPLICATION_CONTENT] = last_application_draft.model_dump()
                case _:
                    raise ValueError(f"Unsupported tool name: {tool_name}")
            
            response = CreateInferenceResponse.model_validate(json_response)
            log.info(response)
            return response
        except Exception as e:
            log.error(f"Error sending or processing application message to OpenAI: {str(e)}")
            raise InferenceFailure("Error sending or processing application message to OpenAI"
    )