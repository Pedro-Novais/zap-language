from loguru import logger

from core.shared.model import ConversationManagerConfig
from core.shared.errors import (
    ErrorSendingMessageToWhatsapp,
    GlobalIALockError,
    UserBannedError,
    AiWithQuotaLimitReachedError,
)
from core.manager.message_history_manager import MessageHistoryManager
from core.manager.user_manager import UserManager
from core.manager.command import CommandHandler
from core.manager.builder import InstructionBuilder
from core.interface.service import (
    AITutorService,
    WhatsappService,
    RedisService,
)


class ConversationManager:

    def __init__(
        self,
        config: ConversationManagerConfig,
        ai_tutor_service: AITutorService, 
        whatsapp_service: WhatsappService,
        redis_service: RedisService,
        user_manager: UserManager,
        message_history_manager: MessageHistoryManager,
        command_handler: CommandHandler,
    ) -> None:
        
        self.config = config

        self.user_manager = user_manager
        self.message_history_manager = message_history_manager

        self.command_handler = command_handler
        
        self.ai_tutor_service = ai_tutor_service
        self.whatsapp_service = whatsapp_service
        self.redis_service = redis_service

        self.instruction_builder = InstructionBuilder()

    def process_incoming_message(
        self, 
        phone: str, 
        message: str,
    ) -> None:
        
        try:
            self.__checking_if_user_is_allowed(phone=phone)
            self.__invalidate_cache_if_user_has_been_modified(phone=phone)
            
            is_command_message = self.command_handler.is_command(user_message=message)
            if is_command_message:
                self.__respond_to_command(
                    phone=phone, 
                    message_text=message,
                )
            else:
                self.__respond_user_with_tutor_message(
                    phone=phone, 
                    message_text=message,
                )
            
            self.__finalize_message_processing(
                phone=phone,
                is_command_message=is_command_message,
            )
        
        except UserBannedError:
            self.redis_service.delete_processing_phone(phone=phone)
            return
        
        except GlobalIALockError:
            logger.warning(f"Global IA lock error")
            raise
        
        except ErrorSendingMessageToWhatsapp:
            logger.error(f"Failed to send message to {phone} by whatsapp")
            raise
        
        except AiWithQuotaLimitReachedError:
            logger.warning(f"AI quota limit reached")
            self.redis_service.set_lock_global_ia(timeout=30)
            raise
        
        except Exception:
            logger.error(f"Unexpected error processing message from {phone}", exc_info=True)
            logger.info(f"Removing phone: {phone} from processing queue")
            self.redis_service.delete_processing_phone(phone=phone)
            raise
        
    def __checking_if_user_is_allowed(
        self, 
        phone: str, 
    ) -> None:

        if self.redis_service.user_is_banned(phone=phone):
            logger.warning(f"User {phone} is currently banned. Ignoring message.")
            raise UserBannedError()

    def __invalidate_cache_if_user_has_been_modified(
        self, 
        phone: str,
    ) -> None:

        if self.redis_service.has_update_to_user_profile(phone=phone):
            self.message_history_manager.clear_message_history_for_user(phone=phone)
            self.user_manager.invalidate_user_cache(phone=phone)
            self.redis_service.delete_update_user_profile(phone=phone)
    
    def __respond_to_command(
        self, 
        phone: str, 
        message_text: str,
    ) -> None:

        logger.info(f"Message from {phone} is a command. Responsing to command")
        response_text = self.command_handler.handle_command(
            phone=phone, 
            user_message=message_text,
        )
        self.whatsapp_service.send_text(
            phone=phone, 
            message=response_text,
        )
    
    def __respond_user_with_tutor_message(
        self, 
        phone: str, 
        message_text: str,
    ) -> None:

        logger.info(f"Message from {phone} is study message")
        
        if self.redis_service.has_lock_global_ia():
            logger.warning(f"Global IA lock is active. Skipping message for {phone} to try again later.")
            raise GlobalIALockError()
    
        user = self.user_manager.get_user_profile(phone=phone)
        if not user:
            logger.error(f"User not found or whatsapp not enabled, adding to blacklist:{phone}")
            self.__ban_user(phone=phone)
            return

        instruction = self.instruction_builder.build(user=user)
        if not instruction:
            logger.error(f"Instruction not found, adding to blacklist: {phone}")
            self.__ban_user(phone=phone)
            return
        
        history = self.message_history_manager.get_message_history(
            user_id=user.id,
            phone=phone,
        )
        message_tutor = self.ai_tutor_service.get_tutor_response(
            instruction=instruction,
            history=history,
            message=message_text,
        )
        self.message_history_manager.save_messages(
            user_id=user.id,
            phone=phone,
            user_message=message_text,
            tutor_message=message_tutor,
        )
        self.whatsapp_service.send_text(
            phone=phone, 
            message=message_tutor,
        )
    
    def __finalize_message_processing(
        self, 
        phone: str,
        is_command_message: bool,
    ) -> None:
        
        self.redis_service.delete_processing_phone(phone=phone)
        if not is_command_message:
            self.redis_service.set_lock_global_ia()
    
    def __ban_user(
        self, 
        phone: str,
        message: str = "Para utilização desse serviço, é necessário habilitar nosso plano de estudo de idiomas.",
    ) -> None:

        logger.warning(f"Banning phone {phone}.")
        
        self.redis_service.ban_phone(phone=phone)
        if self.config.notify_user_when_banned:
            logger.info(f"Notifying phone: {phone} that it has been banned")
            self.whatsapp_service.send_text(
                phone=phone, 
                message=message,
            )
