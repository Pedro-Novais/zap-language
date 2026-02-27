import sys
import os

import redis

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from unittest.mock import create_autospec

from core.interface.repository import UserRepository, PhoneVerificationRepository
from core.interface.service import (
    WhatsappService,
    AITutorService,
)
from core.manager import (
    UserManager,
    MessageHistoryManager,
)
from core.manager.builder import InstructionBuilder


@pytest.fixture
def redis_client():
    return create_autospec(spec=redis.Redis, instance=True)

@pytest.fixture
def user_manager():
    return create_autospec(spec=UserManager, instance=True)

@pytest.fixture
def message_history_manager():
    return create_autospec(spec=MessageHistoryManager, instance=True)

@pytest.fixture
def ai_tutor_service():
    return create_autospec(spec=AITutorService, instance=True)

@pytest.fixture
def whatsapp_service():
    return create_autospec(
        spec=WhatsappService, 
        instance=True,
    )

@pytest.fixture
def user_repository():
    return create_autospec(
        spec=UserRepository, 
        instance=True,
    )

@pytest.fixture
def phone_verification_repository():
    return create_autospec(
        spec=PhoneVerificationRepository, 
        instance=True,
    )

@pytest.fixture
def instruction_builder():
    return create_autospec(
        spec=InstructionBuilder, 
        instance=True,
    )
