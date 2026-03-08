from loguru import logger

from core.manager.factory import ConversationHandler
from core.manager.services import UserService, MessageHistoryService
from core.manager.builder import CommandResponseBuilder
from core.model.enum import (
    CommandTypeGet, 
    CommandTypeSet,
)
from core.model import ConversationSessionModel
from core.shared.errors import CommandDoesNotExistError


class CommandHandler(ConversationHandler):
    
    def __init__(
        self,
        user_service: UserService,
        message_history_service: MessageHistoryService,
    ) -> None:
        
        self.command_to_get = "/"
        self.commando_to_set = "!"

        self.user_service = user_service
        self.message_history_service = message_history_service
    
    def process_message(
        self, 
        phone: str, 
        message: str,
        session: ConversationSessionModel,
    ) -> None:
        
        try:
            logger.info(f"Verifying command message for {phone}")
            
            if message.startswith(self.commando_to_set):
                command = message[len(self.commando_to_set):].strip().lower()
                return self._handle_set_command(
                    phone=phone,
                    command=command,
                )
            
            if message.startswith(self.command_to_get):
                command = message[len(self.command_to_get):].strip().lower()
                return self._handle_get_command(
                    phone=phone, 
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
        
        return message.startswith(self.commando_to_set) or message.startswith(self.command_to_get)

    def is_a_scenario_command(
        self, 
        command: str,
    ) -> bool:
        
        return command == CommandTypeSet.SCENARIO.value
    
    def _handle_set_command(
        self, 
        phone: str,
        command: str,
    ) -> str:
        
        if command == CommandTypeSet.RESET.value:
            logger.info(f"[RESET] command received for {phone}")
            self._handle_reset_command(phone=phone)
            return CommandResponseBuilder.response_for_reset_command()
        
        raise CommandDoesNotExistError()
    
    def _handle_get_command(
        self, 
        phone: str,
        command: str,
    ) -> None:
        
        if command == CommandTypeGet.HELP.value:
            return self._handle_help_command()
        
        raise CommandDoesNotExistError()
        
    def _handle_reset_command(
        self, 
        phone: str,
    ) -> None:
        
        self.user_service.invalidate_user_cache(phone=phone)
        self.message_history_service.clear_message_history_for_user(phone=phone)
    
    def _handle_help_command(
        self, 
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
        