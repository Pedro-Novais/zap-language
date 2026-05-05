import json
from unittest.mock import Mock, patch

import pytest
import requests
import jwt

from external.services.google_oauth_service import GoogleOAuthService
from core.shared.errors import OAuthAuthenticationError


class TestGoogleOAuthService:

    @pytest.fixture
    def service(self):
        return GoogleOAuthService()

    def test_validate_id_token_success(self, service: GoogleOAuthService):
        # Mock the requests.get for keys
        mock_keys_response = {
            "keys": [
                {
                    "kid": "test-kid",
                    "n": "test-n",
                    "e": "AQAB",
                    "kty": "RSA",
                    "alg": "RS256",
                    "use": "sig"
                }
            ]
        }

        # Create a mock token
        payload = {
            "iss": "https://accounts.google.com",
            "aud": "test-client-id",
            "sub": "123456789",
            "email": "user@example.com",
            "name": "User Name",
            "exp": 2000000000,
            "iat": 1000000000
        }

        # Mock the key for decoding
        mock_key = {
            "kid": "test-kid",
            "n": "test-n",
            "e": "AQAB",
            "kty": "RSA"
        }

        with patch('external.services.google_oauth_service.requests.get') as mock_get, \
             patch('external.services.google_oauth_service.jwt.get_unverified_header') as mock_header, \
             patch('external.services.google_oauth_service.jwt.decode') as mock_decode, \
             patch.dict('os.environ', {'GOOGLE_CLIENT_ID': 'test-client-id'}):

            mock_get.return_value.json.return_value = mock_keys_response
            mock_header.return_value = {"kid": "test-kid"}
            mock_decode.return_value = payload

            result = service.validate_id_token("mock.token.here")

            assert result == payload
            mock_decode.assert_called_once()

    def test_validate_id_token_expired(self, service: GoogleOAuthService):
        with patch('external.services.google_oauth_service.requests.get') as mock_get, \
             patch('external.services.google_oauth_service.jwt.get_unverified_header') as mock_header, \
             patch('external.services.google_oauth_service.jwt.decode') as mock_decode:

            mock_get.return_value.raise_for_status.return_value = None
            mock_get.return_value.json.return_value = {"keys": [{"kid": "test-kid", "n": "test-n", "e": "AQAB", "kty": "RSA"}]}
            mock_header.return_value = {"kid": "test-kid"}
            mock_decode.side_effect = jwt.ExpiredSignatureError("Token expired")

            with pytest.raises(OAuthAuthenticationError):
                service.validate_id_token("expired.token")

    def test_validate_id_token_invalid(self, service: GoogleOAuthService):
        with patch('external.services.google_oauth_service.requests.get') as mock_get, \
             patch('external.services.google_oauth_service.jwt.get_unverified_header') as mock_header, \
             patch('external.services.google_oauth_service.jwt.decode') as mock_decode:

            mock_get.return_value.raise_for_status.return_value = None
            mock_get.return_value.json.return_value = {"keys": [{"kid": "test-kid", "n": "test-n", "e": "AQAB", "kty": "RSA"}]}
            mock_header.return_value = {"kid": "test-kid"}
            mock_decode.side_effect = jwt.InvalidTokenError("Invalid token")

            with pytest.raises(OAuthAuthenticationError):
                service.validate_id_token("invalid.token")

    def test_validate_id_token_key_not_found(self, service: GoogleOAuthService):
        mock_keys_response = {"keys": []}

        with patch('external.services.google_oauth_service.requests.get') as mock_get, \
             patch('external.services.google_oauth_service.jwt.get_unverified_header') as mock_header:

            mock_get.return_value.json.return_value = mock_keys_response
            mock_header.return_value = {"kid": "unknown-kid"}

            with pytest.raises(OAuthAuthenticationError, match="Invalid token: key not found"):
                service.validate_id_token("token.with.unknown.kid")