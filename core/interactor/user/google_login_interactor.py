import secrets
from datetime import datetime, timezone

from loguru import logger

from core.interface.repository import UserRepository
from core.interface.service import PasswordHasherService, PaymentService
from core.model import UserModel
from core.shared.auth import generate_auth_token


class GoogleLoginInteractor:

    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher_service: PasswordHasherService,
        payment_service: PaymentService,
    ) -> None:

        self.user_repository = user_repository
        self.password_hasher_service = password_hasher_service
        self.payment_service = payment_service

    def _try_create_payment_customer(
        self,
        user: UserModel,
    ) -> None:

        if user.payment_customer_id:
            return

        try:
            payment_customer_id = self.payment_service.create_customer(
                user_id=str(user.id),
                name=user.name,
                email=user.email,
            )
            self.user_repository.update_payment_customer_id(
                user_id=str(user.id),
                payment_customer_id=payment_customer_id,
            )
        except Exception as error:
            logger.error(
                f"Failed to create payment customer for user '{user.email}': {error}",
            )

    def execute(
        self,
        email: str,
        name: str,
        sub: str,
    ) -> str:

        logger.info(f"Processing Google login for email: {email}")

        last_login = datetime.now(timezone.utc)
        user_by_sub = self.user_repository.get_user_by_sub(sub=sub)
        user_by_email = self.user_repository.get_user_by_email(email=email)

        if not user_by_sub and not user_by_email:
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
            resolved = user_by_sub or user_by_email
            user = self.user_repository.update_google_login(
                user_id=str(resolved.id),
                sub=sub,
                last_login=last_login,
            )
            logger.info(f"Updated last login for Google user: {email}")

        self._try_create_payment_customer(user=user)

        return generate_auth_token(user_id=str(user.id))
