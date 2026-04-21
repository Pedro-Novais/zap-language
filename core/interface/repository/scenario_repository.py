from abc import ABC, abstractmethod
from typing import List, Optional

from core.model import ScenarioModel


class ScenarioRepository(ABC):

    @abstractmethod
    def list_by_creator_id(
        self,
        creator_id: str,
    ) -> List[ScenarioModel]:

        raise NotImplementedError()

    @abstractmethod
    def get_by_key(
        self, 
        key: str,
    ) -> Optional[ScenarioModel]:
        
        raise NotImplementedError()

    @abstractmethod
    def get_by_key_and_creator_id(
        self,
        key: str,
        creator_id: str,
    ) -> Optional[ScenarioModel]:

        raise NotImplementedError()

    @abstractmethod
    def get_by_id(
        self,
        scenario_id: str,
    ) -> Optional[ScenarioModel]:

        raise NotImplementedError()

    @abstractmethod
    def create(
        self,
        creator_id: str,
        key: str,
        name: str,
        description: str,
        ai_role_definition: str,
        user_role_definition: str,
        is_public: bool,
    ) -> ScenarioModel:

        raise NotImplementedError()

    @abstractmethod
    def update(
        self,
        scenario_id: str,
        key: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        ai_role_definition: Optional[str] = None,
        user_role_definition: Optional[str] = None,
        is_public: Optional[bool] = None,
    ) -> ScenarioModel:

        raise NotImplementedError()

    @abstractmethod
    def delete(
        self,
        scenario_id: str,
    ) -> None:

        raise NotImplementedError()
