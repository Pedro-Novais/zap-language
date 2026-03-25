from typing import Optional
from uuid import UUID

from sqlalchemy import select, desc, update

from external.database.connection import get_db_session
from external.database.models import (
    User,
    ConversationSession,
)

from core.interface.repository import ConversationSessionRepository
from core.model import (
    ConversationSessionModel,
    ScenarioModel,
)
from core.model.enum import (
    ConversationSessionsType,
    ConversationSessionsState,
)


class ConversationSessionRepositoryImpl(ConversationSessionRepository):
    
    def create_new_session(
        self,
        phone: str,
    ) -> ConversationSessionModel:
        
        with get_db_session() as session:
            user_stmt = select(User.id).where(User.phone == phone)
            user_id = session.execute(user_stmt).scalar_one()

            new_session_db = ConversationSession(
                user_id=user_id,
                is_active=True
            )

            session.add(new_session_db)
            session.commit()
            session.refresh(new_session_db)

            return ConversationSessionModel.model_validate(new_session_db)

    def get_last_session_by_phone(
        self, 
        phone: str,
    ) -> Optional[ConversationSessionModel]:
        
        with get_db_session() as session:
            stmt = (
                select(ConversationSession)
                .join(User)
                .where(User.phone == phone)
                .where(ConversationSession.is_active == True)
                .order_by(desc(ConversationSession.created_at))
                .limit(1)
            )
            
            result = session.execute(stmt).scalar_one_or_none()
            
            if not result:
                return None
                
            return ConversationSessionModel.model_validate(result)
    
    def set_session_as_expired(
        self, 
        session_id: UUID,
    ) -> None:
        
        with get_db_session() as session:
            stmt = (
                update(ConversationSession)
                .where(ConversationSession.id == session_id)
                .values(
                    status=ConversationSessionsState.EXPIRED,
                    is_active=False
                )
            )
            
            session.execute(stmt)
            session.commit()
            
    def set_session_state(
        self, 
        session_id: str,
        state: ConversationSessionsState,
    ) -> ConversationSessionModel:
        
        with get_db_session() as session:
            is_active = state not in [
                ConversationSessionsState.COMPLETED, 
                ConversationSessionsState.CANCELLED_BY_USER,
                ConversationSessionsState.CANCELLED_BY_SYSTEM,
                ConversationSessionsState.EXPIRED,
                ConversationSessionsState.ERROR
            ]
            stmt = (
                update(ConversationSession)
                .where(ConversationSession.id == session_id)
                .values(
                    status=state,
                    is_active=is_active,
                )
                .returning(ConversationSession)
            )
            result = session.execute(stmt).scalar_one()
            session.commit()
            
            return ConversationSessionModel.model_validate(result)
        
    def update_session(
        self, 
        session_id: UUID,
        scenario: Optional[ScenarioModel] = None,
        status: Optional[ConversationSessionsState] = None,
        session_type: Optional[ConversationSessionsType] = None,
        context_summary: Optional[str] = None,
        context_description: Optional[str] = None,
    ) -> ConversationSessionModel:
        
        update_values = {}
        
        if status is not None:
            update_values["status"] = status
            update_values["is_active"] = status not in [
                ConversationSessionsState.COMPLETED, 
                ConversationSessionsState.CANCELLED_BY_USER,
                ConversationSessionsState.CANCELLED_BY_SYSTEM,
                ConversationSessionsState.EXPIRED,
                ConversationSessionsState.ERROR
            ]
        
        if scenario is not None:
            update_values["scenario_id"] = scenario.id

        if session_type is not None:
            update_values["session_type"] = session_type
            
        if context_summary is not None:
            update_values["context_summary"] = context_summary
            
        if context_description is not None:
            update_values["context_description"] = context_description

        with get_db_session() as session:
            if not update_values:
                stmt = select(ConversationSession).where(ConversationSession.id == session_id)
                result = session.execute(stmt).scalar_one()
                return ConversationSessionModel.model_validate(result)

            stmt = (
                update(ConversationSession)
                .where(ConversationSession.id == session_id)
                .values(**update_values)
                .returning(ConversationSession)
            )
            result = session.execute(stmt).scalar_one()
            session.commit()
            
            return ConversationSessionModel.model_validate(result)
