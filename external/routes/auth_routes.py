from flask import Blueprint, Flask, Response

from external.controllers import AuthController


class AuthRoute:

    def __init__(
        self,
        app: Flask,
        base_route: str,
    ) -> None:

        self.app = app
        self.auth_bp = Blueprint('auth', __name__, url_prefix=f'{base_route}/auth')
        self.auth_controller = AuthController()

    def register_routes(
        self,
    ) -> None:

        @self.auth_bp.route('/login', methods=['GET'])
        def login() -> Response:
            return self.auth_controller.login()

        @self.auth_bp.route('/callback', methods=['GET'])
        def google_auth_callback() -> Response:
            return self.auth_controller.google_auth_callback()

        self.app.register_blueprint(self.auth_bp)