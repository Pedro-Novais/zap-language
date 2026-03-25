import pytest
from datetime import datetime
from uuid import uuid4

from core.shared.errors import (
    GlobalIALockError, 
    AiWithQuotaLimitReachedError,
)
from core.model import (
    UserModel, 
    StudySettingsModel,
)
from core.model.enum import (
    TeacherPersonaType, 
    TeacherCorrectionLevel, 
    TeacherLanguageDynamics, 
    UserPreferredLanguage,
)
from core.manager.conversation_manager import ConversationManager
from core.interface.service import (
    AITutorService,
    WhatsappService,
    RedisService,
)
from core.manager.services import (
    UserService, 
    MessageHistoryService,
)
from core.manager.command import CommandHandler
from core.shared.model import (
    ConversationManagerConfig,
    SystemConfigModel,
)
from core.manager.builder import CommandResponseBuilder



DEFAULT_PHONE = "5511999999999"
DEFAULT_MESSAGE = "Hello, I want to learn English"
DEFAULT_COMMAND_VALID = "!reset"
DEFAULT_COMMAND_INVALID = "!ajuda"


class TestConversationManager:

    @pytest.fixture
    def config_mock(self) -> ConversationManagerConfig:
        config_model = SystemConfigModel(configs={})
        config = config_model.get_system_config().conversation
        return config

    @pytest.fixture
    def manager(
        self,
        redis_service_mock: RedisService,
        ai_tutor_service_mock: AITutorService,
        whatsapp_service_mock: WhatsappService,
        user_service_mock: UserService,
        message_history_service_mock: MessageHistoryService,
        config_mock: ConversationManagerConfig,
        command_handler_mock: CommandHandler,
    ) -> ConversationManager:
        
        return ConversationManager(
            ai_tutor_service=ai_tutor_service_mock,
            whatsapp_service=whatsapp_service_mock,
            user_service=user_service_mock,
            message_history_service=message_history_service_mock,
            redis_service=redis_service_mock,
            config=config_mock,
            command_handler=command_handler_mock,
        )
        
    def test_process_message_user_banned_stops_processing(
        self, 
        manager: ConversationManager, 
        redis_service_mock: RedisService, 
        command_handler_mock: CommandHandler,
    ) -> None:

        redis_service_mock.user_is_banned.return_value = True

        manager.process_incoming_message(
            phone=DEFAULT_PHONE, 
            message=DEFAULT_MESSAGE,
        )

        redis_service_mock.delete_processing_phone.assert_called_once_with(phone=DEFAULT_PHONE)
        command_handler_mock.is_command.assert_not_called()

    def test_process_message_clears_cache_if_modified(
        self, 
        manager: ConversationManager, 
        redis_service_mock: RedisService, 
        message_history_service_mock: MessageHistoryService, 
        user_service_mock: UserService,
    ) -> None:

        redis_service_mock.user_is_banned.return_value = False
        redis_service_mock.has_update_to_user_profile.return_value = True

        manager.process_incoming_message(phone=DEFAULT_PHONE, message="Olá")

        message_history_service_mock.clear_message_history_for_user.assert_called_once_with(phone=DEFAULT_PHONE)
        user_service_mock.invalidate_user_cache.assert_called_once_with(phone=DEFAULT_PHONE)
        redis_service_mock.delete_update_user_profile.assert_called_once_with(phone=DEFAULT_PHONE)

    def test_process_message_as_command_success(
        self, 
        manager: ConversationManager, 
        redis_service_mock: RedisService, 
        command_handler_mock: CommandHandler, 
        whatsapp_service_mock: WhatsappService,
    ) -> None:

        command_message_respond = CommandResponseBuilder.response_for_reset_command()
        redis_service_mock.user_is_banned.return_value = False
        command_handler_mock.is_command.return_value = True
        command_handler_mock.handle_command.return_value = command_message_respond

        manager.process_incoming_message(
            phone=DEFAULT_PHONE, 
            message=DEFAULT_COMMAND_VALID,
        )

        command_handler_mock.handle_command.assert_called_once_with(
            phone=DEFAULT_PHONE, 
            user_message=DEFAULT_COMMAND_VALID,
        )
        whatsapp_service_mock.send_text.assert_called_once_with(
            phone=DEFAULT_PHONE, 
            message=command_message_respond,
        )
        
        redis_service_mock.delete_processing_phone.assert_called_once_with(phone=DEFAULT_PHONE)
        redis_service_mock.set_lock_global_ia.assert_not_called()
        
    def test_process_message_as_command_not_valid(
        self, 
        manager: ConversationManager, 
        redis_service_mock: RedisService, 
        command_handler_mock: CommandHandler, 
        whatsapp_service_mock: WhatsappService,
    ) -> None:

        command_message_respond = CommandResponseBuilder.response_for_error_command()
        
        redis_service_mock.user_is_banned.return_value = False
        command_handler_mock.is_command.return_value = True
        command_handler_mock.handle_command.return_value = command_message_respond

        manager.process_incoming_message(
            phone=DEFAULT_PHONE, 
            message=DEFAULT_COMMAND_VALID,
        )

        command_handler_mock.handle_command.assert_called_once_with(
            phone=DEFAULT_PHONE, 
            user_message=DEFAULT_COMMAND_VALID,
        )
        whatsapp_service_mock.send_text.assert_called_once_with(
            phone=DEFAULT_PHONE, 
            message=command_message_respond,
        )
        
        redis_service_mock.delete_processing_phone.assert_called_once_with(phone=DEFAULT_PHONE)
        redis_service_mock.set_lock_global_ia.assert_not_called()

    def test_process_message_as_tutor_success(
        self, 
        manager: ConversationManager, 
        redis_service_mock: RedisService, 
        command_handler_mock: CommandHandler, 
        user_service_mock: UserService, 
        ai_tutor_service_mock: AITutorService, 
        whatsapp_service_mock: WhatsappService, 
        message_history_service_mock: MessageHistoryService,
    ) -> None:
        
        tutor_message_response = "Resposta do Tutor"
        
        redis_service_mock.user_is_banned.return_value = False
        command_handler_mock.is_command.return_value = False
        redis_service_mock.has_lock_global_ia.return_value = False

        user_model = get_user_model(study_settings=get_study_settings_model())
        user_service_mock.get_user_profile.return_value = user_model
        
        ai_tutor_service_mock.get_tutor_response.return_value = tutor_message_response

        manager.process_incoming_message(
            phone=DEFAULT_PHONE, 
            message=DEFAULT_MESSAGE,
        )

        ai_tutor_service_mock.get_tutor_response.assert_called_once()
        whatsapp_service_mock.send_text.assert_called_once_with(
            phone=DEFAULT_PHONE, 
            message=tutor_message_response,
        )
        message_history_service_mock.save_messages.assert_called_once()
        
        redis_service_mock.delete_processing_phone.assert_called_once_with(phone=DEFAULT_PHONE)
        redis_service_mock.set_lock_global_ia.assert_called_once()

    def test_process_message_raises_global_ia_lock_and_keeps_processing_lock(
        self, 
        manager: ConversationManager, 
        redis_service_mock: RedisService, 
        command_handler_mock: CommandHandler,
    ) -> None:
        
        redis_service_mock.user_is_banned.return_value = False
        command_handler_mock.is_command.return_value = False
        redis_service_mock.has_lock_global_ia.return_value = True

        with pytest.raises(GlobalIALockError):
            manager.process_incoming_message(
                phone=DEFAULT_PHONE, 
                message=DEFAULT_MESSAGE,
            )

        redis_service_mock.delete_processing_phone.assert_not_called()

    def test_process_message_handles_quota_limit_error(
        self, 
        manager: ConversationManager, 
        redis_service_mock: RedisService, 
        command_handler_mock: CommandHandler, 
        user_service_mock: UserService, 
        ai_tutor_service_mock: AITutorService,
    ) -> None:

        user_model = get_user_model(study_settings=get_study_settings_model())
        
        redis_service_mock.user_is_banned.return_value = False
        redis_service_mock.has_lock_global_ia.return_value = False
        command_handler_mock.is_command.return_value = False
        user_service_mock.get_user_profile.return_value = user_model
        ai_tutor_service_mock.get_tutor_response.side_effect = AiWithQuotaLimitReachedError()

        with pytest.raises(AiWithQuotaLimitReachedError):
            manager.process_incoming_message(phone=DEFAULT_PHONE, message="Hello")

        redis_service_mock.set_lock_global_ia.assert_called_once_with(timeout=30)
        redis_service_mock.delete_processing_phone.assert_not_called()

    def test_process_message_bans_user_if_profile_not_found(
        self, 
        manager: ConversationManager, 
        redis_service_mock: RedisService, 
        command_handler_mock: CommandHandler, 
        user_service_mock: UserService,
    ) -> None:
        
        redis_service_mock.user_is_banned.return_value = False
        command_handler_mock.is_command.return_value = False
        redis_service_mock.has_lock_global_ia.return_value = False
        user_service_mock.get_user_profile.return_value = None

        manager.process_incoming_message(
            phone=DEFAULT_PHONE, 
            message=DEFAULT_MESSAGE,
        )

        redis_service_mock.ban_phone.assert_called_once_with(phone=DEFAULT_PHONE)
        redis_service_mock.delete_processing_phone.assert_called_once_with(phone=DEFAULT_PHONE)

    def test_process_message_generic_exception_clears_lock(
        self, 
        manager: ConversationManager, 
        redis_service_mock: RedisService, 
        ai_tutor_service_mock: AITutorService,
        command_handler_mock: CommandHandler,
    ) -> None:

        redis_service_mock.user_is_banned.return_value = False
        command_handler_mock.is_command.return_value = False
        redis_service_mock.has_lock_global_ia.return_value = False
        ai_tutor_service_mock.get_tutor_response.side_effect = Exception("Erro Fatal")

        with pytest.raises(Exception):
            manager.process_incoming_message(
                phone=DEFAULT_PHONE, 
                message=DEFAULT_MESSAGE,
            )

        redis_service_mock.delete_processing_phone.assert_called_once_with(phone=DEFAULT_PHONE)
        
def get_user_model(study_settings: StudySettingsModel) -> UserModel:
    
    return UserModel(
        id = uuid4(),
        email = "teste",
        name ="teste",
        phone = DEFAULT_PHONE,
        whatsapp_enabled = True,
        created_at = datetime.now(),
        study_settings=study_settings,
        password = "teste",
        current_topic = None
    )

def get_study_settings_model() -> StudySettingsModel:
    
    return StudySettingsModel(
        id=uuid4(),
        user_id=uuid4(),
        persona_type=TeacherPersonaType.FUNNY,
        correction_level=TeacherCorrectionLevel.LIGHT,
        preferred_topics=["esportes"],
        language_ratio=100,
        language_dynamics=TeacherLanguageDynamics.BILINGUE,
        receive_newsletters=True,
        preferred_language=UserPreferredLanguage.ENGLISH,
        created_at=datetime.now(),
    )
