from enum import StrEnum
from typing import Any
import logging
from app.models.application import PrimaryKey

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

class ApplicationFunction(StrEnum):
    CREATE_APPLICATION = "create_application"
    APPLICATION_CONTENT = "application_content"
    NAME = "name"
    OVERVIEW = "overview"
    CLARIFICATION = "clarification"
    TABLES = "tables"
    TABLE_NAME = "table_name"
    DESCRIPTION = "description"
    COLUMNS = "columns"
    DATA_TYPE = "data_type"
    ENUM_VALUES = "enum_values"
    NULLABLE = "nullable"
    DEFAULT_VALUE = "default_value"
    UNIQUE = "unique"
    PRIMARY_KEY = "primary_key"
    FOREIGN_KEY = "foreign_key"
    TABLE = "table"
    COLUMN = "column"
    
    
def get_application_creation_schema() -> dict[str, Any]:
    function = {
        "type": "function",
        "function": {
            "name": ApplicationFunction.CREATE_APPLICATION,
            "description": "Create an application that has the necessary table(s) to support the CRUD operations of the user's application",
            "parameters": {
                "type": "object",
                "properties": {
                    ApplicationFunction.APPLICATION_CONTENT: {
                        "type": "object",
                        "properties": {
                            ApplicationFunction.NAME: {
                                "type": "string",
                                "description": "The name of the application to be created"
                            },
                            ApplicationFunction.TABLES: {
                                "type": "array",
                                "description": "An array of tables for the application",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        ApplicationFunction.NAME: {
                                            "type": "string",
                                            "description": "The name of the table"
                                        },
                                        ApplicationFunction.DESCRIPTION: {
                                            "type": "string",
                                            "description": "A description of the table"
                                        },
                                        ApplicationFunction.COLUMNS: {
                                            "type": "array",
                                            "description": "An array of columns for the table",
                                            "items": {
                                                "type": "object", 
                                                "properties": {
                                                    ApplicationFunction.NAME: {
                                                        "type": "string",
                                                        "description": "The name of the column"
                                                    },
                                                    ApplicationFunction.DATA_TYPE: {
                                                        "type": "string",
                                                        "enum": ["string", "integer", "float", "boolean", "date", "datetime", "uuid", "enum"],
                                                        "description": "The data type of the column"
                                                    },
                                                    ApplicationFunction.ENUM_VALUES: {
                                                        "type": "array",
                                                        "items": {"type": "string"},
                                                        "description": "List of enum values if data_type is enum"
                                                    },
                                                    ApplicationFunction.NULLABLE: {
                                                        "type": "boolean",
                                                        "description": "Whether the column can be null"
                                                    },
                                                    ApplicationFunction.DEFAULT_VALUE: {
                                                        "type": ["string", "number", "boolean", "null"],
                                                        "description": "The default value for the column. This is required if the data type is enum"
                                                    },
                                                    ApplicationFunction.UNIQUE: {
                                                        "type": "boolean",
                                                        "description": "Whether the column values must be unique"
                                                    },
                                                    ApplicationFunction.FOREIGN_KEY: {
                                                        "type": "object",
                                                        "properties": {
                                                            ApplicationFunction.TABLE: {"type": "string"},
                                                            ApplicationFunction.COLUMN: {"type": "string"}
                                                        },
                                                        "required": [ApplicationFunction.TABLE, ApplicationFunction.COLUMN],
                                                        "description": "Foreign key reference if applicable"
                                                    }
                                                },
                                                "required": [ApplicationFunction.NAME, ApplicationFunction.DATA_TYPE]
                                            }
                                        },
                                        ApplicationFunction.PRIMARY_KEY: {
                                            "type": "string",
                                            "enum": [PrimaryKey.AUTO_INCREMENT, PrimaryKey.UUID],
                                            "description": "The primary key type for the table"
                                        }
                                    },
                                    "required": [ApplicationFunction.NAME, ApplicationFunction.COLUMNS, ApplicationFunction.PRIMARY_KEY]
                                }
                            }
                        },
                        "required": [ApplicationFunction.NAME, ApplicationFunction.TABLES]
                    },
                    ApplicationFunction.OVERVIEW: {
                        "type": "string",
                        "description": "A general overview of the application and the tasks it supports"
                    },
                    ApplicationFunction.CLARIFICATION: {
                        "type": "string",
                        "description": "A question to ask the user for clarification if needed"
                    }
                }
            }
        }
    }
    return function