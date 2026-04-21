import os

from flask import jsonify, make_response, redirect, session

from core.interactor import GoogleLoginInteractor
from core.shared.errors import OAuthAuthenticationError
from external.container import (
    google_oauth_service,
    password_hasher_service,
    user_repository,
)


class AuthController:

    def __init__(
        self,
    ) -> None:

        self.google_oauth_service = google_oauth_service
        self.google_login_interactor = GoogleLoginInteractor(
            user_repository=user_repository,
            password_hasher_service=password_hasher_service,
        )

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