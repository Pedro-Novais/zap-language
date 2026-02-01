import redis

from loguru import logger


from core.manager.message_history_manager import MessageHistoryManager
from core.manager.user_manager import UserManager
from core.manager.builder import InstructionBuilder
from core.interface.service import (
    AITutorService,
    WhatsappService,
)
from core.shared.errors import ErrorSendingMessageToWhatsapp


class ConversationManager:
    
    KEY_PROCESSING = "processing:{phone}"
    KEY_BAN = "blacklist:{phone}"
    KEY_RATE_LIMIT = "rate_limit:{phone}"

    def __init__(
        self,
        ai_tutor_service: AITutorService, 
        whatsapp_service: WhatsappService,
        user_manager: UserManager,
        message_history_manager: MessageHistoryManager,
        redis_client: redis.Redis,
    ) -> None:
        
        self.redis = redis_client
        
        self.user_manager = user_manager
        self.message_history_manager = message_history_manager
        
        self.ai_tutor_service = ai_tutor_service
        self.whatsapp_service = whatsapp_service
        
        self.instruction_builder = InstructionBuilder()
        
        self.MAX_MESSAGES_WINDOW = 3
        self.BAN_TIME_SECONDS = 1800
    
    def process_and_respond(
        self, 
        phone: str, 
        message_text: str,
    ) -> None:
        
        if not self._is_allowed(phone=phone):
            return

        key_processing = self._get_key_processing(phone=phone)
        key_ban = self._get_key_ban(phone=phone)
        
        self.redis.setex(key_processing, 30, "true")

        try:
            user = self.user_manager.get_study_settings_by_phone(phone=phone)
            if not user or not user.whatsapp_enabled:
                logger.error(f"User not registered, adding to blacklist: {phone}")
                self.redis.setex(key_ban, self.BAN_TIME_SECONDS * 10, "true")
                return

            instruction = self.instruction_builder.build(user=user)
            if not instruction:
                logger.error(f"Instruction not found, adding to blacklist: {phone}")
                self.redis.setex(key_ban, self.BAN_TIME_SECONDS, "true")
                return
            
            history = self.message_history_manager.get_message_history(user_id=user.id)
            message_tutor = self.ai_tutor_service.get_tutor_response(
                instruction=instruction,
                history=history,
                message=message_text,
            )
            self.message_history_manager.save_messages(
                user_id=user.id,
                user_message=message_text,
                tutor_message=message_tutor,
            )
            self.whatsapp_service.send_text(
                phone=phone, 
                message=message_tutor,
            )

        except ErrorSendingMessageToWhatsapp as e:
            logger.error("Error sending message to Whatsapp", exc_info=True)
            return

        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            return
        
        finally:
            self.redis.delete(key_processing)
            
    def _is_allowed(
        self, 
        phone: str,
    ) -> bool:
        
        key_processing = self._get_key_processing(phone=phone)
        key_ban = self._get_key_ban(phone=phone)
        key_rate_limit = self._get_key_rate_limit(phone=phone)
        
        if self.redis.exists(key_ban):
            logger.warning(f"🚫 [Spam] Usuário {phone} ignorado (Blacklist).")
            return False

        if self.redis.exists(key_processing):
            logger.info(f"⏳ [Wait] Usuário {phone} já possui tarefa em andamento.")
            return False

        current_count = self.redis.incr(key_rate_limit)
        if current_count == 1:
            self.redis.expire(key_rate_limit, 60)

        if current_count > self.MAX_MESSAGES_WINDOW:
            logger.error(f"🚨 [Ban] Usuário {phone} excedeu limite e foi para blacklist.")
            self.redis.setex(key_ban, self.BAN_TIME_SECONDS, "true")
            self.whatsapp_service.send_text(
                phone=phone, 
                message="⚠️ Você enviou mensagens muito rápido. Seu acesso foi suspenso por 30 minutos."
            )
            return False

        return True
    
    def _get_key_processing(
        self, 
        phone: str,
    ) -> str:
        
        return self.KEY_PROCESSING.format(phone=phone)
    
    def _get_key_ban(
        self, 
        phone: str,
    ) -> str:
        
        return self.KEY_BAN.format(phone=phone)
    
    def _get_key_rate_limit(
        self, 
        phone: str,
    ) -> str:
        
        return self.KEY_RATE_LIMIT.format(phone=phone)
    