from typing import (
    Any, 
    Dict,
)

from external.repositories import (
    StudySettingsRepositoryImpl,
    UserRepositoryImpl,
)
from external.services import (
    redis_client,
    EventPublisherServiceImpl,
)
from external.utils import validate_request
from core.interactor import StudySettingsInteractor
from core.interactor.study_settings.dto import StudySettingsDTO


class StudySettingsController:
    
    def __init__(
        self,
    ) -> None:

        study_settings_repository = StudySettingsRepositoryImpl()
        user_repository = UserRepositoryImpl()
        
        event_publisher_service = EventPublisherServiceImpl(redis_client=redis_client)
        
        self.study_settings_interactor = StudySettingsInteractor(
            user_repository=user_repository,
            study_settings_repository=study_settings_repository,
            event_publisher_service=event_publisher_service,
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
    
    def update_study_teacher(
        self,
        user_id: str,
        request: Dict[str, Any],
    ) -> Dict[str, Any]:
        
        validate_request(
            request=request,
            required_fields=["studyId"],
        )
        request_dto = StudySettingsDTO(
            user_id=user_id,
            study_id=request.get("studyId"),
            persona_type=request.get("personaType", None),
            correction_level=request.get("correctionLevel", None),
            preferred_topics=request.get("preferredTopics", None),
            language_dynamics=request.get("languageDynamics", None),
        )
        self.study_settings_interactor.update(study_settings_dto=request_dto)
        return {}, 201
    