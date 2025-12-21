from flask import (
    Flask,
    request,
)

class UserRoute:

    def __init__(
            self,
            app: Flask,
        ) -> None:

        self.app = app
        self.route_base = '/api/users'

    def register_routes(
            self,
        ) -> None:

        @self.app.route(f'{self.route_base}/<int:user_id>', methods=['GET'])
        def get_user(user_id):
            return {"user_id": user_id, "name": "John Doe"}

        @self.app.route(f'{self.route_base}', methods=['POST'])
        def create_user():
            data = request.json
            return {"message": "User created", "user": data}, 201
        
        @self.app.route(f'{self.route_base}', methods=['PUT'])
        def update_user():
            data = request.json
            return {"message": "User created", "user": data}, 201
        
        @self.app.route(f'{self.route_base}', methods=['DELETE'])
        def delete_user():
            return {"message": "User delted"}, 201