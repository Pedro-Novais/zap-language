from flask import (
    Flask,
    Blueprint,
    request,
    Request,
    Response,
)

from external.controllers.user_controller import UserController


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
        def create_user():
            return self.user_controller.create_user(request=request.json)
        
        @self.user_bp.route("", methods=['PUT'])
        def update_user():
            data = request.json
            return {"message": "User created", "user": data}, 201

        @self.user_bp.route("", methods=['DELETE'])
        def delete_user():
            return {"message": "User deleted"}, 201

        @self.user_bp.route("/authenticate", methods=['POST'])
        def authenticate_user():
            return self.user_controller.authenticate_user(request=request.json)
            
        self.app.register_blueprint(self.user_bp)