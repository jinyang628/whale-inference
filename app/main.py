import logging
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from app.config import InferenceConfig
from app.generator.selection import SelectionGenerator
from app.generator.http_request import HttpRequestGenerator
from app.llm.model import LLMType
from app.models.inference import HttpMethodResponse, SelectionResponse, InferenceResponse, InferenceRequest

log = logging.getLogger(__name__)

app = FastAPI()

SELECTION_CONFIG = InferenceConfig(
    llm_type=LLMType.OPENAI_GPT3_5,
) 

HTTP_REQUEST_CONFIG = InferenceConfig(
    llm_type=LLMType.OPENAI_GPT3_5,
)

@app.post("/inference")
async def generate_response(input: InferenceRequest) -> JSONResponse:
    try:
        selection_generator = SelectionGenerator(config=SELECTION_CONFIG)
        selection_response: SelectionResponse = await selection_generator.generate(
            applications=input.applications,
            message=input.message,
            chat_history=input.chat_history,
        )
        http_request_generator = HttpRequestGenerator(config=HTTP_REQUEST_CONFIG)
        print("SELECTION COMPLETE")
        http_method_response_lst: list[HttpMethodResponse] = await http_request_generator.generate(
            applications=input.applications,
            message=input.message,
            chat_history=input.chat_history,
            selection_response=selection_response,
        )
        print("INFERENCE COMPLETE")
        # TODO: Need some calibration step that checks for duplicate in the filter conditons/updated data/inserted_row + whether all the NECESSARY parameters of the HTTP request are filled out + INVALID parameters are kept empty 
        inference_response = InferenceResponse(
            response=http_method_response_lst,
        )
        return JSONResponse(    
            status_code=200,
            content=inference_response.model_dump(),
        )
    except Exception as e:
        log.error(f"Error in generating response: {e}")
        raise HTTPException(status_code=500, detail=str(e))
