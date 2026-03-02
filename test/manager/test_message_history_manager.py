from typing import List

import pytest
from unittest.mock import create_autospec
from datetime import datetime
from uuid import uuid4

from core.manager.message_history_manager import MessageHistoryManager
from core.model import MessageHistoryModel
from core.model.enum import MessageRoleModel
from core.shared.model import HistoryManagerConfig, SystemConfigModel
from core.interface.service import RedisService
from core.interface.repository import MessageHistoryRepository

DEFAULT_PHONE = "5511999999999"
DEFAULT_USER_ID = uuid4()   


class TestMessageHistoryManager:

    @pytest.fixture
    def config_mock(self) -> HistoryManagerConfig:
        config_model = SystemConfigModel(configs={})
        config = config_model.get_system_config().history
        return config

    @pytest.fixture
    def manager(
        self, 
        config_mock: HistoryManagerConfig, 
        redis_service_mock: RedisService, 
        history_repository_mock: MessageHistoryRepository,
    ) -> MessageHistoryManager:
        
        return MessageHistoryManager(
            config=config_mock,
            redis_service=redis_service_mock,
            history_repository=history_repository_mock
        )

    def test_get_message_history_cache_hit(
        self, 
        manager: MessageHistoryManager, 
        redis_service_mock: RedisService, 
        history_repository_mock: MessageHistoryRepository,
    ) -> None:
        
        quantity_messages = 5
        message_contente = "Teste"
        mock_history_messages = get_history_model(
            quantity_messages=quantity_messages,
            content=message_contente,
        )

        redis_service_mock.get_message_history.return_value = [m.model_dump_json() for m in mock_history_messages]

        result = manager.get_message_history(user_id=DEFAULT_USER_ID, phone=DEFAULT_PHONE)
        
        assert len(result) == quantity_messages
        for i in range(quantity_messages):
            assert result[i].content == f"{message_contente}-{i}"
            assert result[i].role == MessageRoleModel.USER if i % 2 == 0 else MessageRoleModel.ASSISTANT

        history_repository_mock.get_messages.assert_not_called()

    def test_get_message_history_cache_miss_db_hit(
        self, 
        manager: MessageHistoryManager, 
        redis_service_mock: RedisService, 
        history_repository_mock: MessageHistoryRepository,
    ) -> None:
        
        quantity_messages = 5
        message_contente = "Teste"
        db_messages = get_history_model(
            quantity_messages=quantity_messages,
            content=message_contente,
        )
        
        redis_service_mock.get_message_history.return_value = None
        history_repository_mock.get_messages.return_value = db_messages

        result = manager.get_message_history(
            user_id=DEFAULT_USER_ID, 
            phone=DEFAULT_PHONE,
        )
        
        history_repository_mock.get_messages.assert_called_once()
        assert result == db_messages
        assert redis_service_mock.set_message_history.call_count == quantity_messages

    def test_save_messages_calls_repo_and_cache(
        self, 
        manager: MessageHistoryManager, 
        redis_service_mock: RedisService, 
        history_repository_mock: MessageHistoryRepository,
    ) -> None:
        
        quantity_messages = 2
        message_contente = "Teste"
        db_messages = get_history_model(
            quantity_messages=quantity_messages,
            content=message_contente,
        )
        
        history_repository_mock.insert_messages.return_value = db_messages

        manager.save_messages(
            user_id=DEFAULT_USER_ID, 
            phone=DEFAULT_PHONE, 
            user_message="Teste-0", 
            tutor_message="Teste-1",
        )

        history_repository_mock.insert_messages.assert_called_once_with(
            user_id=DEFAULT_USER_ID, 
            messages=db_messages,
        )
        assert redis_service_mock.set_message_history.call_count == 2

    def test_clear_message_history(
        self, 
        manager: MessageHistoryManager, 
        redis_service_mock: RedisService, 
        history_repository_mock: MessageHistoryRepository,        
    ) -> None:

        manager.clear_message_history_for_user(DEFAULT_PHONE)

        redis_service_mock.delete_message_history.assert_called_once_with(phone=DEFAULT_PHONE)
        history_repository_mock.invalidate_messages.assert_called_once_with(phone=DEFAULT_PHONE)
        
def get_history_model(
    quantity_messages: int = 1, 
    content: str = "Olá",
    is_allowed: bool = True,
) -> List[MessageHistoryModel]:
    
    messages = []
    role = MessageRoleModel.USER
    for i in range(quantity_messages):
        messages.append(
            MessageHistoryModel(
                user_id=DEFAULT_USER_ID, 
                role=role, 
                content=f"{content}-{i}",
                is_allowed=is_allowed,
            )
        )
        role = MessageRoleModel.ASSISTANT if role == MessageRoleModel.USER else MessageRoleModel.USER

    return messages
