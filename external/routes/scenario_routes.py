from flask import Flask, Blueprint, Response, request

from external.controllers import ScenarioController
from external.utils.middleware import token_required


class ScenarioRoute:

    def __init__(
        self,
        app: Flask,
        base_route: str,
    ) -> None:
        self.app = app
        self.scenario_bp = Blueprint('scenarios', __name__, url_prefix=f'{base_route}/scenario')
        self.scenario_controller = ScenarioController()

    def register_routes(self) -> None:

        @self.scenario_bp.route("", methods=['GET'])
        @token_required
        def list_user_scenarios(user_id: str) -> Response:
            return self.scenario_controller.list_user_scenarios(user_id=user_id)

        @self.scenario_bp.route("", methods=['POST'])
        @token_required
        def create_scenario(user_id: str) -> Response:
            return self.scenario_controller.create_scenario(
                user_id=user_id,
                request=request.json,
            )

        @self.scenario_bp.route("/<scenario_id>", methods=['PATCH'])
        @token_required
        def update_scenario(user_id: str, scenario_id: str) -> Response:
            return self.scenario_controller.update_scenario(
                user_id=user_id,
                scenario_id=scenario_id,
                request=request.json,
            )

        @self.scenario_bp.route("/<scenario_id>", methods=['DELETE'])
        @token_required
        def delete_scenario(user_id: str, scenario_id: str) -> Response:
            return self.scenario_controller.delete_scenario(
                user_id=user_id,
                scenario_id=scenario_id,
            )

        self.app.register_blueprint(self.scenario_bp)
