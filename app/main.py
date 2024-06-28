import logging

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from app.config import InferenceConfig
from app.generator.response import ResponseGenerator
from app.models.message import MessageResponse, MessageRequest

log = logging.getLogger(__name__)

app = FastAPI()


@app.post("/inference")
async def generate_response(input: MessageRequest) -> JSONResponse:
    try:
        config = InferenceConfig()
        generator = ResponseGenerator(config=config)
        result: MessageResponse = await generator.generate(
            message=input.message,
            chat_history=input.chat_history,
            agent=input.agent,
        )
        return JSONResponse(
            status_code=200,
            content=result.model_dump(),
        )
    except Exception as e:
        log.error(f"Error in generating response: {e}")
        raise HTTPException(status_code=500, detail=str(e))
