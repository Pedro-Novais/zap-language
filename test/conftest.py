import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from unittest.mock import create_autospec

from core.interface.repository import (
    UserRepository, 
    PhoneVerificationRepository,
    MessageHistoryRepository,
)
from core.interface.service import (
    WhatsappService,
    AITutorService,
    RedisService,
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
    return create_autospec(
        spec=UserRepository, 
        instance=True,
    )

@pytest.fixture
def phone_verification_repository_mock():
    return create_autospec(
        spec=PhoneVerificationRepository, 
        instance=True,
    )
