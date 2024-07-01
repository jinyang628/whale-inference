from enum import StrEnum
from pydantic import BaseModel
from typing import Optional

class DataType(StrEnum):
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    
class PrimaryKey(StrEnum):
    NONE = "none" 
    AUTO_INCREMENT = "auto_increment"
    
class Column(BaseModel):
    name: str
    data_type: DataType
    nullable: bool = False
    primary_key: PrimaryKey = PrimaryKey.NONE

class Table(BaseModel):
    name: str
    description: Optional[str] = None
    columns: list[Column]
    
class ApplicationContent(BaseModel):
    name: str
    tables: list[Table]
    
    class Config: 
        extra = "forbid"
        