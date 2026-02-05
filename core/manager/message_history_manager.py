import redis
from typing import List, Dict

from loguru import logger

from core.interface.repository import MessageHistoryRepository
from core.model import MessageHistoryModel
from core.model.enum import MessageRoleModel
from core.manager.key import RedisKeyManager


class MessageHistoryManager:
   

    def __init__(
        self, 
        redis_client: redis.Redis, 
        history_repository: MessageHistoryRepository, 
        limit: int = 10,
    ) -> None:
        
        self.LIMIT = limit
        self.TTL = 1800
        
        self.redis = redis_client
        self.history_repository = history_repository

    def get_message_history(
        self, 
        user_id: str,
        phone: str,
    ) -> List[MessageHistoryModel]:
        
        logger.info(f"📚 Buscando histórico para {phone}")
        
        key = self._get_key_history(phone=phone)
        
        history_data = self.redis.lrange(
            name=key, 
            start=0, 
            end=self.LIMIT-1,
        )
        if history_data:
            logger.info(f"📚 Cache Hit para {phone}")
            return self._build_message_history_model_from_cache(history_cache=history_data)
        
        logger.info(f"📚 Cache Miss para {phone}. Buscando no banco...")
        db_history = self.history_repository.get_messages(
            user_id=user_id, 
            limit=self.LIMIT,
        )
        if db_history:
            logger.info(f"📚 Banco Hit para {phone}")
            self._add_to_cache(
                phone=phone, 
                message_history_models=db_history,
            )
        
        return db_history

    def save_messages(
        self, 
        user_id: str,
        phone: str, 
        user_message: str,
        tutor_message: str,
    ) -> None:
        
        logger.info(f"💾 Salvando histórico para {user_id}")
        messages = self._build_new_message_histories(
            user_id=user_id,
            message_text=user_message,
            message_tutor=tutor_message,
        )
        message_update = self.history_repository.insert_messages(
            user_id=user_id, 
            messages=messages,
        )
        self._add_to_cache(
            phone=phone, 
            message_history_models=message_update,
        )
    
    def remove_user_message_from_cache(
        self, 
        phone: str,
    ) -> None:
        
        key = self._get_key_history(phone=phone)
        self.redis.delete(key)
        
    def clear_history_for_user(
        self, 
        phone: str,
    ) -> None:
        
        self.history_repository.invalidate_messages(phone=phone)

    def _add_to_cache(
        self, 
        phone: str, 
        message_history_models: List[MessageHistoryModel],
    ) -> None:
        
        key = self._get_key_history(phone=phone)
        logger.info(f"Adicionando historico de mensagens no cache para telefone {phone}")
        
        for message in message_history_models:
            self.redis.lpush(key, message.model_dump_json())
            self.redis.ltrim(key, 0, self.LIMIT - 1)
            self.redis.expire(key, self.TTL)
            
    @staticmethod  
    def _get_key_history(
        phone: str,
    ) -> str:
        
        return RedisKeyManager.user_history(phone=phone)
    
    @staticmethod
    def _build_message_history_model_from_cache(
        history_cache: List[Dict[str, str]],
    ) -> List[MessageHistoryModel]:
        
        response = []
        for message in history_cache:     
            message_history_model = MessageHistoryModel.model_validate_json(message)
            response.append(message_history_model)
            
        return response
    
    @staticmethod
    def _build_new_message_histories(
        user_id: str,
        message_text: str,
        message_tutor: str,
    ) -> List[MessageHistoryModel]:
        
        history = []
        history.append(MessageHistoryModel(
            user_id=user_id,
            role=MessageRoleModel.USER,
            content=message_text,
        ))
        history.append(MessageHistoryModel(
            user_id=user_id,
            role=MessageRoleModel.ASSISTANT,
            content=message_tutor,
        ))
        return history
