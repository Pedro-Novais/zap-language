import os
from typing import (
    Any, 
    Dict,
    Tuple,
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
    subscription_repository,
    send_email_service,
)
from external.utils import validate_request

from core.interactor import (
    CreateUserInteractor,
    AuthenticateUserInteractor,
    AddPhoneNumberInteractor,
    UserInteractor,
    ChangePasswordInteractor,
    ForgotPasswordInteractor,
    ResetPasswordInteractor,
)
from core.interactor.user import (
    RequestEmailVerificationInteractor,
    VerifyEmailInteractor,
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
        self.change_password_interactor = ChangePasswordInteractor(
            user_repository=user_repository,
            password_hasher_service=password_hasher_service,
        )
        self.forgot_password_interactor = ForgotPasswordInteractor(
            user_repository=user_repository,
            send_email_service=send_email_service,
            phone_verification_repository=phone_verification_repository,
        )
        self.reset_password_interactor = ResetPasswordInteractor(
            user_repository=user_repository,
            phone_verification_repository=phone_verification_repository,
            password_hasher_service=password_hasher_service,
        )
        self.request_email_verification_interactor = RequestEmailVerificationInteractor(
            user_repository=user_repository,
            phone_verification_repository=phone_verification_repository,
            send_email_service=send_email_service,
        )
        self.verify_email_interactor = VerifyEmailInteractor(
            user_repository=user_repository,
            phone_verification_repository=phone_verification_repository,
        )
        self.interactor = UserInteractor(user_repository=user_repository)

    def get_user_info(
        self,
        user_id: str,
    ) -> Tuple[Dict[str, Any], int]:
        
        user_model = self.interactor.get_user_info(user_id=user_id)
        user_data = user_model.model_dump()

        user_data.pop('id', None)
        study_settings = user_data.get('study_settings')
        if study_settings:
            study_settings.pop('user_id', None)

            if study_settings.get('created_at'):
                study_settings['created_at'] = study_settings['created_at'].isoformat()

        if user_data.get('created_at'):
            user_data['created_at'] = user_data['created_at'].isoformat()

        # Buscar última assinatura
        subscription = subscription_repository.get_last_by_user_id(user_id=user_id)
        subscription_data = {}
        if subscription:
            subscription_dict = subscription.model_dump(mode='json')
            subscription_data = {
                'id': str(subscription_dict.get('id')),
                'planId': str(subscription_dict.get('plan_id')),
                'status': subscription_dict.get('status'),
                'startedAt': subscription_dict.get('started_at'),
                'expiresAt': subscription_dict.get('expires_at'),
                'isActive': subscription_dict.get('is_active'),
                'gateway': subscription_dict.get('gateway'),
                'plan': subscription_dict.get('plan'),
            }

        user_data['subscription'] = subscription_data
        return jsonify(user_data), 200

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
    
    def change_password(
        self,
        user_id: str,
        request: Dict[str, Any],
    ) -> Dict[str, Any]:
        
        required_fields = ["oldPassword", "newPassword"]
        validate_request(
            request=request,
            required_fields=required_fields,
        )
        self.change_password_interactor.execute(
            user_id=user_id,
            old_password=request["oldPassword"],
            new_password=request["newPassword"],
        )
        return {}, 200

    def forgot_password(
        self,
        request: Dict[str, Any],
    ) -> Dict[str, Any]:

        required_fields = ["email"]
        validate_request(
            request=request,
            required_fields=required_fields,
        )
        self.forgot_password_interactor.execute(
            email=request["email"],
        )
        return {}, 200

    def reset_password(
        self,
        request: Dict[str, Any],
    ) -> Dict[str, Any]:

        required_fields = ["password", "token"]
        validate_request(
            request=request,
            required_fields=required_fields,
        )

        self.reset_password_interactor.execute(
            token=request["token"],
            new_password=request["password"],
        )

        return {}, 200

    def logout_user(
        self,
    ) -> Dict[str, Any]:

        response = make_response(jsonify({"message": "Logout realizado"}), 200)
        response.delete_cookie('authToken')
        return response

    def request_email_verification(
        self,
        user_id: str,
    ) -> Dict[str, Any]:
        
        self.request_email_verification_interactor.execute(
            user_id=user_id,
        )
        
        return {}, 200

    def verify_email(
        self,
        user_id: str,
        request: Dict[str, Any],
    ) -> Dict[str, Any]:
        
        required_fields = ["code"]
        validate_request(
            request=request,
            required_fields=required_fields,
        )
        self.verify_email_interactor.execute(
            user_id=user_id,
            code=request["code"],
        )
        
        return {}, 200
    