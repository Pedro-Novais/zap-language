from typing import Optional, List

from loguru import logger

from core.interface.repository import StudySettingsRepository
from core.shared.errors import UnhandledConfigurationValueError
from core.model.enum import (
    TeacherPersonaType, 
    TeacherCorrectionLevel, 
    TeacherLanguageDynamics,
)
from .dto import StudySettingsDTO


class StudySettingsInteractor:
    
    def __init__(
        self,
        study_settings_repository: StudySettingsRepository,
    ) -> None:

        self.study_settings_repository = study_settings_repository
        
    def create(
        self,
        study_settings_dto: StudySettingsDTO,
    ) -> None:
        
        logger.info(f"Creating study settings for user {study_settings_dto.user_id}")

        persona_type = self._get_persona_type(persona_type=study_settings_dto.persona_type)
        correction_level = self._get_correction_level(correction_level=study_settings_dto.correction_level)
        language_dynamics = self._get_language_dynamics(language_dynamics=study_settings_dto.language_dynamics)
        preferred_topics = self._get_preferred_topics(preferred_topics=study_settings_dto.preferred_topics)
        
        logger.info("Saving study settings")
        self.study_settings_repository.create(
            user_id=study_settings_dto.user_id,
            persona_type=persona_type,
            correction_level=correction_level,
            preferred_topics=preferred_topics,
            language_dynamics=language_dynamics,
        )
    
    def update(
        self,
        study_settings_dto: StudySettingsDTO,
    ) -> None:
        
        pass

    @staticmethod
    def _get_preferred_topics(preferred_topics: Optional[List[str]]) -> List[str]:
        
        logger.info(f"Preferred topics sended: {preferred_topics}")
        
        if not preferred_topics:
            preferred_topics = ["general topics"]
        
        logger.info(f"Preferred topics selected: {preferred_topics}")
        return preferred_topics
    
    @staticmethod
    def _get_language_dynamics(language_dynamics: Optional[str]) -> TeacherLanguageDynamics:
        
        logger.info(f"Language dynamics sended: {language_dynamics}")
        
        result = None
        if not language_dynamics:
            result = TeacherLanguageDynamics.SUPPORT
            
        if language_dynamics == "immersion":
            result = TeacherLanguageDynamics.IMMERSION
            
        if language_dynamics == "bilingue":
            result = TeacherLanguageDynamics.BILINGUE
            
        if language_dynamics == "support":
            result = TeacherLanguageDynamics.SUPPORT
        
        if not result:
            raise UnhandledConfigurationValueError()
            
        logger.info(f"Language dynamics selected: {result}")
        return result
        
    @staticmethod
    def _get_correction_level(correction_level: Optional[int]) -> TeacherCorrectionLevel:
        
        logger.info(f"Correction level sended: {correction_level}")
        
        result = None
        if not correction_level:
            result = TeacherCorrectionLevel.MEDIUM

        if correction_level == 1:
            result = TeacherCorrectionLevel.LIGHT
            
        if correction_level == 2:
            result = TeacherCorrectionLevel.MEDIUM
            
        if correction_level == 3:
            result = TeacherCorrectionLevel.STRONG
        
        if not result:
            raise UnhandledConfigurationValueError()
            
        logger.info(f"Correction level selected: {result}")
        return result
    
    @staticmethod
    def _get_persona_type(persona_type: Optional[str]) -> TeacherPersonaType:
        
        logger.info(f"Persona type sended: {persona_type}")
        
        result = None
        if not persona_type:
            result = TeacherPersonaType.FRIENDLY
            
        if persona_type == "friendly":
            result = TeacherPersonaType.FRIENDLY
            
        if persona_type == "strict":
            result = TeacherPersonaType.STRICT
            
        if persona_type == "funny":
            result = TeacherPersonaType.FUNNY
            
        if persona_type == "academic":
            result = TeacherPersonaType.ACADEMIC
        
        if not result:
            raise UnhandledConfigurationValueError()
            
        logger.info(f"Persona type selected: {result}")
        return result