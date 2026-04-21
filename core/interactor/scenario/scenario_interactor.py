from loguru import logger
from typing import List

from core.interface.repository import ScenarioRepository
from core.model import ScenarioModel
from core.shared.errors import (
    MissingRequiredFieldError,
    ScenarioKeyAlreadyExistsError,
    ScenarioNotFoundError,
    ScenarioPermissionDeniedError,
)
from .dto import CreateScenarioDTO, UpdateScenarioDTO


class ScenarioInteractor:

    def __init__(
        self,
        scenario_repository: ScenarioRepository,
    ) -> None:

        self.scenario_repository = scenario_repository

    def create_scenario(
        self,
        dto: CreateScenarioDTO,
    ) -> ScenarioModel:

        logger.info(f"Creating scenario with key: {dto.key}")

        existing_scenario = self.scenario_repository.get_by_key_and_creator_id(
            key=dto.key,
            creator_id=dto.creator_id,
        )
        if existing_scenario:
            raise ScenarioKeyAlreadyExistsError(key=dto.key)

        return self.scenario_repository.create(
            creator_id=dto.creator_id,
            key=dto.key,
            name=dto.name,
            description=dto.description,
            ai_role_definition=dto.ai_role_definition,
            user_role_definition=dto.user_role_definition,
            is_public=dto.is_public,
        )

    def list_user_scenarios(
        self,
        user_id: str,
    ) -> List[ScenarioModel]:

        logger.info(f"Listing scenarios for user: {user_id}")
        return self.scenario_repository.list_by_creator_id(creator_id=user_id)

    def update_scenario(
        self,
        user_id: str,
        dto: UpdateScenarioDTO,
    ) -> ScenarioModel:

        logger.info(f"Updating scenario: {dto.scenario_id}")

        scenario = self.scenario_repository.get_by_id(scenario_id=dto.scenario_id)
        if not scenario:
            raise ScenarioNotFoundError()

        self._validate_permission(user_id=user_id, creator_id=scenario.creator_id)
        self._validate_update_payload(dto=dto)
        self._validate_unique_key(dto=dto, current_key=scenario.key)

        return self.scenario_repository.update(
            scenario_id=dto.scenario_id,
            key=dto.key,
            name=dto.name,
            description=dto.description,
            ai_role_definition=dto.ai_role_definition,
            user_role_definition=dto.user_role_definition,
            is_public=dto.is_public,
        )

    def delete_scenario(
        self,
        user_id: str,
        scenario_id: str,
    ) -> None:

        logger.info(f"Deleting scenario: {scenario_id}")

        scenario = self.scenario_repository.get_by_id(scenario_id=scenario_id)
        if not scenario:
            raise ScenarioNotFoundError()

        self._validate_permission(user_id=user_id, creator_id=scenario.creator_id)
        self.scenario_repository.delete(scenario_id=scenario_id)

    def _validate_unique_key(
        self,
        dto: UpdateScenarioDTO,
        current_key: str,
    ) -> None:

        if dto.key is None or dto.key.lower() == current_key.lower():
            return

        existing_scenario = self.scenario_repository.get_by_key(key=dto.key)
        if existing_scenario:
            raise ScenarioKeyAlreadyExistsError(key=dto.key)

    @staticmethod
    def _validate_permission(
        user_id: str,
        creator_id: str,
    ) -> None:

        if creator_id is None or str(creator_id) != str(user_id):
            raise ScenarioPermissionDeniedError()

    @staticmethod
    def _validate_update_payload(
        dto: UpdateScenarioDTO,
    ) -> None:

        if all(
            field is None
            for field in [
                dto.key,
                dto.name,
                dto.description,
                dto.ai_role_definition,
                dto.user_role_definition,
                dto.is_public,
            ]
        ):
            raise MissingRequiredFieldError()
