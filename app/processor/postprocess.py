from pydantic import BaseModel
from app.models.application import ApplicationContent, Column, PrimaryKey

from app.models.inference import HttpMethodResponse, InferenceRequest, InferenceResponse

# TODO: Need some calibrator that checks for duplicate in the filter conditons/updated data/inserted_row + whether all the NECESSARY parameters of the HTTP request are filled out + INVALID parameters are kept empty 
class Postprocessor(BaseModel):
    def postprocess(self, input: list[HttpMethodResponse], original_applications: list[ApplicationContent]) -> InferenceResponse:
        http_method_response_lst: list[HttpMethodResponse] = []
        for http_method_response in input:
            result: HttpMethodResponse = _recover_applications(
                input=http_method_response,
                original_applications=original_applications,
            )
            
            http_method_response_lst.append(result)
            
        return InferenceResponse(
            response=http_method_response_lst,
        )
        
    
def _recover_applications(input: HttpMethodResponse, original_applications: list[ApplicationContent]) -> HttpMethodResponse:
    target_application_name: str = input.application.name
    for application in original_applications:
        if application.name == target_application_name:
            input.application = application
            break
    return input