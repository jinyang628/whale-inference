from pydantic import BaseModel
from app.models.application import Column, PrimaryKey

from app.models.inference import InferenceRequest


class Preprocessor(BaseModel):
    def preprocess(self, input: InferenceRequest) -> InferenceRequest:
        copied_input = input.model_copy(deep=True) # I believe this is necessary if not the original copy will still be corrupted in main.py (which is necessary for post-processing)
        return _drop_id_column(input=copied_input)
        
    
def _drop_id_column(input: InferenceRequest):
    for application in input.applications:
        for table in application.tables:
            updated_table_columns: list[Column] = []
            for column in table.columns:
                if column.primary_key == PrimaryKey.AUTO_INCREMENT:
                    print(f"{column.name} column dropped from {table.name} table in {application.name} application")
                    continue
                updated_table_columns.append(column)
            table.columns = updated_table_columns
    return input