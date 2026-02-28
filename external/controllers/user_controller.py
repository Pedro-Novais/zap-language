import os
from typing import (
    Any, 
    Dict,
)

from flask import (
    jsonify, 
    make_response,
)

from external.container import(
    user_repository,
    whatsapp_service,
    password_hasher_service,
    phone_verification_repository,
)
from external.utils import validate_request

from core.interactor import (
    CreateUserInteractor,
    AuthenticateUserInteractor,
    AddPhoneNumberInteractor,
)


class UserController:
    
    def __init__(
        self,
    ) -> None:
        
        self.create_user_interactor = CreateUserInteractor(
            user_repository=user_repository,
            password_hasher_service=password_hasher_service,
        )
        self.authenticate_user_interactor = AuthenticateUserInteractor(
            user_repository=user_repository,
            password_hasher_service=password_hasher_service,
        )
        self.add_phone_number_interactor = AddPhoneNumberInteractor(
            whatsapp_service=whatsapp_service,
            user_repository=user_repository,
            phone_verification_repository=phone_verification_repository,
        )

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
    
    def add_phone_number(
        self, 
        user_id: str,
        request: Dict[str, Any],
    ) -> Dict[str, Any]:
        
        required_fields = ["phoneNumber"]
        validate_request(
            request=request,
            required_fields=required_fields,
        )
        self.add_phone_number_interactor.add_phone_number(
            user_id=user_id,
            phone_number=request["phoneNumber"],
        )
        return {}, 201
    
    def verify_phone_number(
        self, 
        user_id: str,
        request: Dict[str, Any],
    ) -> Dict[str, Any]:
        
        required_fields = ["phoneNumber", "code"]
        validate_request(
            request=request,
            required_fields=required_fields,
        )
        self.add_phone_number_interactor.verify_phone_number_code(
            user_id=user_id,
            phone_number=request["phoneNumber"],
            code=request["code"],
        )
        return {}, 201
    
    def authenticate_user(
        self,
        request: Dict[str, Any],
    ) -> Dict[str, Any]:

        required_fields = ["email", "password"]
        validate_request(
            request=request,
            required_fields=required_fields,
        )
        token = self.authenticate_user_interactor.execute(
            email=request["email"],
            password=request["password"],
        )
        response = make_response(jsonify(), 200)
        response.set_cookie(
            key='authToken',
            value=token,
            httponly=True,  
            secure=os.getenv("ENV") == "production",    
            samesite='Strict',  
            max_age=60 * 60 * 24
        )
        return response
    
    def logout_user(
        self,
    ) -> Dict[str, Any]:

        response = make_response(jsonify({"message": "Logout realizado"}), 200)
        response.delete_cookie('authToken')
        return response
    