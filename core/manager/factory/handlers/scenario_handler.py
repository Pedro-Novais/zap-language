from typing import Optional

from loguru import logger

from core.interface.service.redis_service import RedisService
from core.manager.instructions import InstructionBuilder
from core.manager.factory.handlers import ConversationHandler
from core.manager.factory.handlers.conversation_handler import StudySessionMixin, CommandHandlerMixin
from core.manager.services import (
    ScenarioService,
    MessageHistoryService,
    ConversationSessionService,
)
from core.model.user_model import UserModel
from core.model import ConversationSessionModel, ScenarioModel
from core.model.enum import ConversationSessionsState
from external.services.ai_tutor_service import AITutorService


class ScenarioHandler(
    ConversationHandler, 
    StudySessionMixin, 
    CommandHandlerMixin,
):
    
    def __init__(
        self,
        ai_tutor_service: AITutorService, 
        redis_service: RedisService,
        message_history_service: MessageHistoryService,
        session_service: ConversationSessionService,
        scenario_service: ScenarioService,
    ) -> None:

        self.message_history_service = message_history_service
        
        self.ai_tutor_service = ai_tutor_service
        self.redis_service = redis_service
        self.session_service = session_service
        self.scenario_service = scenario_service

        self.instruction_builder = InstructionBuilder()
    
    def reply_message(
        self, 
        phone: str, 
        message: str,
        session: ConversationSessionModel,
        user: UserModel,
    ) -> str:

        scenario = None
        if self.is_command(message=message):
            logger.info(f"[Scenario] Command received for {phone}")
            
            self._verify_session_interrupt(session=session)
            scenario_key = self._extract_key_after_command(message=message)
            if not scenario_key:
                # TODO: Reply to user that scenario is missing
                raise Exception("Scenario key not found after command")

            scenario = self.scenario_service.get_by_key(key=scenario_key)
            if not scenario:
                # TODO: Reply to user that scenario does not exist
                raise Exception(f"Scenario with key {scenario_key} not found")
            
            session = self.session_service.set_start_session_scenario(
                phone=phone,
                session=session,
                scenario=scenario,
            )
            logger.info(f"[Scenario] Session started successfully, scenario: {scenario.title}")
            
        message_to_tutor = self.__get_message_to_tutor(
            message=message,
            is_command=scenario is not None,
            scenario=scenario
        )
        response = self.__handle_scenario(
            user=user,
            phone=phone,
            message=message_to_tutor,
            session=session,
            scenario=scenario,
        )
        return response
    
    def is_command(
        self,
        message: str,
    ) -> bool:
        
        clean_message = message.strip().lower()
        return clean_message.startswith("/scenario")
    
    def __handle_scenario(
        self, 
        user: UserModel,
        phone: str,
        message: str,
        session: ConversationSessionModel,
        scenario: ScenarioModel,
    ) -> str:
        
        logger.info(f"[Scenario] Handling message for {phone}")

        self._check_ia_lock(
            phone=phone, 
            redis_service=self.redis_service,
        )
        instruction = self.instruction_builder.build_scenario_instruction(
            user=user,
            session=session,
            scenario=scenario,
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
        scenario: Optional[ScenarioModel] = None,
    ) -> Optional[str]:
        
        if is_command: 
            return f"Inicie o cenário de '{scenario.title}' para o usuário. Apresente o contexto de '{scenario.context}' e o seu personagem '{scenario.teacher_char}' e peça para o usuário iniciar a interação."
        
        return message
