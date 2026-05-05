from loguru import logger

from core.interface.repository import UserRepository
from core.interface.service import PasswordHasherService, PaymentService
from core.shared.errors import EmailAlreadyExistsError


class CreateUserInteractor:
    
    def __init__(
        self, 
        user_repository: UserRepository,
        password_hasher_service: PasswordHasherService,
        payment_service: PaymentService,
    ) -> None:
        
        self.user_repository = user_repository
        self.password_hasher_service = password_hasher_service
        self.payment_service = payment_service

    def execute(
        self,
        name: str,
        email: str,
        password: str,
    ) -> None:
        
        logger.info(f"Creating user with email: {email}")
        
        if self.user_repository.get_user_by_email(email):
            logger.error(f"Email '{email}' already exists")
            raise EmailAlreadyExistsError(email=email)
        
        password_hash = self.password_hasher_service.hash(password=password)
        user = self.user_repository.create(
            name=name,
            email=email,
            password_hash=password_hash,
        )

        try:
            payment_customer_id = self.payment_service.create_customer(
                user_id=user.id,
                name=name,
                email=email,
            )
            self.user_repository.update_payment_customer_id(
                user_id=user.id,
                payment_customer_id=payment_customer_id,
            )
        except Exception as error:
            logger.error(
                f"Failed to create payment customer for user '{email}': {error}"
            )

        logger.info(f"User with email '{email}' created successfully")
        return