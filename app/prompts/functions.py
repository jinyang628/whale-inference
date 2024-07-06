from enum import StrEnum
from typing import Any

from app.models.application import ApplicationContent, Column, Table
from app.models.inference import HttpMethod

class SelectionFunctions(StrEnum):
    SELECT = "select"
    TASK = "task"
    APPLICATION_NAME = "application_name"
    TABLE_NAME = "table_name"
    HTTP_METHOD = "http_method"
    RELEVANT_GROUPINGS = "relevant_groupings"
    
def get_selection_function(
    applications: list[ApplicationContent]
) -> dict[str, Any]:
    
    function = {
        "type": "function",
        "function": {
            "name": SelectionFunctions.SELECT,
            "description": "Select the relevant (task, application, table name, HTTP method) groupings that are necessary to perform the user's instruction.",
            "parameters": {
                "type": "object",
                "properties": {
                    SelectionFunctions.RELEVANT_GROUPINGS: {
                        "type": "array",
                        "description": "All the relevant (task, application, table name, HTTP method) groupings.",
                        "items": {
                            "type": "object",
                            "properties": {
                                SelectionFunctions.TASK: {
                                    "type": "string",
                                    "description": "This task represents a single step in the entire user instruction."
                                },
                                SelectionFunctions.APPLICATION_NAME: {
                                    "type": "string",
                                    "enum": [application.name for application in applications],
                                    "description": "The name of the application to use the HTTP method on."
                                },
                                SelectionFunctions.TABLE_NAME: {
                                    "type": "string",
                                    "description": "The table name of the application to use the HTTP method on.",
                                },
                                SelectionFunctions.HTTP_METHOD: {
                                    "type": "string",
                                    "enum": [method.value for method in HttpMethod],
                                    "description": "The HTTP method to use on the chosen application's table",
                                }
                            },
                            "required": [SelectionFunctions.TASK, SelectionFunctions.APPLICATION_NAME, SelectionFunctions.TABLE_NAME, SelectionFunctions.HTTP_METHOD]
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
    UPDATED_DATA = "updated_data"
    INSERTED_ROWS = "inserted_rows"
    TARGET_ROW = "target_row"
    COLUMN_NAME = "column_name"
    COLUMN_VALUE = "column_value"
    TABLE_NAME = "table_name"
    FILTER_CONDITIONS = "filter_conditions"
    
def get_http_method_parameters_function(
    http_method: HttpMethod,
    table: Table
) -> dict[str, Any]:
    match http_method:
        case HttpMethod.GET:
            return _get_get_http_method_parameters_function(columns=table.columns)
        case HttpMethod.POST:
            return _get_post_http_method_parameters_function(columns=table.columns)
        case HttpMethod.PUT:
            return _get_put_http_method_parameters_function(columns=table.columns)
        case HttpMethod.DELETE:
            return _get_delete_http_method_parameters_function(columns=table.columns)
        
def _get_post_http_method_parameters_function(columns: list[Column]) -> dict[str, Any]:
    function = {
        "type": "function",
        "function": {
            "name": HttpMethodFunctions.GET_HTTP_METHOD_PARAMETERS,
            "description": f"Generate the parameters of the {HttpMethod.POST} request based on the user's instruction and the table's schema",
            "parameters": {
                "type": "object",
                "properties": {
                    HttpMethodFunctions.INSERTED_ROWS: {
                        "type": "array",
                        "description": "A list of rows to be inserted",
                        "items": {
                            "type": "object",
                            "properties": {
                                column.name: {
                                    "type": ["string", "number", "boolean", "null"],
                                    "description": f"The value for the {column.name} column in the inserted row. Make sure that the value is of the same type as the column's data type."
                                } for column in columns
                            },
                            "required": [column.name for column in columns if not column.nullable]
                        }
                    }
                },
                "required": [HttpMethodFunctions.INSERTED_ROWS]
            }
        }
    }
    
    return function

def _get_delete_http_method_parameters_function(columns: list[Column]) -> dict[str, Any]:
    function = {
        "type": "function",
        "function": {
            "name": HttpMethodFunctions.GET_HTTP_METHOD_PARAMETERS,
            "description": f"Generate the parameters of the {HttpMethod.DELETE} request(s) based on the user's instruction and the table's schema",
            "parameters": {
                "type": "object",
                "properties": {
                    HttpMethodFunctions.FILTER_CONDITIONS: {
                        "type": "array",
                        "description": f"A list of specifications that filters for the rows to delete in the {HttpMethod.DELETE} request",
                        "items": {
                            "type": "object",
                            "properties": {
                                HttpMethodFunctions.COLUMN_NAME: {
                                    "type": "string",
                                    "enum": [column.name for column in columns],
                                    "description": "The name of the column that will be used to filter for the row to delete."
                                },
                                HttpMethodFunctions.COLUMN_VALUE: {
                                    "type": ["string", "number", "boolean", "null"],
                                    "description": "The value of the column that will be used to filter for the row to delete. Make sure that the value is of the same type as the column's data type."
                                }
                            },
                            "required": [HttpMethodFunctions.COLUMN_NAME, HttpMethodFunctions.COLUMN_VALUE]
                        }
                    }
                },
                "required": [HttpMethodFunctions.FILTER_CONDITIONS]
            }
        }
    }
    
    return function

def _get_get_http_method_parameters_function(columns: list[Column]) -> dict[str, Any]:
    
    function = {
        "type": "function",
        "function": {
            "name": HttpMethodFunctions.GET_HTTP_METHOD_PARAMETERS,
            "description": f"Generate the parameters of the {HttpMethod.GET} request(s) based on the user's instruction and the table's schema",
            "parameters": {
                "type": "object",
                "properties": {
                    HttpMethodFunctions.FILTER_CONDITIONS: {
                        "type": "array",
                        "description": f"A list of specifications that filters for the rows to get in the {HttpMethod.GET} request",
                        "items": {
                            "type": "object",
                            "properties": {
                                HttpMethodFunctions.COLUMN_NAME: {
                                    "type": "string",
                                    "enum": [column.name for column in columns],
                                    "description": "The name of the column that will be used to filter for the row to get."
                                },
                                HttpMethodFunctions.COLUMN_VALUE: {
                                    "type": ["string", "number", "boolean", "null"],
                                    "description": "The value of the column that will be used to filter for the row to get. Make sure that the value is of the same type as the column's data type."
                                }
                            },
                            "required": [HttpMethodFunctions.COLUMN_NAME, HttpMethodFunctions.COLUMN_VALUE]
                        }
                    }
                },
                "required": [HttpMethodFunctions.FILTER_CONDITIONS]
            }
        }
    }
    
    return function

def _get_put_http_method_parameters_function(columns: list[Column]) -> dict[str, Any]:
    function = {
        "type": "function",
        "function": {
            "name": HttpMethodFunctions.GET_HTTP_METHOD_PARAMETERS,
            "description": f"Generate the parameters of the {HttpMethod.PUT} request(s) based on the user's instruction and the table's schema",
            "parameters": {
                "type": "object",
                "properties": {
                    HttpMethodFunctions.FILTER_CONDITIONS: {
                        "type": "array",
                        "description": f"A list of specifications that filters for the rows to update in the {HttpMethod.PUT} request",
                        "items": {
                            "type": "object",
                            "properties": {
                                HttpMethodFunctions.COLUMN_NAME: {
                                    "type": "string",
                                    "enum": [column.name for column in columns],
                                    "description": "The name of the column that will be used to filter for the row to get."
                                },
                                HttpMethodFunctions.COLUMN_VALUE: {
                                    "type": ["string", "number", "boolean", "null"],
                                    "description": "The value of the column that will be used to filter for the row to get. Make sure that the value is of the same type as the column's data type."
                                }
                            },
                            "required": [HttpMethodFunctions.COLUMN_NAME, HttpMethodFunctions.COLUMN_VALUE]
                        }
                    },
                    HttpMethodFunctions.UPDATED_DATA: {
                        "type": "array",
                        "description": f"A list of data to update for the rows that meet the filter conditions in the {HttpMethod.PUT} request",
                        "items": {
                            "type": "object",
                            "properties": {
                                HttpMethodFunctions.COLUMN_NAME: {
                                    "type": "string",
                                    "enum": [column.name for column in columns],
                                    "description": "The name of the column that will be updated."
                                },
                                HttpMethodFunctions.COLUMN_VALUE: {
                                    "type": ["string", "number", "boolean", "null"],
                                    "description": "The new value for the column that will be updated. Make sure that the value is of the same type as the column's data type."
                                }
                            },
                            "required": [HttpMethodFunctions.COLUMN_NAME, HttpMethodFunctions.COLUMN_VALUE]
                        }
                    },
                },
                "required": [HttpMethodFunctions.FILTER_CONDITIONS, HttpMethodFunctions.UPDATED_DATA]
            }
        }
    }
    
    return function
