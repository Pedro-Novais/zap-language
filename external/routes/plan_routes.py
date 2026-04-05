from flask import Flask, Blueprint, Response, request

from external.controllers.plan_controller import PlanController
from external.utils.middleware import token_required, admin_required


class PlanRoute:

    def __init__(
        self,
        app: Flask,
        base_route: str,
    ) -> None:
        self.app = app
        self.plan_bp = Blueprint('plans', __name__, url_prefix=f'{base_route}/plan')
        self.plan_controller = PlanController()

    def register_routes(self) -> None:

        @self.plan_bp.route("", methods=['GET'])
        def get_plans() -> Response:
            return self.plan_controller.get_plans()

        @self.plan_bp.route("", methods=['POST'])
        @admin_required
        def create_plan(user_id: str) -> Response:
            return self.plan_controller.create_plan(request=request.json)

        self.app.register_blueprint(self.plan_bp)
