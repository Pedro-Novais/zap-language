from typing import List, Dict

from loguru import logger

from core.shared.model import HistoryManagerConfig
from core.interface.repository import MessageHistoryRepository
from core.interface.service import RedisService
from core.model import MessageHistoryModel
from core.model.enum import MessageRoleModel


class MessageHistoryService:
   
    def __init__(
        self, 
        config: HistoryManagerConfig,
        redis_service: RedisService,
        history_repository: MessageHistoryRepository, 
    ) -> None:
        
        self.config = config
        
        self.redis_service = redis_service
        self.history_repository = history_repository

    def get_message_history(
        self, 
        user_id: str,
        phone: str,
    ) -> List[MessageHistoryModel]:
        
        logger.info(f"Getting message history for {phone}")
        
        message_history_cached = self.redis_service.get_message_history(phone=phone)
        if message_history_cached:
            logger.info(f"Message history cache hit to {phone}")
            return self._build_message_history_model_from_cache(message_history=message_history_cached)
        
        logger.info(f"Cache miss to {phone}. Getting message histories from database")
        message_history_db = self.history_repository.get_messages(
            user_id=user_id, 
            limit=self.config.limit_message_from_history,
        )
        if message_history_db:
            logger.info(f"Message history from database found to {phone}. Adding to cache")
            self._add_to_cache(
                phone=phone, 
                message_history_models=message_history_db,
            )
        
        return message_history_db

    def save_messages(
        self, 
        user_id: str,
        phone: str, 
        user_message: str,
        tutor_message: str,
    ) -> None:
        
        logger.info(f"Saving new messages for {phone}")
        
        message_models = self._build_new_message_histories(
            user_id=user_id,
            message_text=user_message,
            message_tutor=tutor_message,
        )
        message_update = self.history_repository.insert_messages(
            user_id=user_id, 
            messages=message_models,
        )
        self._add_to_cache(
            phone=phone, 
            message_history_models=message_update,
        )
        
    def clear_message_history_for_user(
        self, 
        phone: str,
    ) -> None:
        
        logger.info(f"Clearing message history for {phone}")
        
        self.redis_service.delete_message_history(phone=phone)
        self.history_repository.invalidate_messages(phone=phone)

    def _add_to_cache(
        self, 
        phone: str, 
        message_history_models: List[MessageHistoryModel],
    ) -> None:
        
        logger.info(f"Adding message history to cache for {phone}")
        
        for message in message_history_models:
            self.redis_service.set_message_history(
                phone=phone,
                message=message.model_dump_json(),
            )
    
    @staticmethod
    def _build_message_history_model_from_cache(
        message_history: List[Dict[str, str]],
    ) -> List[MessageHistoryModel]:
        
        response = []
        for message in message_history:     
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
