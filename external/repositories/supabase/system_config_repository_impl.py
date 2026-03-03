from typing import Dict

from external.database.models._SystemConfig import SystemConfig
from external.database.connection import get_db_session
from core.interface.repository import SystemConfigRepository


class SystemConfigRepositoryImpl(SystemConfigRepository):

    def get_configurations(self) -> Dict[str, str]:

        with get_db_session() as session:
            configs = session.query(SystemConfig).all()
        
        result = {}
        for config in configs:
            result[config.key] = config.value
            
        return result
    