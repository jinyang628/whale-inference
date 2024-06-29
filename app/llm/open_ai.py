import json
from app.exceptions.exception import InferenceFailure
from app.llm.base import LLMBaseModel, LLMConfig
from openai import OpenAI
import os
import logging
from dotenv import load_dotenv

# from app.prompts.functions import Functions, get_response_function

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

    async def send_message(
        self,
        system_message: str,
        user_message: str,
    ) -> str:
        """Sends a message to the AI and returns the response."""
        log.info(f"Sending messages to OpenAI")
        try:
            response = self._client.chat.completions.create(
                model=self._model_name,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message},
                ],
                # tools=[get_response_function()],
                # tool_choice={"name": NotesFunctions.GET_NOTES},
            )
            try:
                json_response: dict[str, str] = json.loads(response.choices[0].message.function_call.arguments)
                print("~~~LLM RESPONSE~~~")
                print(json_response)
            except Exception as e:
                log.error(f"Error processing response from OpenAI: {str(e)}")
                raise InferenceFailure("Error processing OpenAI response")
        except Exception as e:
            log.error(f"Error sending message to OpenAI: {str(e)}")
            raise InferenceFailure("Error sending message to OpenAI")
