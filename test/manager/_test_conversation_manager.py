import pytest
import json

import redis

from core.model import UserModel
from core.manager.conversation_manager import ConversationManager
from core.interface.service import (
    AITutorService,
    WhatsappService,
)
from core.manager import (
    UserManager,
    MessageHistoryManager,
)
from core.manager.key import RedisKeyManager
from core.manager.builder import InstructionBuilder


DEFAULT_PHONE = "5511999999999"
DEFAULT_MESSAGE = "Hello, I want to learn English"


class TestConversationManager:

    @pytest.fixture
    def manager(
        self,
        redis_client: redis.Redis,
        ai_tutor_service: AITutorService,
        whatsapp_service: WhatsappService,
        user_manager: UserManager,
        message_history_manager: MessageHistoryManager,
    ) -> ConversationManager:
        
        return ConversationManager(
            ai_tutor_service=ai_tutor_service,
            whatsapp_service=whatsapp_service,
            user_manager=user_manager,
            message_history_manager=message_history_manager,
            redis_client=redis_client,
        )

    def test_add_message_to_queue_successfully(
        self, 
        manager: ConversationManager, 
        redis_client: redis.Redis,
    ) -> None:
        
        manager.add_message_to_queue(phone=DEFAULT_PHONE, message_text=DEFAULT_MESSAGE)

        args, _ = redis_client.lpush.call_args
        payload = json.loads(args[1])
        
        assert payload["phone"] == DEFAULT_PHONE
        assert payload["message"] == DEFAULT_MESSAGE
        redis_client.lpush.assert_called_once()

    def test_process_message_should_return_false_if_user_is_banned(
        self, 
        manager: ConversationManager, 
        redis_client: redis.Redis,
    ) -> None:

        redis_client.exists.side_effect = RedisKeyManager.black_list_phone(phone=DEFAULT_PHONE)
        
        result = manager.process_message(phone=DEFAULT_PHONE)

        assert result is False
        
        redis_client.incr.assert_not_called()

    def test_process_message_should_ban_user_when_rate_limit_exceeded(
        self, 
        manager: ConversationManager, 
        redis_client: redis.Redis,
    ) -> None:

        redis_client.exists.return_value = False
        redis_client.incr.return_value = 4

        result = manager.process_message(phone=DEFAULT_PHONE)

        assert result is False

    # def test_reply_user_should_send_error_if_instruction_not_found(
    #     self, 
    #     manager: ConversationManager, 
    #     user_manager: UserManager, 
    #     whatsapp_service: WhatsappService, 
    #     redis_client: redis.Redis,
    #     instruction_builder: InstructionBuilder,
    # ) -> None:

    #     manager.instruction_builder = instruction_builder
    #     instruction_builder.build.return_value = None

    #     user_manager.get_study_settings_by_phone.return_value = UserModel(
    #         phone=DEFAULT_PHONE, 
    #         whatsapp_enabled=True,
    #         study_settings=None,
    #         id=1,
    #         email="",
    #         name="",
    #         created_at=None,
    #     )
        
    #     manager.reply_user(phone=DEFAULT_PHONE, message_text=DEFAULT_MESSAGE)
        
    #     instruction_builder.build.assert_called_once()
    #     whatsapp_service.send_text.assert_called_with(
    #         phone=DEFAULT_PHONE, 
    #         message="Para utilização desse serviço, é necessário habilitar nosso plano de estudo de idiomas."
    #     )
        
    def test_reply_user_should_send_error_if_user_not_found(
        self, 
        manager: ConversationManager, 
        user_manager: UserManager, 
        whatsapp_service: WhatsappService, 
        redis_client: redis.Redis,
    ) -> None:

        user_manager.get_study_settings_by_phone.return_value = None

        manager.reply_user(phone=DEFAULT_PHONE, message_text=DEFAULT_MESSAGE)

        whatsapp_service.send_text.assert_called_with(
            phone=DEFAULT_PHONE, 
            message="Para utilização desse serviço, é necessário habilitar nosso plano de estudo de idiomas."
        )
        