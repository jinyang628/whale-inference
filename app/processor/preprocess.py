import logging

from pydantic import BaseModel

from app.models.inference.use import UseInferenceRequest

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class Preprocessor(BaseModel):
    def preprocess(self, input: UseInferenceRequest) -> UseInferenceRequest:
        return input
        # copied_input = input.model_copy(deep=True) # I believe this is necessary if not the original copy will still be corrupted in main.py (which is necessary for post-processing)
