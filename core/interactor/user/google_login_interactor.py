import secrets
from datetime import datetime, timezone

from loguru import logger

from core.interface.repository import UserRepository
from core.interface.service import PasswordHasherService
from core.shared.auth import generate_auth_token


class GoogleLoginInteractor:

    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher_service: PasswordHasherService,
    ) -> None:

        self.user_repository = user_repository
        self.password_hasher_service = password_hasher_service

    def execute(
        self,
        email: str,
        name: str,
        sub: str,
    ) -> str:

        logger.info(f"Processing Google login for email: {email}")

        last_login = datetime.now(timezone.utc)
        user = self.user_repository.get_user_by_sub(sub=sub)
        if not user:
            generated_password = secrets.token_urlsafe(32)
            password_hash = self.password_hasher_service.hash(password=generated_password)
            user = self.user_repository.create_google_user(
                name=name,
                email=email,
                sub=sub,
                password_hash=password_hash,
                last_login=last_login,
            )
            logger.info(f"Created new user from Google login: {email}")
        else:
            user = self.user_repository.update_google_login(
                user_id=str(user.id),
                sub=sub,
                last_login=last_login,
            )
            logger.info(f"Updated last login for Google user: {email}")

        return generate_auth_token(user_id=str(user.id))