import sys
import os

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from unittest.mock import create_autospec

from core.interface.repository import (
    UserRepository, 
    PhoneVerificationRepository,
    MessageHistoryRepository,
    PlanRepository,
    SubscriptionRepository,
    ScenarioRepository,
)
from core.interface.service import (
    WhatsappService,
    AITutorService,
    RedisService,
    PasswordHasherService,
    PaymentService,
)
from core.manager.services import (
    UserService, 
    MessageHistoryService,
)


@pytest.fixture
def history_repository_mock():
    return create_autospec(
        spec=MessageHistoryRepository, 
        instance=True,
    )

@pytest.fixture
def redis_service_mock():
    return create_autospec(
        spec=RedisService, 
        instance=True,
    )

@pytest.fixture
def user_service_mock():
    return create_autospec(
        spec=UserService, 
        instance=True,
    )

@pytest.fixture
def message_history_service_mock():
    return create_autospec(
        spec=MessageHistoryService, 
        instance=True
    )

@pytest.fixture
def ai_tutor_service_mock():
    return create_autospec(
        spec=AITutorService, 
        instance=True,
    )

@pytest.fixture
def whatsapp_service_mock():
    return create_autospec(
        spec=WhatsappService, 
        instance=True,
    )

@pytest.fixture
def user_repository_mock():
    mock = create_autospec(
        spec=UserRepository,
        instance=True,
    )
    mock.get_user_by_phone_number.return_value = None
    mock.get_phone_number_by_user_id.return_value = None
    mock.get_user_by_sub.return_value = None
    return mock
    

@pytest.fixture
def phone_verification_repository_mock():
    return create_autospec(
        spec=PhoneVerificationRepository, 
        instance=True,
    )


@pytest.fixture
def plan_repository_mock():
    return create_autospec(
        spec=PlanRepository,
        instance=True,
    )


@pytest.fixture
def subscription_repository_mock():
    return create_autospec(
        spec=SubscriptionRepository,
        instance=True,
    )


@pytest.fixture
def subscription_payment_service_mock():
    return create_autospec(
        spec=PaymentService,
        instance=True,
    )


@pytest.fixture
def password_hasher_service_mock():
    return create_autospec(
        spec=PasswordHasherService,
        instance=True,
    )


@pytest.fixture
def scenario_repository_mock():
    return create_autospec(
        spec=ScenarioRepository,
        instance=True,
    )
