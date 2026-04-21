from dataclasses import dataclass


@dataclass
class CreateScenarioDTO:
    creator_id: str
    key: str
    name: str
    description: str
    ai_role_definition: str
    user_role_definition: str
    is_public: bool = False
