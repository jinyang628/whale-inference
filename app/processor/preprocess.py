from pydantic import BaseModel
import logging
from app.models.application import Column, PrimaryKey

from app.models.inference import InferenceRequest

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

class Preprocessor(BaseModel):
    def preprocess(self, input: InferenceRequest) -> InferenceRequest:
        return input
        # copied_input = input.model_copy(deep=True) # I believe this is necessary if not the original copy will still be corrupted in main.py (which is necessary for post-processing)
