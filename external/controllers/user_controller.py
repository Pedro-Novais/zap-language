from typing import (
    Any, 
    Dict,
)

from external.repositories import UserRepositoryImpl
from external.services.bycrypt_password_hasher_service import BcryptPasswordHasherService
from external.utils import validate_request
from core.interactor import CreateUserInteractor


class UserController:
    
    def __init__(
        self,
    ) -> None:

        self.user_repository = UserRepositoryImpl()
        
        self.password_hasher_service = BcryptPasswordHasherService()
        
        self.create_user_interactor = CreateUserInteractor(
            user_repository=self.user_repository,
            password_hasher_service=self.password_hasher_service,
        )
    
    def get_user(
        self,
        user_id: str,
    ) -> Any:
        
        interactor = CreateUserInteractor(user_repository=self.user_repository)
        interactor.execute(name="", email="", password="")
        return {"message": "User created successfully"}, 201

    def create_user(
        self, 
        request: Dict[str, Any],
    ) -> Dict[str, Any]:
        
        required_fields = ["name", "email", "password"]
        validate_request(
            request=request,
            required_fields=required_fields,
        )
        self.create_user_interactor.execute(
            name=request["name"],
            email=request["email"],
            password=request["password"],
        )
        return {}, 201
        
    def authenticate_user(
        self,
        request: Dict[str, Any],
    ) -> Dict[str, Any]:

        pass
        return {"token": "fake-jwt-token"}
    
    @staticmethod
    def _validate_autheticate_user_request(
        request: Dict[str, Any],
    ) -> Any:

        try:
            email = request['email']
            password = request['password']
        except KeyError as e:
            raise ValueError(f'Missing required field: {e.args[0]}')

    
    @staticmethod
    def _validate_create_user_request(
        request: Dict[str, Any],
    ) -> Any:

        try:
            name = request['name']
            email = request['email']
            password = request['password']
        except KeyError as e:
            raise ValueError(f'Missing required field: {e.args[0]}')
