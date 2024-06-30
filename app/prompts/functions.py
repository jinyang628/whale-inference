from enum import StrEnum
from typing import Any

from app.models.application import ApplicationContent
from app.models.inference import HttpMethod

class SelectionFunctions(StrEnum):
    SELECT = "select"
    APPLICATION_NAME = "application_name"
    TABLES = "tables"
    HTTP_METHOD = "http_method"
    RELEVANT_PAIRS = "relevant_pairs"
    
def get_selection_function(
    applications: list[ApplicationContent]
) -> dict[str, Any]:
    
    function = {
        "type": "function",
        "function": {
            "name": SelectionFunctions.SELECT,
            "description": "Select the relevant (application, HTTP method) pairs that are necessary to perform the user's instruction.",
            "parameters": {
                "type": "object",
                "properties": {
                    SelectionFunctions.RELEVANT_PAIRS: {
                        "type": "array",
                        "description": "All the relevant (application, HTTP method) pairs.",
                        "items": {
                            "type": "object",
                            "properties": {
                                SelectionFunctions.APPLICATION_NAME: {
                                    "type": "string",
                                    "enum": [application.name for application in applications],
                                    "description": "The name of the application to use the HTTP method on."
                                },
                                SelectionFunctions.HTTP_METHOD: {
                                    "type": "string",
                                    "enum": [method.value for method in HttpMethod],
                                    "description": "The HTTP method to use on the application",
                                }
                            },
                            "required": [SelectionFunctions.APPLICATION_NAME, SelectionFunctions.HTTP_METHOD]
                        }
                    }
                }
            }
        }
    }
    
    return function

class HttpMethodFunctions(StrEnum):
    GET_HTTP_METHOD_PARAMETERS = "get_http_method_parameters"
    HTTP_METHODS = "http_methods"
    HTTP_METHOD = "http_method"
    APPLICATION_NAME = "application_name"
    UPDATED_COLUMNS = "updated_columns"
    INSERTED_ROW = "inserted_row"
    COLUMN_NAME = "column_name"
    COLUMN_VALUE = "column_value"
    TABLE_NAME = "table_name"
    FILTER_CONDITIONS = "filter_conditions"
    
def get_http_method_parameters_function(
    applications: list[ApplicationContent]
) -> dict[str, Any]:
        
    function = {
        "type": "function",
        "function": {
            "name": HttpMethodFunctions.GET_HTTP_METHOD_PARAMETERS,
            "description": "Generate the components of the HTTP methods based on the user's instructions and the available applications",
            "parameters": {
                "type": "object",
                "properties": {
                    HttpMethodFunctions.HTTP_METHODS: {
                        "type": "array",
                        "description": "A list of components of every HTTP method.",
                        "items": {
                            "type": "object",
                            "properties": {
                                HttpMethodFunctions.APPLICATION_NAME: {
                                    "type": "string",
                                    "enum": [application.name for application in applications],
                                    "description": "The name of the application to use the HTTP method on."
                                },
                                HttpMethodFunctions.HTTP_METHOD: {
                                    "type": "string",
                                    "enum": [method.value for method in HttpMethod],
                                    "description": "The HTTP method to use."
                                },
                                HttpMethodFunctions.TABLE_NAME: {
                                    "type": "string",
                                    "description": "The name of the table to use the HTTP method on. The table must belong to the application."
                                },
                                HttpMethodFunctions.INSERTED_ROW: {
                                    "type": "object",
                                    "description": "The row to insert into the table. Each property represents a column.",
                                    "properties": {},
                                    "patternProperties": {
                                        "^.*$": {
                                            "type": "string",
                                            "description": "The value for the column. Must conform to the column's data type."
                                        }
                                    }
                                },
                                HttpMethodFunctions.FILTER_CONDITIONS: {
                                    "type": "object",
                                    "description": "The filter conditions for GET, PUT and DELETE methods. Each property represents a column to filter on.",
                                    "properties": {},
                                    "patternProperties": {
                                        "^.*$": {
                                            "type": "string",
                                            "description": "The value to filter the column by. Must conform to the column's data type."
                                        }
                                    }
                                },
                                HttpMethodFunctions.UPDATED_COLUMNS: {
                                    "type": "object",
                                    "description": "The column values to update for the PUT method. Each property represents a column to update.",
                                    "properties": {},
                                    "patternProperties": {
                                        "^.*$": {
                                            "type": "string",
                                            "description": "The new value for the column. Must conform to the column's data type."
                                        }
                                    }
                                },
                            },
                            "required": [HttpMethodFunctions.APPLICATION_NAME, HttpMethodFunctions.HTTP_METHOD, HttpMethodFunctions.TABLE_NAME, HttpMethodFunctions.INSERTED_ROW]
                        }
                    }
                },
                "required": [HttpMethodFunctions.HTTP_METHODS]
            }
        }
    }
    
    return function    
    