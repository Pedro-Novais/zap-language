import json
from unittest.mock import Mock, patch

import pytest
from faker import Faker

from external.controllers.auth_controller import AuthController
from core.shared.errors import OAuthAuthenticationError

fake = Faker()


class TestAuthController:

    @pytest.fixture
    def app(self):
        from flask import Flask

        return Flask(__name__)

    @pytest.fixture
    def app_context(self, app):
        with app.app_context():
            yield

    @pytest.fixture
    def mock_request(self):
        with patch('external.controllers.auth_controller.request', new=Mock()) as mock_req:
            yield mock_req

    @pytest.fixture
    def mock_google_oauth_service(self):
        return Mock()

    @pytest.fixture
    def mock_google_login_interactor(self):
        return Mock()

    @pytest.fixture
    def controller(self, mock_google_oauth_service, mock_google_login_interactor):
        return AuthController(
            google_oauth_service=mock_google_oauth_service,
            password_hasher_service=Mock(),
            user_repository=Mock(),
            google_login_interactor=mock_google_login_interactor,
        )

    def test_google_login_success(
        self,
        controller: AuthController,
        mock_request,
        mock_google_oauth_service,
        mock_google_login_interactor,
        app_context,
    ):
        # Arrange
        id_token = "valid.jwt.token"
        payload = {
            "sub": "google-sub-123",
            "email": "user@example.com",
            "name": "User Name"
        }
        auth_token = "generated.auth.token"

        mock_request.get_json.return_value = {"token": id_token}
        mock_google_oauth_service.validate_id_token.return_value = payload
        mock_google_login_interactor.execute.return_value = auth_token

        # Act
        response = controller.google_login()

        # Assert
        assert response.status_code == 200
        response_data = json.loads(response.get_data(as_text=True))
        assert response_data["token"] == auth_token
        mock_google_oauth_service.validate_id_token.assert_called_once_with(id_token)
        mock_google_login_interactor.execute.assert_called_once_with(
            email="user@example.com",
            name="User Name",
            sub="google-sub-123"
        )

    def test_google_login_missing_token(
        self,
        controller: AuthController,
        mock_request,
        app_context,
    ):
        # Arrange
        mock_request.get_json.return_value = {}

        # Act
        response = controller.google_login()

        # Assert
        assert response.status_code == 400
        response_data = json.loads(response.get_data(as_text=True))
        assert "Token is required" in response_data["error"]

    def test_google_login_invalid_token(
        self,
        controller: AuthController,
        mock_request,
        mock_google_oauth_service,
        app_context,
    ):
        # Arrange
        id_token = "invalid.jwt.token"
        mock_request.get_json.return_value = {"token": id_token}
        mock_google_oauth_service.validate_id_token.side_effect = OAuthAuthenticationError()

        # Act
        response = controller.google_login()

        # Assert
        assert response.status_code == 401
        response_data = json.loads(response.get_data(as_text=True))
        assert response_data["error"] == "Falha na autenticação com o Google"

    def test_google_login_invalid_payload(
        self,
        controller: AuthController,
        mock_request,
        mock_google_oauth_service,
        app_context,
    ):
        # Arrange
        id_token = "valid.jwt.token"
        payload = {
            "sub": None,
            "email": "user@example.com",
            "name": "User Name"
        }
        mock_request.get_json.return_value = {"token": id_token}
        mock_google_oauth_service.validate_id_token.return_value = payload

        # Act
        response = controller.google_login()

        # Assert
        assert response.status_code == 400
        response_data = json.loads(response.get_data(as_text=True))
        assert "Invalid token payload" in response_data["error"]

    def test_google_login_missing_name_uses_email_prefix(
        self,
        controller: AuthController,
        mock_request,
        mock_google_oauth_service,
        mock_google_login_interactor,
        app_context,
    ):
        # Arrange
        id_token = "valid.jwt.token"
        payload = {
            "sub": "google-sub-123",
            "email": "user@example.com",
            "name": None
        }
        auth_token = "generated.auth.token"

        mock_request.get_json.return_value = {"token": id_token}
        mock_google_oauth_service.validate_id_token.return_value = payload
        mock_google_login_interactor.execute.return_value = auth_token

        # Act
        response = controller.google_login()

        # Assert
        assert response.status_code == 200
        mock_google_login_interactor.execute.assert_called_once_with(
            email="user@example.com",
            name="user",
            sub="google-sub-123"
        )