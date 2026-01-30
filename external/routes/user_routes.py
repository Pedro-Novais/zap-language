from flask import (
    Flask,
    Blueprint,
    request,
    Request,
    Response,
)

from external.controllers.user_controller import UserController
from external.utils.middleware import token_required


class UserRoute:

    def __init__(
        self,
        app: Flask,
        base_route: str,
    ) -> None:

        self.app = app
        self.user_bp = Blueprint('users', __name__, url_prefix=f'{base_route}/user')
        self.user_controller = UserController()

    def register_routes(
        self,
    ) -> None:

        @self.user_bp.route("", methods=['POST'])
        def create_user() -> Response:
            return self.user_controller.create_user(request=request.json)

        @self.user_bp.route("/add-phone-number", methods=['POST'])
        @token_required
        def add_phone(user_id: str) -> Response:
            return self.user_controller.add_phone_number(
                user_id=user_id, 
                request=request.json,
            )
        
        @self.user_bp.route("/verify-phone-number", methods=['POST'])
        @token_required
        def verify_code_phone(user_id: str) -> Response:
            return self.user_controller.verify_phone_number(
                user_id=user_id, 
                request=request.json,
            )

        # @self.user_bp.route("", methods=['PUT'])
        # def update_user() -> Response:
        #     data = request.json
        #     return {"message": "User created", "user": data}, 201

        # @self.user_bp.route("", methods=['DELETE'])
        # def delete_user() -> Response:
        #     return {"message": "User deleted"}, 201

        @self.user_bp.route("/authenticate", methods=['POST'])
        def authenticate_user() -> Response:
            return self.user_controller.authenticate_user(request=request.json)

        @self.user_bp.route("/logout", methods=['POST'])
        def logout_user() -> Response:
            return self.user_controller.logout_user()
            
        self.app.register_blueprint(self.user_bp)