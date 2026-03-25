from typing import Optional

from sqlalchemy import select

from external.database.connection import get_db_session
from external.database.models import ScenarioContext
from core.interface.repository import ScenarioRepository
from core.model import ScenarioModel


class ScenarioRepositoryImpl(ScenarioRepository):

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
