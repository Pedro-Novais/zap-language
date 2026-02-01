from typing import (
    List, 
    Optional,
)

from external.database.connection import get_db_session
from external.database.models import MessageHistory
from core.interface.repository import MessageHistoryRepository
from core.model import MessageHistoryModel


class MessageHistoryRepositoryImpl(MessageHistoryRepository):

    def get_messages(
        self,
        user_id: str,
        limit: int,
    ) -> List[MessageHistoryModel]:
        
        with get_db_session() as session:
            messages = session.query(MessageHistory).filter(
                MessageHistory.user_id == user_id,
            ).order_by(MessageHistory.created_at.desc()).limit(limit).all()
            
            response = []
            for message in messages:
                response.append(MessageHistoryModel(
                    id=message.id,
                    user_id=message.user_id,
                    role=message.role,
                    content=message.content,
                    created_at=message.created_at,
                ))
            
            return response

    def insert_messages(
        self,
        user_id: str,
        messages: List[MessageHistoryModel],
    ) -> List[MessageHistoryModel]:
        
        message_db_instances: List[MessageHistory]= []
        with get_db_session() as session:
            for message in messages:
                message = MessageHistory(
                    user_id=user_id,
                    role=message.role,
                    content=message.content,
                )
                message_db_instances.append(message)
            
            session.add_all(message_db_instances)
            session.commit()
            
            for db_msg in message_db_instances:
                session.refresh(db_msg)
            
            return [
                self._transform_message_data_in_message_model(db_msg) 
                for db_msg in message_db_instances
            ]
        
    @staticmethod
    def _transform_message_data_in_message_model(
        message: Optional[MessageHistory],
    ) -> Optional[MessageHistoryModel]:
        
        if not message:
            return None
    
        return MessageHistoryModel(   
            id=message.id,
            user_id=message.user_id,
            role=message.role,
            content=message.content,
            created_at=message.created_at,
        )
        