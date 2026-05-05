from datetime import datetime, timezone

from unittest.mock import create_autospec

from core.interactor.user.create_user_interactor import CreateUserInteractor
from core.interface.repository import UserRepository
from core.interface.service import PasswordHasherService, PaymentService
from core.model import UserModel


def test_execute_should_create_user_and_update_payment_customer_id():
    user_repository_mock = create_autospec(spec=UserRepository, instance=True)
    password_hasher_service_mock = create_autospec(spec=PasswordHasherService, instance=True)
    payment_service_mock = create_autospec(spec=PaymentService, instance=True)

    name = "Test User"
    email = "test@example.com"
    password = "secure_password"
    hashed_password = "hashed_secure_password"
    customer_id = "cust_123"

    user_model = UserModel(
        id="00000000-0000-0000-0000-000000000001",
        email=email,
        name=name,
        phone=None,
        whatsapp_enabled=False,
        is_valid=False,
        is_admin=False,
        created_at=datetime.now(timezone.utc),
        password=hashed_password,
        current_topic=None,
    )

    user_repository_mock.get_user_by_email.return_value = None
    password_hasher_service_mock.hash.return_value = hashed_password
    user_repository_mock.create.return_value = user_model
    payment_service_mock.create_customer.return_value = customer_id

    interactor = CreateUserInteractor(
        user_repository=user_repository_mock,
        password_hasher_service=password_hasher_service_mock,
        payment_service=payment_service_mock,
    )

    interactor.execute(name=name, email=email, password=password)

    user_repository_mock.create.assert_called_once_with(
        name=name,
        email=email,
        password_hash=hashed_password,
    )
    payment_service_mock.create_customer.assert_called_once_with(
        user_id=str(user_model.id),
        name=name,
        email=email,
    )
    user_repository_mock.update_payment_customer_id.assert_called_once_with(
        user_id=str(user_model.id),
        payment_customer_id=customer_id,
    )


def test_execute_should_create_user_even_when_payment_customer_creation_fails():
    user_repository_mock = create_autospec(spec=UserRepository, instance=True)
    password_hasher_service_mock = create_autospec(spec=PasswordHasherService, instance=True)
    payment_service_mock = create_autospec(spec=PaymentService, instance=True)

    name = "Test User"
    email = "test@example.com"
    password = "secure_password"
    hashed_password = "hashed_secure_password"

    user_model = UserModel(
        id="00000000-0000-0000-0000-000000000002",
        email=email,
        name=name,
        phone=None,
        whatsapp_enabled=False,
        is_valid=False,
        is_admin=False,
        created_at=datetime.now(timezone.utc),
        password=hashed_password,
        current_topic=None,
    )

    user_repository_mock.get_user_by_email.return_value = None
    password_hasher_service_mock.hash.return_value = hashed_password
    user_repository_mock.create.return_value = user_model
    payment_service_mock.create_customer.side_effect = RuntimeError("gateway unavailable")

    interactor = CreateUserInteractor(
        user_repository=user_repository_mock,
        password_hasher_service=password_hasher_service_mock,
        payment_service=payment_service_mock,
    )

    interactor.execute(name=name, email=email, password=password)

    user_repository_mock.create.assert_called_once_with(
        name=name,
        email=email,
        password_hash=hashed_password,
    )
    payment_service_mock.create_customer.assert_called_once_with(
        user_id=str(user_model.id),
        name=name,
        email=email,
    )
    user_repository_mock.update_payment_customer_id.assert_not_called()
