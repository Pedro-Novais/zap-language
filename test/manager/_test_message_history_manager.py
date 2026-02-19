import pytest
from unittest.mock import MagicMock
from datetime import datetime
from uuid import uuid4

from core.manager.message_history_manager import MessageHistoryManager
from core.model import MessageHistoryModel
from core.model.enum import MessageRoleModel

@pytest.fixture
def mock_redis():
    return MagicMock()

@pytest.fixture
def mock_repo():
    return MagicMock()

@pytest.fixture
def manager(mock_redis, mock_repo):
    return MessageHistoryManager(
        redis_client=mock_redis,
        history_repository=mock_repo,
        limit=10
    )

@pytest.fixture
def user_id():
    return str(uuid4())

def test_get_message_history_cache_hit(manager, mock_redis, mock_repo, user_id):
    """Deve retornar histórico do Redis se estiver disponível"""
    # Arrange
    mock_msg = MessageHistoryModel(
        id=uuid4(), user_id=uuid4(), role=MessageRoleModel.USER, 
        content="Hello", created_at=datetime.now()
    )
    mock_redis.lrange.return_value = [mock_msg.model_dump_json()]
    
    # Act
    result = manager.get_message_history(user_id)
    
    # Assert
    assert len(result) == 1
    assert result[0].content == "Hello"
    mock_redis.lrange.assert_called_once()
    mock_repo.get_messages.assert_not_called()

def test_get_message_history_cache_miss(manager, mock_redis, mock_repo, user_id):
    """Deve buscar do banco e salvar no Redis se cache estiver vazio"""
    # Arrange
    mock_redis.lrange.return_value = [] # Cache vazio
    mock_msg = MessageHistoryModel(
        id=uuid4(), user_id=uuid4(), role=MessageRoleModel.USER, 
        content="Hi DB", created_at=datetime.now()
    )
    mock_repo.get_messages.return_value = [mock_msg]
    
    # Act
    result = manager.get_message_history(user_id)
    
    # Assert
    assert len(result) == 1
    assert result[0].content == "Hi DB"
    mock_repo.get_messages.assert_called_once()
    mock_redis.lpush.assert_called()

def test_save_messages(manager, mock_redis, mock_repo, user_id):
    """Deve salvar mensagens no banco e atualizar o cache"""
    # Arrange
    mock_repo.insert_messages.return_value = []
    
    # Act
    manager.save_messages(user_id, "User Msg", "Tutor Msg")
    
    # Assert
    mock_repo.insert_messages.assert_called_once()
    assert mock_redis.lpush.call_count == 2
