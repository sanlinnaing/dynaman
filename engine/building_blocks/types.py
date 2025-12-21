from enum import Enum

class FieldType(str, Enum):
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    EMAIL = "email"
    REFERENCE = "reference"
    DATE = "date"