import pytest
from unittest.mock import MagicMock
from uuid import uuid4

from core.manager.conversation_manager import ConversationManager
from core.model import UserModel

@pytest.fixture
def mock_ai(): return MagicMock()

@pytest.fixture
def mock_whatsapp(): return MagicMock()

@pytest.fixture
def mock_user_manager(): return MagicMock()

@pytest.fixture
def mock_history_manager(): return MagicMock()

@pytest.fixture
def mock_redis(): return MagicMock()

@pytest.fixture
def manager(mock_ai, mock_whatsapp, mock_user_manager, mock_history_manager, mock_redis):
    mgr = ConversationManager(
        ai_tutor_service=mock_ai,
        whatsapp_service=mock_whatsapp,
        user_manager=mock_user_manager,
        message_history_manager=mock_history_manager,
        redis_client=mock_redis
    )
    mgr.instruction_builder = MagicMock()
    return mgr

def test_process_and_respond_success(manager, mock_redis, mock_user_manager, mock_ai, mock_whatsapp, mock_history_manager):
    """Fluxo feliz: Usuário permitido, processa IA e responde"""
    # Arrange
    phone = "5511999999999"
    msg = "Hello teacher"
    
    # Mocks do Redis para _is_allowed retornar True
    mock_redis.exists.return_value = False # Não está banido nem processando
    mock_redis.incr.return_value = 1 # Rate limit ok
    
    # Mock do Usuário
    mock_user = MagicMock(spec=UserModel)
    mock_user.id = uuid4()
    mock_user.whatsapp_enabled = True
    mock_user_manager.get_study_settings_by_phone.return_value = mock_user
    
    # Mock da IA e Instrução
    manager.instruction_builder.build.return_value = "System Prompt"
    mock_ai.get_tutor_response.return_value = "Hello Student"
    
    # Act
    manager.process_and_respond(phone, msg)
    
    # Assert
    mock_whatsapp.send_text.assert_called_with(phone=phone, message="Hello Student")
    mock_history_manager.save_messages.assert_called()
    mock_redis.delete.assert_called()

def test_process_and_respond_user_disabled(manager, mock_redis, mock_user_manager, mock_whatsapp, mock_ai):
    """Se usuário estiver desativado (whatsapp_enabled=False), deve ir para blacklist"""
    # Arrange
    phone = "5511999999999"
    mock_redis.exists.return_value = False
    mock_redis.incr.return_value = 1
    mock_user = MagicMock(spec=UserModel)
    mock_user.whatsapp_enabled = False
    mock_user_manager.get_study_settings_by_phone.return_value = mock_user
    
    # Act
    manager.process_and_respond(phone, "Hi")
    
    # Assert
    mock_whatsapp.send_text.assert_not_called()
    mock_ai.get_tutor_response.assert_not_called()
    assert mock_redis.setex.called
