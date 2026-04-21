from typing import Any, Dict, Tuple

from flask import jsonify

from core.interactor import ScenarioInteractor
from core.interactor.scenario import CreateScenarioDTO, UpdateScenarioDTO
from external.container import scenario_repository
from external.utils import validate_request


class ScenarioController:

    def __init__(self) -> None:
        self.scenario_interactor = ScenarioInteractor(
            scenario_repository=scenario_repository,
        )

    def create_scenario(
        self,
        user_id: str,
        request: Dict[str, Any],
    ) -> Tuple[Dict[str, Any], int]:

        validate_request(
            request=request,
            required_fields=[
                "key",
                "name",
                "description",
                "aiRoleDefinition",
                "userRoleDefinition",
            ],
        )
        dto = CreateScenarioDTO(
            creator_id=user_id,
            key=request["key"],
            name=request["name"],
            description=request["description"],
            ai_role_definition=request["aiRoleDefinition"],
            user_role_definition=request["userRoleDefinition"],
            is_public=False,
        )
        scenario = self.scenario_interactor.create_scenario(dto=dto)
        scenario_data = self._sanitize_scenario_response(scenario=scenario)
        return jsonify(scenario_data), 201

    def list_user_scenarios(
        self,
        user_id: str,
    ) -> Tuple[Dict[str, Any], int]:

        scenarios = self.scenario_interactor.list_user_scenarios(user_id=user_id)
        scenarios_data = [
            self._sanitize_scenario_response(scenario=scenario)
            for scenario in scenarios
        ]
        return jsonify(scenarios_data), 200

    def update_scenario(
        self,
        user_id: str,
        scenario_id: str,
        request: Dict[str, Any],
    ) -> Tuple[Dict[str, Any], int]:

        dto = UpdateScenarioDTO(
            scenario_id=scenario_id,
            key=request.get("key"),
            name=request.get("name"),
            description=request.get("description"),
            ai_role_definition=request.get("aiRoleDefinition"),
            user_role_definition=request.get("userRoleDefinition"),
            is_public=False,
        )
        scenario = self.scenario_interactor.update_scenario(
            user_id=user_id,
            dto=dto,
        )
        scenario_data = self._sanitize_scenario_response(scenario=scenario)
        return jsonify(scenario_data), 200

    def delete_scenario(
        self,
        user_id: str,
        scenario_id: str,
    ) -> Tuple[Dict[str, Any], int]:

        self.scenario_interactor.delete_scenario(
            user_id=user_id,
            scenario_id=scenario_id,
        )
        return {}, 204

    @staticmethod
    def _sanitize_scenario_response(
        scenario,
    ) -> Dict[str, Any]:

        scenario_data = scenario.model_dump(mode="json")
        scenario_data.pop("creator_id", None)
        return scenario_data
