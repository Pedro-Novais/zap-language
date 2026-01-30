import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from unittest.mock import create_autospec

from core.interface.repository import UserRepository, PhoneVerificationRepository
from core.interface.service import WhatsappService


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
