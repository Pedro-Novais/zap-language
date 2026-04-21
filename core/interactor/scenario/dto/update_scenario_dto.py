from dataclasses import dataclass
from typing import Optional


@dataclass
class UpdateScenarioDTO:
    scenario_id: str
    key: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    ai_role_definition: Optional[str] = None
    user_role_definition: Optional[str] = None
    is_public: Optional[bool] = None
