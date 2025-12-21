from typing import Dict, Any
from ..entities.schema import SchemaEntity

class SchemaValidator:
    """
    Japanese: ドメインサービス (Domain Service)
    Handles complex validation that might involve external rules or 
    multiple field dependencies.
    """
    @staticmethod
    def validate_record_data(schema: SchemaEntity, data: Dict[str, Any]):
        # This calls the internal validation logic of the Entity
        # but can be extended to check cross-field constraints.
        schema.validate_payload(data)
        
        # Example of a service-level rule:
        # if "created_at" in data and "updated_at" in data:
        #     if data["updated_at"] < data["created_at"]:
        #         raise ValueError("Update time cannot be before creation time")