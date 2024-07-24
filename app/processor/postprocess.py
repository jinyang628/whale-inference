from typing import Any
from pydantic import BaseModel
from app.models.application import ApplicationContent, Column, DataType

from app.models.inference import HttpMethodResponse, InferenceResponse
from app.prompts.functions import HttpMethodFunctions
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# TODO: Need some calibrator that checks for duplicate in the filter conditons/updated data/inserted_row + whether all the NECESSARY parameters of the HTTP request are filled out + INVALID parameters are kept empty 
class Postprocessor(BaseModel):
    def postprocess(self, input: list[HttpMethodResponse], original_applications: list[ApplicationContent]) -> InferenceResponse:
        http_method_response_lst: list[HttpMethodResponse] = []
        for http_method_response in input:
            result = _enforce_response_types(
                input=http_method_response,
            )
            result = _restore_application_schema(
                input=result,
                original_applications=original_applications,
            )
            
            http_method_response_lst.append(result)
            
        return InferenceResponse(
            response=http_method_response_lst,
        )
        
    
def _restore_application_schema(
    input: HttpMethodResponse, 
    original_applications: list[ApplicationContent]
)-> HttpMethodResponse:
    """We drop certain columns like id, created_at, updated_at, etc. in the preprocessing step as they are unhelpful for inference. This function restores the original schema of the application."""
    target_application_name: str = input.application.name
    for application in original_applications:
        if application.name == target_application_name:
            input.application = application
            break
    return input

def _enforce_response_types(
    input: HttpMethodResponse,
) -> HttpMethodResponse:
    if input.inserted_rows:
        log.info("Enforcing response types for inserted rows")
        input = _enforce_response_types_for_inserted_rows(
            input=input
        )
    if input.filter_conditions:
        log.info("Enforcing response types for filter conditions")
        input = _enforce_response_types_for_filter_conditions(
            input=input,
        )
    if input.updated_data:
        log.info("Enforcing response types for updated data")
        input = _enforce_response_types_for_updated_data(
            input=input,
        )
    return input
        
def _enforce_response_types_for_filter_conditions(
    input: HttpMethodResponse
) -> HttpMethodResponse:
    
    def validate_condition(
        condition: dict[str, Any],
        column_name_to_data_type: dict[str, DataType]
    ) -> dict[str]:
        if HttpMethodFunctions.BOOLEAN_CLAUSE in condition:
            validated_sub_conditions: list[dict[str, Any]] = []
            for sub_condition in condition[HttpMethodFunctions.CONDITIONS]:
                validated_sub_conditions.append(validate_condition(
                    condition=sub_condition,
                    column_name_to_data_type=column_name_to_data_type,
                ))
            condition[HttpMethodFunctions.CONDITIONS] = validated_sub_conditions
            return condition 
        
        else:
            column_name: str = condition[HttpMethodFunctions.COLUMN]
            column_value: Any = condition[HttpMethodFunctions.VALUE]
            match column_name_to_data_type[column_name]:
                case DataType.STRING:
                    if isinstance(column_value, list):
                        return {
                            HttpMethodFunctions.COLUMN: column_name, 
                            HttpMethodFunctions.OPERATOR: condition[HttpMethodFunctions.OPERATOR],
                            HttpMethodFunctions.VALUE: [str(value) for value in column_value]
                        }
                    else:
                        return {
                            HttpMethodFunctions.COLUMN: column_name, 
                            HttpMethodFunctions.OPERATOR: condition[HttpMethodFunctions.OPERATOR],
                            HttpMethodFunctions.VALUE: str(column_value)
                        }
                case DataType.INTEGER:
                    if isinstance(column_value, list):
                        return {
                            HttpMethodFunctions.COLUMN: column_name, 
                            HttpMethodFunctions.OPERATOR: condition[HttpMethodFunctions.OPERATOR],
                            HttpMethodFunctions.VALUE: [int(value) for value in column_value]
                        }
                    else:
                        return {
                            HttpMethodFunctions.COLUMN: column_name, 
                            HttpMethodFunctions.OPERATOR: condition[HttpMethodFunctions.OPERATOR],
                            HttpMethodFunctions.VALUE: int(column_value)
                        }
                case DataType.FLOAT:
                    if isinstance(column_value, list):
                        return {
                            HttpMethodFunctions.COLUMN: column_name, 
                            HttpMethodFunctions.OPERATOR: condition[HttpMethodFunctions.OPERATOR],
                            HttpMethodFunctions.VALUE: [float(value) for value in column_value]
                        }
                    else:
                        return {
                            HttpMethodFunctions.COLUMN: column_name, 
                            HttpMethodFunctions.OPERATOR: condition[HttpMethodFunctions.OPERATOR],
                            HttpMethodFunctions.VALUE: float(column_value)
                        }
                case DataType.BOOLEAN:
                    return {
                        HttpMethodFunctions.COLUMN: column_name, 
                        HttpMethodFunctions.OPERATOR: condition[HttpMethodFunctions.OPERATOR],
                        HttpMethodFunctions.VALUE: column_value
                    }
                case DataType.DATE:
                    return {
                        HttpMethodFunctions.COLUMN: column_name, 
                        HttpMethodFunctions.OPERATOR: condition[HttpMethodFunctions.OPERATOR],
                        HttpMethodFunctions.VALUE: column_value
                    }
                case DataType.DATETIME:
                    return {
                        HttpMethodFunctions.COLUMN: column_name, 
                        HttpMethodFunctions.OPERATOR: condition[HttpMethodFunctions.OPERATOR],
                        HttpMethodFunctions.VALUE: column_value
                    }
                case DataType.ENUM:
                    if isinstance(column_value, list):
                        return {
                            HttpMethodFunctions.COLUMN: column_name, 
                            HttpMethodFunctions.OPERATOR: condition[HttpMethodFunctions.OPERATOR],
                            HttpMethodFunctions.VALUE: [str(value) for value in column_value]
                        }
                    else:
                        return {
                            HttpMethodFunctions.COLUMN: column_name, 
                            HttpMethodFunctions.OPERATOR: condition[HttpMethodFunctions.OPERATOR],
                            HttpMethodFunctions.VALUE: str(column_value)
                        }
                case _:
                    raise ValueError(f"Data type {column_name_to_data_type[column_name]} is not supported")
        
        
    for table in input.application.tables:
        if table.name != input.table_name:
            continue
        table_columns: list[Column] = table.columns
        # Add id as a possible field to filter by
        table_columns.append(Column(name="id", data_type=DataType.INTEGER))
        
        column_name_to_data_type: dict[str, DataType] = {column.name: column.data_type for column in table_columns}
        
        validated_filter_conditions: dict[str, Any] = {}
        validated_filter_conditions[HttpMethodFunctions.BOOLEAN_CLAUSE] = input.filter_conditions[HttpMethodFunctions.BOOLEAN_CLAUSE]
                
        validated_conditions: list[dict[str, Any]] = []
        for condition in input.filter_conditions[HttpMethodFunctions.CONDITIONS]:
            validated_conditions.append(validate_condition(
                condition=condition,
                column_name_to_data_type=column_name_to_data_type,
            ))
        validated_filter_conditions[HttpMethodFunctions.CONDITIONS] = validated_conditions
                
        input.filter_conditions = validated_filter_conditions
        # The row(s) should only be updated in one table
        break
    return input
    

