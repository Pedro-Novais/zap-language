from typing import (Optional, List)

from external.database.models import StudySettings
from external.database.connection import get_db_session
from core.model.enum import (
    TeacherPersonaType, 
    TeacherCorrectionLevel, 
    TeacherLanguageDynamics,
)
from core.interface.repository import StudySettingsRepository
from core.interactor.study_settings.dto import StudySettingsDTO


class StudySettingsRepositoryImpl(StudySettingsRepository):

    def get(
        self,
        user_id: str,
    ) -> None:
        
        raise NotImplementedError()

    def create(
        self,
        user_id: str,
        persona_type: TeacherPersonaType,
        correction_level: TeacherCorrectionLevel,
        preferred_topics: List[str],
        language_dynamics: TeacherLanguageDynamics,
    ) -> None:
        
        with get_db_session() as session:
            study_settings = StudySettings(
                user_id=user_id,
                persona_type=persona_type,
                correction_level=correction_level,
                preferred_topics=preferred_topics,
                language_dynamics=language_dynamics,
            )
            session.add(study_settings)
            session.commit()
            return
    
    def update(
        self,
        study_settings: StudySettingsDTO,
    ) -> None:
        
        raise NotImplementedError()
