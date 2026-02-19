import pytest
from unittest.mock import MagicMock
from uuid import uuid4

from core.manager.user_manager import UserManager
from core.model import UserModel

@pytest.fixture
def mock_redis():
    return MagicMock()

@pytest.fixture
def mock_repo():
    return MagicMock()

@pytest.fixture
def manager(mock_redis, mock_repo):
    return UserManager(
        redis_client=mock_redis,
        user_repository=mock_repo
    )

@pytest.fixture
def phone():
    return "5511999999999"

def test_get_study_settings_by_phone_cache_hit(manager, mock_redis, mock_repo, phone):
    """Deve retornar usuário deserializado do Redis"""
    # Arrange
    mock_user_json = f'{{"id": "{uuid4()}", "name": "Test", "email": "t@t.com", "phone": "{phone}", "whatsapp_enabled": true, "created_at": "2023-01-01T00:00:00", "study_settings": null}}'
    mock_redis.get.return_value = mock_user_json
    
    # Act
    result = manager.get_study_settings_by_phone(phone)
    
    # Assert
    assert result is not None
    assert result.phone == phone
    mock_repo.get_user_by_phone_number.assert_not_called()

def test_get_study_settings_by_phone_cache_miss_found_db(manager, mock_redis, mock_repo, phone):
    """Deve buscar no banco e salvar no Redis se não estiver no cache"""
    # Arrange
    mock_redis.get.return_value = None
    mock_user = MagicMock(spec=UserModel)
    mock_user.model_dump_json.return_value = "{}"
    mock_repo.get_user_by_phone_number.return_value = mock_user
    
    # Act
    result = manager.get_study_settings_by_phone(phone)
    
    # Assert
    assert result is not None
    mock_redis.setex.assert_called_once()

def test_get_study_settings_by_phone_not_found(manager, mock_redis, mock_repo, phone):
    """Deve retornar None se usuário não existir em lugar nenhum"""
    # Arrange
    mock_redis.get.return_value = None
    mock_repo.get_user_by_phone_number.return_value = None
    
    # Act
    result = manager.get_study_settings_by_phone(phone)
    
    # Assert
    assert result is None
