import logging

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from app.config import InferenceConfig
from app.generator.selection import SelectionGenerator
from app.generator.http_request import HttpRequestGenerator
from app.llm.model import LLMType
from app.models.inference import HttpMethodResponse, SelectionResponse, InferenceResponse, InferenceRequest
from app.processor.postprocess import Postprocessor
from app.processor.preprocess import Preprocessor

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
        processed_input = Preprocessor().preprocess(input=input)
        print("PREPROCESS COMPLETE")

        selection_generator = SelectionGenerator(config=SELECTION_CONFIG)
        selection_response: SelectionResponse = await selection_generator.generate(
            applications=processed_input.applications,
            message=processed_input.message,
            chat_history=processed_input.chat_history,
        )
        print("SELECTION COMPLETE")

        http_request_generator = HttpRequestGenerator(config=HTTP_REQUEST_CONFIG)
        http_method_response_lst: list[HttpMethodResponse] = await http_request_generator.generate(
            applications=processed_input.applications,
            message=processed_input.message,
            chat_history=processed_input.chat_history,
            selection_response=selection_response,
        )
        print("HTTP REQUEST COMPLETE")

        inference_response: InferenceResponse = Postprocessor().postprocess(
            input=http_method_response_lst,
            original_applications=input.applications,
        )
        print(input.applications)
        print(inference_response)
        print("POST PROCESS COMPLETE")
        
        
        return JSONResponse(    
            status_code=200,
            content=inference_response.model_dump(),
        )
    except Exception as e:
        log.error(f"Error in generating response: {e}")
        raise HTTPException(status_code=500, detail=str(e))