# Consider whether we should just use pydantic for this with a leaner definition of Table and Column
def _enforce_response_types_for_updated_data(
    input: HttpMethodResponse,
) -> HttpMethodResponse:    
    for table in input.application.tables:
        if table.name != input.table_name:
            continue
        table_columns: list[Column] = table.columns
        column_name_to_data_type: dict[str, DataType] = {column.name: column.data_type for column in table_columns}
        validated_updated_data: dict[str, Any] = {}
        for column_name, column_value in input.updated_data.items():
            match column_name_to_data_type[column_name]:
                case DataType.STRING:
                    if isinstance(column_value, list):
                        validated_updated_data[column_name] = [str(value) for value in column_value]
                    else:
                        validated_updated_data[column_name] = str(column_value)
                case DataType.INTEGER:
                    if isinstance(column_value, list):
                        validated_updated_data[column_name] = [int(value) for value in column_value]
                    else:
                        validated_updated_data[column_name] = int(column_value)
                case DataType.FLOAT:
                    if isinstance(column_value, list):
                        validated_updated_data[column_name] = [float(value) for value in column_value]  
                    else:
                        validated_updated_data[column_name] = float(column_value)
                case DataType.BOOLEAN:
                    validated_updated_data[column_name] = column_value
                case DataType.DATE:
                    validated_updated_data[column_name] = column_value
                case DataType.DATETIME:
                    validated_updated_data[column_name] = column_value
                case DataType.ENUM:
                    if isinstance(column_value, list):
                        validated_updated_data[column_name] = [str(value) for value in column_value]
                    else:
                        validated_updated_data[column_name] = str(column_value)
                case _:
                    raise ValueError(f"Data type {column_name_to_data_type[column_name]} is not supported.")
        input.updated_data = validated_updated_data
        # The row(s) should only be updated in one table
        break
    return input


# Consider whether we should just use pydantic for this with a leaner definition of Table and Column
def _enforce_response_types_for_inserted_rows(
    input: HttpMethodResponse,
) -> HttpMethodResponse:
    """User might define enums that LLMs might output non-string values for (e.g. '1', '2'). Enums in PostgreSQL are all strings so we need to stringify them."""
    for table in input.application.tables:
        if table.name != input.table_name:
            continue
        table_columns: list[Column] = table.columns
        column_name_to_data_type: dict[str, DataType] = {column.name: column.data_type for column in table_columns}
        validated_inserted_rows: list[dict[str, Any]] = []
        for row in input.inserted_rows:
            validated_inserted_row: dict[str, Any] = {}
            for column_name, column_value in row.items():
                match column_name_to_data_type[column_name]:
                    case DataType.STRING:
                        if isinstance(column_value, list):
                            validated_inserted_row[column_name] = [str(value) for value in column_value]
                        else:
                            validated_inserted_row[column_name] = str(column_value)
                    case DataType.INTEGER:
                        if isinstance(column_value, list):
                            validated_inserted_row[column_name] = [int(value) for value in column_value]
                        else:
                            validated_inserted_row[column_name] = int(column_value)
                    case DataType.FLOAT:
                        if isinstance(column_value, list):
                            validated_inserted_row[column_name] = [float(value) for value in column_value]
                        else:
                            validated_inserted_row[column_name] = float(column_value)
                    case DataType.BOOLEAN:
                        validated_inserted_row[column_name] = column_value
                    case DataType.DATE:
                        validated_inserted_row[column_name] = column_value
                    case DataType.DATETIME:
                        validated_inserted_row[column_name] = column_value
                    case DataType.ENUM:
                        if isinstance(column_value, list):
                            validated_inserted_row[column_name] = [str(value) for value in column_value]
                        else:
                            validated_inserted_row[column_name] = str(column_value)
                    case _:
                        raise ValueError(f"Data type {column_name_to_data_type[column_name]} is not supported.")
            validated_inserted_rows.append(validated_inserted_row)
        input.inserted_rows = validated_inserted_rows
        # The row should only be inserted into one table
        break
    return input