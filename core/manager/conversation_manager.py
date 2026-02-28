from typing import List

import redis
from loguru import logger

from core.manager.message_history_manager import MessageHistoryManager
from core.manager.user_manager import UserManager
from core.manager.command import CommandHandler
from core.manager.builder import InstructionBuilder
from core.manager.key import RedisKeyManager
from core.interface.service import (
    AITutorService,
    WhatsappService,
)
from core.model.message_history_model import MessageHistoryModel
from core.shared.errors import ApplicationError


class ConversationManager:

    def __init__(
        self,
        ai_tutor_service: AITutorService, 
        whatsapp_service: WhatsappService,
        user_manager: UserManager,
        message_history_manager: MessageHistoryManager,
        redis_client: redis.Redis,
        command_handler: CommandHandler,
    ) -> None:

        self.redis = redis_client

        self.user_manager = user_manager
        self.message_history_manager = message_history_manager

        self.command_handler = command_handler
        
        self.ai_tutor_service = ai_tutor_service
        self.whatsapp_service = whatsapp_service

        self.instruction_builder = InstructionBuilder()

        self.MAX_MESSAGES_WINDOW = 1
        self.BAN_TIME_SECONDS = 1800

    def process_message(
        self, 
        phone: str, 
    ) -> bool:

        if not self._is_allowed(phone=phone):
            return False

        self._invalidate_cache_if_user_has_been_modified(phone=phone)
        return True

    def reply_user(
        self, 
        phone: str, 
        message_text: str,
    ) -> None:

        try:
            is_message_command = self.command_handler.is_command(user_message=message_text)
            if is_message_command:
                self._respond_to_command(
                    phone=phone,
                    message_text=message_text,
                )
            else:
                self._respond_user_with_tutor_message(
                    phone=phone, 
                    message_text=message_text,
                )

        except ApplicationError as ex:
            logger.error(f"Application error while replying to {phone}: {ex}")
            raise ex

        except Exception as ex:
            logger.error(f"Error FATAL while processing message: {ex}", exc_info=True)
            raise ex

    def _respond_to_command(
        self, 
        phone: str, 
        message_text: str,
    ) -> None:

        response_text = self.command_handler.handle_command(
            phone=phone, 
            user_message=message_text,
        )
        self.whatsapp_service.send_text(
            phone=phone, 
            message=response_text,
        )
    
    def _respond_user_with_tutor_message(
        self, 
        phone: str, 
        message_text: str,
    ) -> None:

        user = self.user_manager.get_study_settings_by_phone(phone=phone)
        if not user or not user.whatsapp_enabled:
            logger.error(f"User not found or whatsapp not enabled, adding to blacklist:{phone}")
            self._ban_user(phone=phone)
            return

        instruction = self.instruction_builder.build(user=user)
        if not instruction:
            logger.error(f"Instruction not found, adding to blacklist: {phone}")
            self._ban_user(phone=phone)
            return
        
        history = self.message_history_manager.get_message_history(
            user_id=user.id,
            phone=phone,
        )
        message_tutor = self._get_tutor_response(
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
    
    def _ban_user(
        self, 
        phone: str,
        message: str = "Para utilização desse serviço, é necessário habilitar nosso plano de estudo de idiomas.",
        notify_user: bool = True,
    ) -> None:

        key_ban = self._get_key_ban(phone=phone)
        self.redis.setex(key_ban, self.BAN_TIME_SECONDS, "1")
        logger.warning(f"Banning user {phone} for {self.BAN_TIME_SECONDS} seconds.")
        if notify_user:
            self.whatsapp_service.send_text(
                phone=phone, 
                message=message,
            )
        
    def _get_tutor_response(
        self,
        instruction: str,
        history: List[MessageHistoryModel],
        message: str,
    ) -> str:

        tutor_response = self.ai_tutor_service.get_tutor_response(
            instruction=instruction,
            history=history,
            message=message,
        )
        return tutor_response

    def _is_allowed(
        self, 
        phone: str,
    ) -> bool:

        key_ban = self._get_key_ban(phone=phone)
        key_rate_limit = self._get_key_rate_limit(phone=phone)
        if self.redis.exists(key_ban):
            logger.warning(f"User {phone} is currently banned. Ignoring message.")
            return False

        current_count = self.redis.incr(key_rate_limit)
        if current_count == 1:
            self.redis.expire(key_rate_limit, 20)

        if current_count > self.MAX_MESSAGES_WINDOW:
            logger.error(f"User {phone} exceeded rate limit with {current_count} messages. We will ignore their messages until us replying them.")
            return False

        return True

    def _invalidate_cache_if_user_has_been_modified(
        self, 
        phone: str,
    ) -> None:

        key_update_user = RedisKeyManager.update_user_profile(phone=phone)
        if self.redis.exists(key_update_user):
            self.message_history_manager.remove_user_message_from_cache(phone=phone)
            self.message_history_manager.clear_history_for_user(phone=phone)
            self.user_manager.invalidate_user_cache(phone=phone)
            self.redis.delete(key_update_user)

    @staticmethod
    def _get_key_processing(
        phone: str,
    ) -> str:
        return RedisKeyManager.processing_phone(phone=phone)

    @staticmethod
    def _get_key_ban(
        phone: str,
    ) -> str:
        return RedisKeyManager.black_list_phone(phone=phone)

    @staticmethod
    def _get_key_rate_limit(
        phone: str,
    ) -> str:
        return RedisKeyManager.rate_limit_phone(phone=phone)
