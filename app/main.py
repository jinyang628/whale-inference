import logging

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from app.config import (
    APPLICATION_CONFIG,
    CLARIFICATION_CONFIG,
    HTTP_REQUEST_CONFIG,
    SELECTION_CONFIG,
)
from app.exceptions.exception import InferenceFailure
from app.generator.create.application import ApplicationGenerator
from app.generator.use.clarification import ClarificationGenerator
from app.generator.use.http_request import HttpRequestGenerator
from app.generator.use.selection import SelectionGenerator
from app.models.inference.create import CreateInferenceRequest, CreateInferenceResponse
from app.models.inference.use import (
    HttpMethodResponse,
    SelectionResponse,
    UseInferenceRequest,
    UseInferenceResponse,
)
from app.processor.postprocess import Postprocessor
from app.processor.preprocess import Preprocessor

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

app = FastAPI()


@app.post("/inference/use")
async def generate_use_response(input: UseInferenceRequest) -> JSONResponse:
    try:
        processed_input = Preprocessor().preprocess(input=input)
        log.info("PREPROCESS COMPLETE")
        log.info(processed_input)

        selection_generator = SelectionGenerator(config=SELECTION_CONFIG)
        selection_response: SelectionResponse = await selection_generator.generate(
            applications=processed_input.applications,
            message=processed_input.message,
            chat_history=processed_input.chat_history,
        )
        if not selection_response.relevant_groupings:
            clarification_generator = ClarificationGenerator(
                config=CLARIFICATION_CONFIG
            )
            clarification_response: str = await clarification_generator.generate(
                applications=processed_input.applications,
                message=processed_input.message,
                chat_history=processed_input.chat_history,
            )
            inference_response = UseInferenceResponse(
                response=[],
                clarification=clarification_response,
            )
            return JSONResponse(
                status_code=200,
                content=inference_response.model_dump(),
            )
        log.info("SELECTION COMPLETE")

        http_request_generator = HttpRequestGenerator(config=HTTP_REQUEST_CONFIG)
        http_method_response_lst: list[HttpMethodResponse] = (
            await http_request_generator.generate(
                applications=processed_input.applications,
                message=processed_input.message,
                chat_history=processed_input.chat_history,
                selection_response=selection_response,
            )
        )
        log.info("HTTP REQUEST COMPLETE")

        inference_response: UseInferenceResponse = Postprocessor().postprocess(
            input=http_method_response_lst,
            original_applications=input.applications,
        )
        log.info(inference_response)
        log.info("USE INFERENCE COMPLETE")

        return JSONResponse(
            status_code=200,
            content=inference_response.model_dump(),
        )
    except InferenceFailure as e:
        log.error(f"Inference failure: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        log.error(f"Unknown error in generating response: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/inference/create")
async def generate_use_response(input: CreateInferenceRequest) -> JSONResponse:
    try:
        application_generator = ApplicationGenerator(config=APPLICATION_CONFIG)
        inference_response: CreateInferenceResponse = (
            await application_generator.generate(
                message=input.message,
                chat_history=input.chat_history,
            )
        )
        log.info("CREATE INFERENCE COMPLETE")
        return JSONResponse(
            status_code=200,
            content=inference_response.model_dump(),
        )
    except InferenceFailure as e:
        log.error(f"Inference failure: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        log.error(f"Unknown error in generating response: {e}")
        raise HTTPException(status_code=500, detail=str(e))
