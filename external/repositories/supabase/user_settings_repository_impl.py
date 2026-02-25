from typing import (Optional, List)

from core.interactor import study_settings
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
        user_id: str,
        study_id: str,
        persona_type: TeacherPersonaType | None,
        correction_level: TeacherCorrectionLevel | None,
        preferred_topics: List[str] | None,
        language_dynamics: TeacherLanguageDynamics | None,
    ) -> None:
        
        with get_db_session() as session:
            study_settings_db = session.query(StudySettings).filter(
                StudySettings.user_id == user_id and StudySettings.study_id == study_id
            ).first()
            if study_settings_db is None:
                raise ValueError("Study settings not found")
            
            if persona_type is not None:
                study_settings_db.persona_type = persona_type
                
            if correction_level is not None:
                study_settings_db.correction_level = correction_level
                
            if preferred_topics is not None:
                study_settings_db.preferred_topics = preferred_topics
                
            if language_dynamics is not None:
                study_settings_db.language_dynamics = language_dynamics
                
            session.commit()
            return
        