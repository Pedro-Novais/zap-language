from typing import (
    List, 
    Optional,
)

from datetime import (
    datetime, 
    timedelta,
    timezone,
)

from external.database.connection import get_db_session
from external.database.models import (
    User,
    MessageHistory, 
)
from core.interface.repository import MessageHistoryRepository
from core.model import MessageHistoryModel


class MessageHistoryRepositoryImpl(MessageHistoryRepository):

    def get_messages(
        self,
        user_id: str,
        limit: int,
        messages_from_the_last_hours: int = 5,
    ) -> List[MessageHistoryModel]:
        
        time_threshold = datetime.now(tz=timezone.utc) - timedelta(hours=messages_from_the_last_hours)
        with get_db_session() as session:
            messages = session.query(MessageHistory).filter(
                MessageHistory.user_id == user_id,
                MessageHistory.is_allowed == True,
                MessageHistory.created_at >= time_threshold,
            ).order_by(MessageHistory.created_at.asc()).limit(limit).all()
            
            response = []
            for message in messages:
                response.append(self._transform_message_data_in_message_model(message=message))
            
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
            
            return [self._transform_message_data_in_message_model(message=db_msg) for db_msg in message_db_instances]
        
    def invalidate_messages(
        self,
        phone: str,
    ) -> None:
        
        with get_db_session() as session:
            user_id_subquery = (
                session.query(User.id)
                .filter(User.phone == phone)
                .scalar_subquery()
            )
            session.query(MessageHistory).filter(
                MessageHistory.user_id == user_id_subquery,
                MessageHistory.is_allowed == True
            ).update(
                {"is_allowed": False}, 
                synchronize_session=False
            )
            
            session.commit()
            return
    
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
        