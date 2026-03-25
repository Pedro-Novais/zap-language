from typing import Optional

from loguru import logger

from core.interface.service.redis_service import RedisService
from core.manager.instructions import InstructionBuilder
from core.manager.factory.handlers import ConversationHandler
from core.manager.factory.handlers.conversation_handler import StudySessionMixin, CommandHandlerMixin
from core.manager.services.conversation_session_service import ConversationSessionService
from core.manager.services.message_history_service import MessageHistoryService
from core.manager.services.user_service import UserService
from core.model.user_model import UserModel
from core.model import ConversationSessionModel
from core.model.enum import ConversationSessionsState
from external.services.ai_tutor_service import AITutorService



class FreeTalkHandler(
    ConversationHandler, 
    StudySessionMixin, 
    CommandHandlerMixin,
):
    
    def __init__(
        self,
        ai_tutor_service: AITutorService, 
        redis_service: RedisService,
        user_service: UserService,
        message_history_service: MessageHistoryService,
        session_service: ConversationSessionService,
    ) -> None:

        self.user_service = user_service
        self.message_history_service = message_history_service
        
        self.ai_tutor_service = ai_tutor_service
        self.redis_service = redis_service
        self.session_service = session_service

        self.instruction_builder = InstructionBuilder()
    
    def reply_message(
        self, 
        phone: str, 
        message: str,
        session: ConversationSessionModel,
        user: UserModel,
    ) -> str:

        command = None
        if self.is_command(message=message):
            logger.info(f"[Free Talk] Command received for {phone}")
            
            self._verify_session_interrupt(session=session)
            command = self._extract_key_after_command(message=message)
            if not command:
                raise
            
            session = self.session_service.set_start_session_free_talk(
                phone=phone,
                session=session,
                context_summary=command,
            )
            
            logger.info(f"[Free Talk] Session started successfully, topic: {command}")
            
        message_to_tutor = self.__get_message_to_tutor(
            message=message, 
            is_command=command is not None,
        )
        response = self.__handle_free_talk(
            user=user,
            phone=phone,
            message=message_to_tutor,
            session=session,
        )
        return response
    
    def is_command(
        self,
        message: str,
    ) -> bool:
        
        clean_message = message.strip().lower()
        return clean_message.startswith("/free_talk")
    
    def __handle_free_talk(
        self, 
        user: UserModel,
        phone: str,
        message: str,
        session: ConversationSessionModel,
    ) -> str:
        
        logger.info(f"[Free Talk] Handling message for {phone}")

        self._check_ia_lock(
            phone=phone, 
            redis_service=self.redis_service,
        )
        instruction = self.instruction_builder.build_free_talk_instruction(
            user=user,
            session=session,
        )
        history = self.message_history_service.get_message_history(
            user_id=user.id,
            phone=phone,
            session=session,
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
            session=session,
            tutor_message=message_tutor,
        )
        return message_tutor
    
    def __get_message_to_tutor(
        self, 
        message: str,
        is_command: bool = False,
    ) -> Optional[str]:
        
        if is_command: 
            return f"Inicie comentando alguma curiosidade sobre o tópico selecionado, {message}, ou pergunte ao usuário qual assunto do mundo de {message} ele deseja conversar"
        
        return message
