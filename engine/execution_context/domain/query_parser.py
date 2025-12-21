from typing import Dict, Any, Optional

def parse_filters(query_params: Dict[str, Any], field_type_map: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """
    Converts a dictionary of query parameters into a MongoDB query filter.
    
    Supported operators (suffixed to field name):
    - _eq: Equal to ($eq)
    - _gt: Greater than ($gt)
    - _lt: Less than ($lt)
    - _contains: Case-insensitive regex search
    
    Args:
        query_params: Dictionary of query parameters.
        field_type_map: Optional dictionary mapping field names to their expected types ("number", "boolean", etc.).
                        Used for type casting values.

    Example:
        Input: {"age_gt": "18", "name_contains": "john"}, field_type_map={"age": "number"}
        Output: {"age": {"$gt": 18.0}, "name": {"$regex": "john", "$options": "i"}}
    """
    mongo_query = {}

    for key, value in query_params.items():
        field = key
        operator = None

        if key.endswith("_eq"):
            field = key[:-3]
            operator = "$eq"
        elif key.endswith("_gt"):
            field = key[:-3]
            operator = "$gt"
        elif key.endswith("_lt"):
            field = key[:-3]
            operator = "$lt"
        elif key.endswith("_contains"):
            field = key[:-9]
            operator = "$regex"
        
        # Determine strict field name for type lookup
        # If no operator found, the field name is just the key
        
        # Cast value if type map is provided
        casted_value = value
        if field_type_map and field in field_type_map:
            target_type = field_type_map[field]
            try:
                if target_type == "number":
                    casted_value = float(value)
                    if casted_value.is_integer():
                         casted_value = int(casted_value)
                elif target_type == "boolean":
                    if isinstance(value, str):
                        casted_value = value.lower() == "true"
            except ValueError:
                # If casting fails, keep original value (or could raise error)
                pass

        if operator == "$regex":
            mongo_query[field] = {"$regex": casted_value, "$options": "i"}
        elif operator:
            mongo_query[field] = {operator: casted_value}
        else:
            # Direct match
            mongo_query[field] = casted_value

    return mongo_query
