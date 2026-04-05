from flask import Flask, Blueprint, Response, request

from external.controllers.subscription_controller import SubscriptionController
from external.utils.middleware import token_required


class SubscriptionRoute:

    def __init__(
        self,
        app: Flask,
        base_route: str,
    ) -> None:
        self.app = app
        self.subscription_bp = Blueprint('subscriptions', __name__, url_prefix=f'{base_route}/subscriptions')
        self.subscription_controller = SubscriptionController()

    def register_routes(self) -> None:

        @self.subscription_bp.route("", methods=['GET'])
        @token_required
        def get_user_subscription(user_id: str) -> Response:
            return self.subscription_controller.get_user_subscription(user_id=user_id)

        @self.subscription_bp.route("", methods=['POST'])
        @token_required
        def create_user_subscription(user_id: str) -> Response:
            return self.subscription_controller.create_user_subscription(
                user_id=user_id,
                request=request.json,
            )

        @self.subscription_bp.route("/cancel", methods=['PATCH'])
        @token_required
        def cancel_user_subscription(user_id: str) -> Response:
            return self.subscription_controller.cancel_user_subscription(user_id=user_id)

        self.app.register_blueprint(self.subscription_bp)
