from loguru import logger

from core.interface.service.redis_service import RedisService
from core.interface.service.whatsapp_service import WhatsappService
from core.manager.builder.instruction_builder import InstructionBuilder
from core.manager.factory.handlers import ConversationHandler
from core.manager.services.message_history_service import MessageHistoryService
from core.manager.services.user_service import UserService
from core.shared.errors.custom_exceptions import GlobalIALockError
from core.model import ConversationSessionModel
from external.services.ai_tutor_service import AITutorService



class FreeTalkHandler(ConversationHandler):
    
    def __init__(
        self,
        ai_tutor_service: AITutorService, 
        whatsapp_service: WhatsappService,
        redis_service: RedisService,
        user_service: UserService,
        message_history_service: MessageHistoryService,
    ) -> None:

        self.user_service = user_service
        self.message_history_service = message_history_service
        
        self.ai_tutor_service = ai_tutor_service
        self.whatsapp_service = whatsapp_service
        self.redis_service = redis_service

        self.instruction_builder = InstructionBuilder()

    
    def process_message(
        self, 
        phone: str, 
        message: str,
        session: ConversationSessionModel,
    ) -> None:

        logger.info(f"Message from {phone} is study message")
        
        if self.redis_service.has_lock_global_ia():
            logger.warning(f"Global IA lock is active. Skipping message for {phone} to try again later.")
            raise GlobalIALockError()
    
        user = self.user_service.get_user_profile(phone=phone)
        if not user:
            logger.error(f"User not found or whatsapp not enabled, adding to blacklist:{phone}")
            self.__ban_user(phone=phone)
            return

        instruction = self.instruction_builder.build(user=user)
        if not instruction:
            logger.error(f"Instruction not found, adding to blacklist: {phone}")
            self.__ban_user(phone=phone)
            return
        
        history = self.message_history_service.get_message_history(
            user_id=user.id,
            phone=phone,
        )
        message_tutor = self.ai_tutor_service.get_tutor_response(
            instruction=instruction,
            history=history,
            message=message,
        )
        self.message_history_service.save_messages(
            user_id=user.id,
            phone=phone,
            user_message=message,
            tutor_message=message_tutor,
        )
        self.whatsapp_service.send_text(
            phone=phone, 
            message=message_tutor,
        )
