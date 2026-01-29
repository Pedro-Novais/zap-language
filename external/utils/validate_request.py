from typing import Any, Dict, List

from core.shared.errors import MissingRequiredFieldError


def validate_request(
    request: Dict[str, Any], 
    required_fields: List[str],
) -> None:
    
    for field in required_fields:
        if field not in request:
            raise MissingRequiredFieldError(field=field)
        
    return None