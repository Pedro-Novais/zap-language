import uuid
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class StudySettingsDTO:
    user_id: uuid.UUID
    id: Optional[uuid.UUID] = None
    persona_type: Optional[str] = None
    correction_level: Optional[int] = None
    preferred_topics: Optional[List[str]] = None
    language_ratio: Optional[int] = None
    language_dynamics: Optional[str] = None
    receive_newsletters: bool = False
    preferred_language: Optional[str] = None
