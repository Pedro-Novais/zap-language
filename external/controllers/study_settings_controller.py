from typing import (
    Any, 
    Dict,
)

from external.repositories import StudySettingsRepositoryImpl
from core.interactor import StudySettingsInteractor
from core.interactor.study_settings.dto import StudySettingsDTO
from external.utils import validate_request


class StudySettingsController:
    
    def __init__(
        self,
    ) -> None:

        study_settings_repository = StudySettingsRepositoryImpl()
        
        self.study_settings_interactor = StudySettingsInteractor(
            study_settings_repository=study_settings_repository,
        )
    
    def create_study_teacher(
        self,
        user_id: str,
        request: Dict[str, Any],
    ) -> Dict[str, Any]:
        
        request_dto = StudySettingsDTO(
            user_id=user_id,
            persona_type=request.get("personaType", None),
            correction_level=request.get("correctionLevel", None),
            preferred_topics=request.get("preferredTopics", None),
            language_dynamics=request.get("languageDynamics", None),
        )
        self.study_settings_interactor.create(study_settings_dto=request_dto)
        return {}, 201
    