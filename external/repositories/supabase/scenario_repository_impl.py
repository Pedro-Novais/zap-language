from typing import List, Optional

from sqlalchemy import select

from external.database.connection import get_db_session
from external.database.models import ScenarioContext
from core.interface.repository import ScenarioRepository
from core.model import ScenarioModel


class ScenarioRepositoryImpl(ScenarioRepository):

    def list_by_creator_id(
        self,
        creator_id: str,
    ) -> List[ScenarioModel]:

        with get_db_session() as session:
            stmt = select(ScenarioContext).where(ScenarioContext.creator_id == creator_id)
            result = session.execute(stmt).scalars().all()
            return [ScenarioModel.model_validate(scenario) for scenario in result]

    def get_by_key(
        self, 
        key: str,
    ) -> Optional[ScenarioModel]:
        
        with get_db_session() as session:
            stmt = select(ScenarioContext).where(ScenarioContext.key == key.lower())
            result = session.execute(stmt).scalar_one_or_none()
        
            if not result:
                return None
                
            return ScenarioModel.model_validate(result)

    def get_by_key_and_creator_id(
        self,
        key: str,
        creator_id: str,
    ) -> Optional[ScenarioModel]:

        with get_db_session() as session:
            stmt = select(ScenarioContext).where(
                ScenarioContext.key == key.lower(),
                ScenarioContext.creator_id == creator_id,
            )
            result = session.execute(stmt).scalar_one_or_none()

            if not result:
                return None

            return ScenarioModel.model_validate(result)

    def get_by_id(
        self,
        scenario_id: str,
    ) -> Optional[ScenarioModel]:

        with get_db_session() as session:
            stmt = select(ScenarioContext).where(ScenarioContext.id == scenario_id)
            result = session.execute(stmt).scalar_one_or_none()

            if not result:
                return None

            return ScenarioModel.model_validate(result)

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

        with get_db_session() as session:
            scenario = ScenarioContext(
                creator_id=creator_id,
                key=key.lower(),
                name=name,
                description=description,
                ai_role_definition=ai_role_definition,
                user_role_definition=user_role_definition,
                is_public=is_public,
            )
            session.add(scenario)
            session.commit()
            session.refresh(scenario)
            return ScenarioModel.model_validate(scenario)

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

        with get_db_session() as session:
            stmt = select(ScenarioContext).where(ScenarioContext.id == scenario_id)
            scenario = session.execute(stmt).scalar_one()

            if key is not None:
                scenario.key = key.lower()
            if name is not None:
                scenario.name = name
            if description is not None:
                scenario.description = description
            if ai_role_definition is not None:
                scenario.ai_role_definition = ai_role_definition
            if user_role_definition is not None:
                scenario.user_role_definition = user_role_definition
            if is_public is not None:
                scenario.is_public = is_public

            session.commit()
            session.refresh(scenario)
            return ScenarioModel.model_validate(scenario)

    def delete(
        self,
        scenario_id: str,
    ) -> None:

        with get_db_session() as session:
            stmt = select(ScenarioContext).where(ScenarioContext.id == scenario_id)
            scenario = session.execute(stmt).scalar_one()
            session.delete(scenario)
            session.commit()
