import logging
from enum import StrEnum
from typing import Any

from app.models.application import DataType, PrimaryKey

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class ApplicationFunction(StrEnum):
    CREATE_APPLICATION = "create_application"
    APPLICATION_CONTENT = "application_content"
    NAME = "name"
    OVERVIEW = "overview"
    CLARIFY = "clarify"
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
    CONCLUDE = "conclude"
    CONCLUDING_MESSAGE = "concluding_message"


def create_application() -> dict[str, Any]:
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
                                "description": "The name of the application to be created",
                            },
                            ApplicationFunction.TABLES: {
                                "type": "array",
                                "description": "An array of tables for the application",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        ApplicationFunction.NAME: {
                                            "type": "string",
                                            "description": "The name of the table",
                                        },
                                        ApplicationFunction.DESCRIPTION: {
                                            "type": "string",
                                            "description": "A description of the table",
                                        },
                                        ApplicationFunction.COLUMNS: {
                                            "type": "array",
                                            "description": "An array of columns for the table",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    ApplicationFunction.NAME: {
                                                        "type": "string",
                                                        "description": "The name of the column",
                                                    },
                                                    ApplicationFunction.DATA_TYPE: {
                                                        "type": "string",
                                                        "enum": [
                                                            data_type.value
                                                            for data_type in DataType.__members__.values()
                                                        ],
                                                        "description": "The data type of the column",
                                                    },
                                                    ApplicationFunction.ENUM_VALUES: {
                                                        "type": "array",
                                                        "items": {"type": "string"},
                                                        "description": "List of enum values if data_type is enum",
                                                    },
                                                    ApplicationFunction.NULLABLE: {
                                                        "type": "boolean",
                                                        "description": "Whether the column can be null",
                                                    },
                                                    ApplicationFunction.DEFAULT_VALUE: {
                                                        "type": [
                                                            "string",
                                                            "number",
                                                            "boolean",
                                                            "null",
                                                        ],
                                                        "description": "The default value for the column. This is required if the data type is enum",
                                                    },
                                                    ApplicationFunction.UNIQUE: {
                                                        "type": "boolean",
                                                        "description": "Whether the column values must be unique",
                                                    },
                                                    ApplicationFunction.FOREIGN_KEY: {
                                                        "type": "object",
                                                        "properties": {
                                                            ApplicationFunction.TABLE: {
                                                                "type": "string"
                                                            },
                                                            ApplicationFunction.COLUMN: {
                                                                "type": "string"
                                                            },
                                                        },
                                                        "required": [
                                                            ApplicationFunction.TABLE,
                                                            ApplicationFunction.COLUMN,
                                                        ],
                                                        "description": "Foreign key reference if applicable",
                                                    },
                                                },
                                                "required": [
                                                    ApplicationFunction.NAME,
                                                    ApplicationFunction.DATA_TYPE,
                                                ],
                                            },
                                        },
                                        ApplicationFunction.PRIMARY_KEY: {
                                            "type": "string",
                                            "enum": [
                                                PrimaryKey.AUTO_INCREMENT,
                                                PrimaryKey.UUID,
                                            ],
                                            "description": "The primary key type for the table",
                                        },
                                    },
                                    "required": [
                                        ApplicationFunction.NAME,
                                        ApplicationFunction.COLUMNS,
                                        ApplicationFunction.PRIMARY_KEY,
                                    ],
                                },
                            },
                        },
                        "required": [
                            ApplicationFunction.NAME,
                            ApplicationFunction.TABLES,
                        ],
                    },
                    ApplicationFunction.OVERVIEW: {
                        "type": "string",
                        "description": "A general overview of the application and the tasks it supports",
                    },
                    ApplicationFunction.CLARIFICATION: {
                        "type": "string",
                        "description": "A question to ask the user for clarification if needed",
                    },
                },
                "required": [
                    ApplicationFunction.APPLICATION_CONTENT,
                    ApplicationFunction.OVERVIEW,
                ],
            },
        },
    }
    return function


def clarify() -> dict[str, Any]:
    function = {
        "type": "function",
        "function": {
            "name": ApplicationFunction.CLARIFY,
            "description": "Ask the user for clarification on the application requirements",
            "parameters": {
                "type": "object",
                "properties": {
                    ApplicationFunction.CLARIFICATION: {
                        "type": "string",
                        "description": "A question to ask the user for clarification",
                    }
                },
                "required": [ApplicationFunction.CLARIFICATION],
            },
        },
    }
    return function


def conclude() -> dict[str, Any]:
    function = {
        "type": "function",
        "function": {
            "name": ApplicationFunction.CONCLUDE,
            "description": "Conclude the conversation with the user and inform him that the application has been created",
            "parameters": {
                "type": "object",
                "properties": {
                    ApplicationFunction.CONCLUDING_MESSAGE: {
                        "type": "string",
                        "description": "The message to send to the user to conclude the conversation",
                    }
                },
                "required": [ApplicationFunction.CONCLUDING_MESSAGE],
            },
        },
    }
    return function
