from enum import StrEnum
from typing import Any
import logging
from app.models.application import ApplicationContent, Column, DataType, Table
from app.models.inference import HttpMethod

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

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
                            "properties": _build_rows_schema(columns=columns),
                            "required": [column.name for column in columns if not column.nullable]
                        }
                    }
                },
                "required": [HttpMethodFunctions.INSERTED_ROWS]
            }
        }
    }
    log.info(f"Post HTTP Method Parameters Function: {function}")
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
                        "type": "object",
                        "description": f"A specification that filters for the rows to delete in the {HttpMethod.DELETE} request",
                        "properties": {
                            "operator": {
                                "type": "string",
                                "enum": ["AND", "OR"],
                                "description": "The logical operator to apply to the conditions"
                            },
                            "conditions": {
                                "type": "array",
                                "items": {
                                    "oneOf": [
                                        {
                                            "type": "object",
                                            "properties": {
                                                "column": {
                                                    "type": "string",
                                                    "enum": [column.name for column in columns],
                                                    "description": "The name of the column to filter on"
                                                },
                                                "operator": {
                                                    "type": "string",
                                                    "enum": ["=", "!=", ">", "<", ">=", "<=", "LIKE", "IN"],
                                                    "description": "The comparison operator"
                                                },
                                                "value": {
                                                    "oneOf": [
                                                        {"type": "string"},
                                                        {"type": "number"},
                                                        {"type": "boolean"},
                                                        {"type": "null"},
                                                        {
                                                            "type": "array",
                                                            "items": {
                                                                "oneOf": [
                                                                    {"type": "string"},
                                                                    {"type": "number"},
                                                                    {"type": "boolean"},
                                                                    {"type": "null"}
                                                                ]
                                                            }
                                                        }
                                                    ],
                                                    "description": "The value to compare against. Use array for IN operator."
                                                }
                                            },
                                            "required": ["column", "operator", "value"]
                                        },
                                        {
                                            "$ref": "#/properties/HttpMethodFunctions.FILTER_CONDITIONS"
                                        }
                                    ]
                                }
                            }
                        },
                        "required": ["operator", "conditions"]
                    }
                },
                "required": [HttpMethodFunctions.FILTER_CONDITIONS]
            }
        }
    }
    log.info(f"Delete HTTP Method Parameters Function: {function}")
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
                        "type": "object",
                        "description": f"A specification that filters for the rows to delete in the {HttpMethod.GET} request",
                        "properties": {
                            "operator": {
                                "type": "string",
                                "enum": ["AND", "OR"],
                                "description": "The logical operator to apply to the conditions"
                            },
                            "conditions": {
                                "type": "array",
                                "items": {
                                    "oneOf": [
                                        {
                                            "type": "object",
                                            "properties": {
                                                "column": {
                                                    "type": "string",
                                                    "enum": [column.name for column in columns],
                                                    "description": "The name of the column to filter on"
                                                },
                                                "operator": {
                                                    "type": "string",
                                                    "enum": ["=", "!=", ">", "<", ">=", "<=", "LIKE", "IN"],
                                                    "description": "The comparison operator"
                                                },
                                                "value": {
                                                    "oneOf": [
                                                        {"type": "string"},
                                                        {"type": "number"},
                                                        {"type": "boolean"},
                                                        {"type": "null"},
                                                        {
                                                            "type": "array",
                                                            "items": {
                                                                "oneOf": [
                                                                    {"type": "string"},
                                                                    {"type": "number"},
                                                                    {"type": "boolean"},
                                                                    {"type": "null"}
                                                                ]
                                                            }
                                                        }
                                                    ],
                                                    "description": "The value to compare against. Use array for IN operator."
                                                }
                                            },
                                            "required": ["column", "operator", "value"]
                                        },
                                        {
                                            "$ref": "#/properties/HttpMethodFunctions.FILTER_CONDITIONS"
                                        }
                                    ]
                                }
                            }
                        },
                        "required": ["operator", "conditions"]
                    }
                },
                "required": [HttpMethodFunctions.FILTER_CONDITIONS]
            }
        }
    }
    log.info(f"Get HTTP Method Parameters Function: {function}")
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
                        "type": "object",
                        "description": f"A specification that filters for the rows to delete in the {HttpMethod.PUT} request",
                        "properties": {
                            "operator": {
                                "type": "string",
                                "enum": ["AND", "OR"],
                                "description": "The logical operator to apply to the conditions"
                            },
                            "conditions": {
                                "type": "array",
                                "items": {
                                    "oneOf": [
                                        {
                                            "type": "object",
                                            "properties": {
                                                "column": {
                                                    "type": "string",
                                                    "enum": [column.name for column in columns],
                                                    "description": "The name of the column to filter on"
                                                },
                                                "operator": {
                                                    "type": "string",
                                                    "enum": ["=", "!=", ">", "<", ">=", "<=", "LIKE", "IN"],
                                                    "description": "The comparison operator"
                                                },
                                                "value": {
                                                    "oneOf": [
                                                        {"type": "string"},
                                                        {"type": "number"},
                                                        {"type": "boolean"},
                                                        {"type": "null"},
                                                        {
                                                            "type": "array",
                                                            "items": {
                                                                "oneOf": [
                                                                    {"type": "string"},
                                                                    {"type": "number"},
                                                                    {"type": "boolean"},
                                                                    {"type": "null"}
                                                                ]
                                                            }
                                                        }
                                                    ],
                                                    "description": "The value to compare against. Use array for IN operator."
                                                }
                                            },
                                            "required": ["column", "operator", "value"]
                                        },
                                        {
                                            "$ref": "#/properties/HttpMethodFunctions.FILTER_CONDITIONS"
                                        }
                                    ]
                                }
                            }
                        },
                        "required": ["operator", "conditions"]
                    },
                    HttpMethodFunctions.UPDATED_DATA: {
                        "type": "object",
                        "description": "An object containing the columns to be updated and their new values",
                        "properties": _build_rows_schema(columns=columns),
                    }
                },
                "required": [HttpMethodFunctions.FILTER_CONDITIONS, HttpMethodFunctions.UPDATED_DATA]
            }
        }
    }
    log.info(f"PUT HTTP Method Parameters Function: {function}")
    return function

def _build_rows_schema(columns: list[Column]) -> dict[str, Any]:
    inserted_rows_schema: dict[str, Any] = {}
    for column in columns:
        name: str = column.name
        data_type: DataType = column.data_type
        if data_type == DataType.ENUM:
            # Note for PostgreSQL, enum types are strings
            inserted_rows_schema[name] = {
                "type": "string",
                "enum": column.enum_values,
                "description": f"The value for the {name} column in the inserted row. Make sure that the value is one of the enum values for the column."
            }
        elif data_type == DataType.DATE:
            # Date objects are not JSON serialisable across API requests so this is the best alternative
            inserted_rows_schema[name] = {
                "type": "string",
                "description": f"The value for the {name} column in the inserted row. Make sure that the value is in the format of YYYY-MM-DD."
            }
        elif data_type == DataType.FLOAT:
            # Floats are called numbers in OpenAI function calling schema
            inserted_rows_schema[name] = {
                "type": "number",
                "description": f"The value for the {name} column in the inserted row."
            }
        else:
            # The rest of the data types do not need special mapping
            inserted_rows_schema[name] = {
                "type": data_type,
                "description": f"The value for the {name} column in the inserted row."
            }
    
    return inserted_rows_schema