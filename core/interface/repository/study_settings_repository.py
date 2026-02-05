from abc import ABC, abstractmethod
from typing import Optional, List

from core.model.enum import (
    TeacherPersonaType, 
    TeacherCorrectionLevel, 
    TeacherLanguageDynamics,
)


class StudySettingsRepository(ABC):

    @abstractmethod
    def get(
        self,
        user_id: str,
    ) -> None:
        
        raise NotImplementedError()

    @abstractmethod
    def create(
        self,
        user_id: str,
        persona_type: TeacherPersonaType,
        correction_level: TeacherCorrectionLevel,
        preferred_topics: List[str],
        language_dynamics: TeacherLanguageDynamics,
    ) -> None:
        
        raise NotImplementedError()
    
    @abstractmethod
    def update(
        self,
        user_id: str,
        study_id: str,
        persona_type: TeacherPersonaType | None,
        correction_level: TeacherCorrectionLevel | None,
        preferred_topics: List[str] | None,
        language_dynamics: TeacherLanguageDynamics | None,
    ) -> None:
        
        raise NotImplementedError()
