from typing import Optional

from loguru import logger

from core.interface.repository import ScenarioRepository
from core.interface.service import RedisService
from core.model import ScenarioModel


class ScenarioService:
    
    def __init__(
        self, 
        scenario_repository: ScenarioRepository, 
    ) -> None:
        
        self.scenario_repository = scenario_repository

    def get_by_key(
        self, 
        key: str,
    ) -> Optional[ScenarioModel]:
        
        logger.info(f"Getting scenario {key}")
        
        scenario = self.scenario_repository.get_by_key(key=key)
        if not scenario:
            logger.error(f"Scenario not found")
            return None
        
        return scenario
    