from typing import (
    Any, 
    Dict,
)

from external.utils import validate_request


class StudySettingsController:
    
    def __init__(
        self,
    ) -> None:

        pass
    
    def create_study_teacher(
        self,
        request: Dict[str, Any],
    ) -> Dict[str, Any]:
        
        validate_request(
            request=request,
            required_fields=[],
        )
    