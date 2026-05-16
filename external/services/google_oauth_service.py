import os
from typing import Any, Dict

from authlib.integrations.flask_client import OAuth
from flask import Flask, url_for
import jwt
import requests

from core.shared.errors import (
    OAuthAuthenticationError,
    OAuthConfigurationError,
)


class GoogleOAuthService:

    CLIENT_NAME = "google"

    def __init__(
        self,
    ) -> None:

        self.oauth = OAuth()

    def init_app(
        self,
        app: Flask,
    ) -> None:

        self.oauth.init_app(app)
        if self._is_configured():
            self._register_client()

    def _register_client(
        self,
    ) -> None:

        self.oauth.register(
            name=self.CLIENT_NAME,
            client_id=os.getenv("GOOGLE_CLIENT_ID"),
            client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
            server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
            client_kwargs={
                "scope": "openid email profile",
            },
        )

    def authorize_redirect(self):
        client = self._get_client()
        redirect_uri = url_for("auth.google_auth_callback", _external=True)
        return client.authorize_redirect(redirect_uri)

    def get_user_info(
        self,
    ) -> Dict[str, Any]:

        client = self._get_client()
        try:
            token = client.authorize_access_token()
            user_info = token.get("userinfo")
            if not user_info:
                user_info_response = client.get("userinfo")
                user_info_response.raise_for_status()
                user_info = user_info_response.json()
        except Exception as exc:
            raise OAuthAuthenticationError() from exc

        if not user_info:
            raise OAuthAuthenticationError()

        return dict(user_info)

    def validate_id_token(
        self,
        id_token: str,
    ) -> Dict[str, Any]:
        """
        Validate Google ID token and return the decoded payload.
        """
        try:
            # Get Google's public keys
            response = requests.get("https://www.googleapis.com/oauth2/v3/certs")
            response.raise_for_status()
            keys = response.json()["keys"]

            # Decode without verification first to get header
            header = jwt.get_unverified_header(id_token)
            kid = header.get("kid")

            # Find the correct key
            key = None
            for k in keys:
                if k["kid"] == kid:
                    key = k
                    break

            if not key:
                raise OAuthAuthenticationError("Invalid token: key not found")

            payload = jwt.decode(
                id_token,
                key,
                algorithms=["RS256"],
                audience=os.getenv("GOOGLE_CLIENT_ID"),
                issuer="https://accounts.google.com"
            )

            return payload

        except jwt.ExpiredSignatureError:
            raise OAuthAuthenticationError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise OAuthAuthenticationError(f"Invalid token: {str(e)}")
        except OAuthAuthenticationError:
            raise
        except Exception as exc:
            raise OAuthAuthenticationError() from exc

    def _get_client(self):
        if not self._is_configured():
            raise OAuthConfigurationError()

        client = self.oauth.create_client(self.CLIENT_NAME)
        if client is None:
            self._register_client()
            client = self.oauth.create_client(self.CLIENT_NAME)

        if client is None:
            raise OAuthConfigurationError()

        return client

    @staticmethod
    def _is_configured() -> bool:
        return bool(
            os.getenv("GOOGLE_CLIENT_ID")
            and os.getenv("GOOGLE_CLIENT_SECRET")
        )