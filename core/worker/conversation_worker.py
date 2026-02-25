import json
import time
from typing import Dict, Union

import redis
from loguru import logger

from core.manager.conversation_manager import ConversationManager
from core.manager.key.redis_key_manager import RedisKeyManager
from core.shared.errors import AiWithQuotaLimitReachedError


class ConversationWorker:
    def __init__(
        self, 
        redis_client: redis.Redis,
        conversation_manager: ConversationManager, 
    ) -> None:
        
        self.manager = conversation_manager
        self.redis = redis_client
        self.MAX_RETRIES = 3
        self.MAX_ERROR = 10 

        self.running = True
        self.attempt_errors = 0
        self.time_to_sleep_on_error = 15

    def run(self):
        logger.info("🚀 Worker de conversação iniciado e aguardando mensagens...")
        while self.running:
            try:
                _, data_json = self.redis.brpop(RedisKeyManager.queue_whatasapp_messages(), timeout=0)
                data = json.loads(data_json)
                self._process_message(data=data)
                
            except Exception as e:
                logger.error(f"💥 Erro crítico no loop do Worker: {e}")
                time.sleep(seconds=self.time_to_sleep_on_error)

    def _process_message(
        self, 
        data: Dict[str, Union[str, int]]
    ) -> None:
        
        phone = data["phone"]
        message = data["message"]
        attempt = int(data["attempt"])
        
        if attempt >= self.MAX_RETRIES:
            logger.error(f"❌ Máximo de tentativas atingido para {phone}. Mensagem descartada.")
            return
        
        try:
            is_valid = self.manager.process_message(phone=phone)
            if not is_valid:
                logger.warning(f"⚠️ Mensagem de {phone} não processada devido a restrições ou saúde da IA.")
                return
            
            self.manager.process_request(phone=phone, message_text=message)
            self.attempt_errors = 0
            
        except Exception as e:
            self._handle_error(
                phone=phone, 
                message=message, 
                error=e,
            )
            
        finally:
            self._update_time_to_sleep_on_error()

    def _handle_error(
        self, 
        phone: str, 
        message: str, 
        error: Exception,
    ) -> None:
        
        logger.error(f"❌ Erro ao processar mensagem de {phone}: {error}")
        payload = self.manager._create_payload_to_queue(
            phone=phone, 
            message_text=message,
        )
        self.redis.lpush(RedisKeyManager.queue_whatasapp_messages(), json.dumps(payload))
        self.attempt_errors += 1
       
    def _update_time_to_sleep_on_error(
        self, 
    ) -> None:
        
        attempt_errors = self.attempt_errors
        if attempt_errors > self.MAX_ERROR:
            attempt_errors = self.MAX_ERROR
        
        if attempt_errors == 0:
            attempt_errors = 1
            
        current_time = self.time_to_sleep_on_error
        self.time_to_sleep_on_error = current_time * attempt_errors
        logger.info(f"⏱️ Tempo de espera em caso de erro atualizado para {self.time_to_sleep_on_error} segundos.")
