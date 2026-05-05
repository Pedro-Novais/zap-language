import os

from flask import jsonify, make_response, redirect, request, session

from core.interactor import GoogleLoginInteractor
from core.shared.errors import OAuthAuthenticationError


class AuthController:

    def __init__(
        self,
        google_oauth_service=None,
        password_hasher_service=None,
        user_repository=None,
        google_login_interactor=None,
    ) -> None:

        if google_oauth_service is None:
            from external.container import google_oauth_service as default_google_oauth_service
            google_oauth_service = default_google_oauth_service

        if password_hasher_service is None:
            from external.container import password_hasher_service as default_password_hasher_service
            password_hasher_service = default_password_hasher_service

        if user_repository is None:
            from external.container import user_repository as default_user_repository
            user_repository = default_user_repository

        self.google_oauth_service = google_oauth_service
        if google_login_interactor is None:
            self.google_login_interactor = GoogleLoginInteractor(
                user_repository=user_repository,
                password_hasher_service=password_hasher_service,
            )
        else:
            self.google_login_interactor = google_login_interactor

    def login(
        self,
    ):

        return self.google_oauth_service.authorize_redirect()

    def google_auth_callback(
        self,
    ):

        user_info = self.google_oauth_service.get_user_info()

        email = user_info.get("email")
        google_id = user_info.get("sub")
        name = user_info.get("name") or (email.split("@")[0] if email else None)
        if not email or not google_id or not name:
            raise OAuthAuthenticationError()

        token = self.google_login_interactor.execute(
            email=email,
            name=name,
            google_id=google_id,
        )
        session.clear()

        frontend_url = os.getenv("FRONTEND_URL")
        if frontend_url:
            response = make_response(redirect(frontend_url), 302)
        else:
            response = make_response(jsonify({"authenticated": True}), 200)

        response.set_cookie(
            key='authToken',
            value=token,
            httponly=True,
            secure=os.getenv("ENV") == "production",
            samesite='Lax',
            max_age=60 * 60 * 24,
        )
        return response

    def google_login(
        self,
    ):

        data = request.get_json()
        if not data or 'token' not in data:
            return make_response(jsonify({"error": "Token is required"}), 400)

        id_token = data['token']

        try:
            payload = self.google_oauth_service.validate_id_token(id_token)
        except OAuthAuthenticationError as e:
            return make_response(jsonify({"error": e.message_error}), 401)

        email = payload.get("email")
        sub = payload.get("sub")
        name = payload.get("name") or (email.split("@")[0] if email else None)

        if not email or not sub or not name:
            return make_response(jsonify({"error": "Invalid token payload"}), 400)

        token = self.google_login_interactor.execute(
            email=email,
            name=name,
            sub=sub,
        )

        return make_response(jsonify({"token": token}), 200)