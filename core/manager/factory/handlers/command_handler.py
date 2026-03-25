from loguru import logger

from core.manager.factory.handlers import ConversationHandler
from core.manager.factory.handlers.conversation_handler import CommandHandlerMixin
from core.manager.services import UserService, MessageHistoryService
from core.manager.builder import CommandResponseBuilder
from core.manager.services.conversation_session_service import ConversationSessionService
from core.model.enum import (
    CommandType, 
    CommandTypeSet,
    ConversationSessionsState,
)
from core.model import ConversationSessionModel
from core.model.user_model import UserModel
from core.shared.errors import CommandDoesNotExistError


class CommandHandler(
    ConversationHandler, 
    CommandHandlerMixin,
):
    
    def __init__(
        self,
        user_service: UserService,
        message_history_service: MessageHistoryService,
        session_service: ConversationSessionService,
    ) -> None:
        
        self.start_command = "/"
        self.commando_to_set = "!"

        self.user_service = user_service
        self.session_service = session_service
        self.message_history_service = message_history_service

    def reply_message(
        self, 
        user: UserModel,
        phone: str, 
        message: str,
        session: ConversationSessionModel,
    ) -> str:
        
        try:
            logger.info(f"Verifying command message for {phone}")
            
            if message.startswith(self.commando_to_set):
                command = message[len(self.commando_to_set):].strip().lower()
                return self._handle_set_command(
                    phone=phone,
                    command=command,
                )
            
            if message.startswith(self.start_command):
                command = message[len(self.start_command):].strip().lower()
                return self.__handle_command(
                    phone=phone, 
                    session=session,
                    command=command,
                )
            
        except CommandDoesNotExistError as ex:
            logger.error(f"Command {command} does not exist for")
            return CommandResponseBuilder.response_for_error_command()
        
        except Exception as ex:
            logger.error(f"Unexpected error processing command for {phone}", exc_info=True)
            raise ex
    
    def is_command(
        self, 
        message: str,
    ) -> bool:
        
        return message.startswith(self.commando_to_set) or message.startswith(self.start_command)
    
    def _handle_set_command(
        self, 
        phone: str,
        command: str,
    ) -> str:
        
        if command == CommandTypeSet.RESET.value:
            logger.info(f"[RESET] command received for {phone}")
            self.__handle_reset_command(phone=phone)
            return CommandResponseBuilder.response_for_reset_command()
        
        raise CommandDoesNotExistError()
    
    def __handle_command(
        self, 
        phone: str,
        command: str,
        session: ConversationSessionModel,
    ) -> None:
        
        if command == CommandType.HELP.value:
            return self.__handle_help_command()
        
        if command == CommandType.END_SESSION.value:
            return self.__handle_end_session_command(
                phone=phone,
                session=session,
            )
        
        raise CommandDoesNotExistError()
        
    def __handle_reset_command(
        self, 
        phone: str,
    ) -> None:
        
        self.user_service.invalidate_user_cache(phone=phone)
        self.message_history_service.clear_message_history_for_user(phone=phone)
    
    def __handle_end_session_command(
        self, 
        phone: str,
        session: ConversationSessionModel,
    ) -> str:
        
        logger.info(f"[END SESSION] command received for {phone}")
        self.session_service.set_session_state(
            phone=phone,
            session_id=session.id,
            state=ConversationSessionsState.CANCELLED_BY_USER,
        )
        return CommandResponseBuilder.response_for_end_session_command()
    
    @staticmethod
    def __handle_help_command(
    ) -> str:
        
        return CommandResponseBuilder.response_for_help_command()
    
    def _handle_translate_command(
        self, 
    ) -> None:
        
        pass
        
    def _handle_tutor_command(
        self, 
    ) -> None:
        
        pass
        