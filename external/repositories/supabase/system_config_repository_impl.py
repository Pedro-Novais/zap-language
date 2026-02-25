from typing import Dict

from external.database.models._SystemConfig import SystemConfig
from external.database.connection import get_db_session
from core.interface.repository import SystemConfigRepository
from core.model import SystemConfigModel


class SystemConfigRepositoryImpl(SystemConfigRepository):

    def get(self) -> Dict[str, SystemConfigModel]:

        with get_db_session() as session:
            configs = session.query(SystemConfig).all()
        
        result = {}
        for config in configs:
            result[config.key] = SystemConfigModel(
                key=config.key,
                value=config.value,
                description=config.description
            )
            
        return result
    