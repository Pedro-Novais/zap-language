import json
from time import time
from typing import Dict, List, Union

import redis
from loguru import logger

from core.manager.message_history_manager import MessageHistoryManager
from core.manager.user_manager import UserManager
from core.manager.builder import InstructionBuilder
from core.manager.key import RedisKeyManager
from core.interface.service import (
    AITutorService,
    WhatsappService,
)
from core.model.message_history_model import MessageHistoryModel
from core.shared.errors import (
    ErrorSendingMessageToWhatsapp,
    AiWithQuotaLimitReachedError,
)


class ConversationManager:

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

    def process_message(
        self, 
        phone: str, 
    ) -> bool:

        if not self._is_allowed(phone=phone) or not self._is_ai_healthy():
            return False

        self._invalidate_cache_if_user_has_been_modified(phone=phone)
        return True

    def add_message_to_queue(
        self, 
        phone: str, 
        message_text: str,
    ) -> None:

        payload = self.create_payload_to_queue(
            phone=phone, 
            message_text=message_text,
        )
        try:
            self.redis.lpush(RedisKeyManager.queue_whatasapp_messages(), json.dumps(payload))
            logger.info(f"📥 Mensagem de {phone} adicionada para a fila de processamento.")
        except Exception as e:
            logger.error(f"❌ Erro ao enfileirar mensagem para {phone}: {e}")

    def create_payload_to_queue(
        self,
        phone: str,
        message_text: str,
        attempt: int = 0,
    ) -> Dict[str, Union[str, int]]:

        return {
            "phone": phone,
            "message": message_text,
            "attempt": attempt,
            "timestamp": str(time())
        }

    def process_request(
        self, 
        phone: str, 
        message_text: str,
    ) -> None:

        key_processing = self._get_key_processing(phone=phone)
        key_ban = self._get_key_ban(phone=phone)
        try:
            self.redis.setex(
                name=key_processing, 
                time=30, 
                value="1",
            )
            user = self.user_manager.get_study_settings_by_phone(phone=phone)
            if not user or not user.whatsapp_enabled:
                logger.error(f"User not registered, adding to blacklist: {phone}")
                self.redis.setex(key_ban, self.BAN_TIME_SECONDS, "1")
                self.whatsapp_service.send_text(
                    phone=phone, 
                    message="Para utilização desse serviço, é necessário habilitar nosso plano de estudo de idiomas."
                )
                return

            instruction = self.instruction_builder.build(user=user)
            if not instruction:
                logger.error(f"Instruction not found, adding to blacklist: {phone}")
                self.redis.setex(key_ban, self.BAN_TIME_SECONDS, "1")
                self.whatsapp_service.send_text(
                    phone=phone, 
                    message="Para utilização desse serviço, é necessário habilitar nosso plano de estudo de idiomas."
                )
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

        except AiWithQuotaLimitReachedError as e:
            logger.error(f"AI quota limit reached for {phone}: {e}")
            raise e

        except ErrorSendingMessageToWhatsapp as e:
            logger.error("Error sending message to Whatsapp", exc_info=True)
            raise e

        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            raise e

        finally:
            self.redis.delete(key_processing)

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
        self.redis.setex(RedisKeyManager.ai_health_status(), 10, "1")
        return tutor_response

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
            self.redis.expire(key_rate_limit, 20)

        if current_count > self.MAX_MESSAGES_WINDOW:
            logger.error(f"🚨 [Ban] Usuário {phone} excedeu limite e foi para blacklist.")
            self.redis.setex(key_ban, self.BAN_TIME_SECONDS, "true")
            self.whatsapp_service.send_text(
                phone=phone, 
                message="⚠️ Você enviou mensagens muito rápido. Seu acesso foi suspenso por 30 minutos."
            )
            return False

        return True

    def _is_ai_healthy(self) -> bool:

        for attempt in range(3):
            if not self.redis.exists(RedisKeyManager.ai_health_status()):
                return True

            logger.warning(f"🤖 [AI] Tentativa {attempt + 1}: AI está ocupada. Verificando novamente em 5 segundos...")
            time.sleep(10)

        logger.error("🤖 [AI] AI continua ocupada após 3 tentativas. Retornando erro para o usuário.")
        return False

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
