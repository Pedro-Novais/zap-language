from loguru import logger

from core.manager.message_history_manager import MessageHistoryManager
from core.manager.user_manager import UserManager
from core.manager.builder import CommandResponseBuilder
from core.model.enum import (
    CommandTypeGet, 
    CommandTypeSet,
)
from core.shared.errors import CommandDoesNotExistError


class CommandHandler:
    
    def __init__(
        self,
        user_manager: UserManager,
        message_history_manager: MessageHistoryManager,
    ) -> None:
        
        self.command_to_get = "/"
        self.commando_to_set = "!"

        self.user_manager = user_manager
        self.message_history_manager = message_history_manager
    
    def handle_command(
        self, 
        phone: str,  
        user_message: str,
    ) -> str:
        
        try:
            logger.info(f"Verifying command message for {phone}")
            
            if user_message.startswith(self.commando_to_set):
                command = user_message[len(self.commando_to_set):].strip().lower()
                return self._handle_set_command(
                    phone=phone,
                    command=command,
                )
            
            if user_message.startswith(self.command_to_get):
                command = user_message[len(self.command_to_get):].strip().lower()
                return self._handle_get_command(
                    phone=phone, 
                    command=command,
                )
            
        except CommandDoesNotExistError as ex:
            logger.error(f"Error processing command for {phone}: {ex}")
            return CommandResponseBuilder.response_for_error_command()
        
        except Exception as ex:
            logger.error(f"Unexpected error processing command for {phone}: {ex}", exc_info=True)
            raise ex
    
    def is_command(
        self, 
        user_message: str,
    ) -> bool:
        
        return user_message.startswith(self.commando_to_set) or user_message.startswith(self.command_to_get)
    
    def _handle_set_command(
        self, 
        phone: str,
        command: str,
    ) -> str:
        
        if command == CommandTypeSet.RESET.value:
            logger.info(f"Comando de reset identificado para {phone}")
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
        
        if command == CommandTypeGet.TUTOR.value:
            return 
        
        if command == CommandTypeGet.TRANSLATE.value:
            return 
        
        raise CommandDoesNotExistError()
        
    def _handle_reset_command(
        self, 
        phone: str,
    ) -> None:
        
        self.user_manager.invalidate_user_cache(phone=phone)
        self.message_history_manager.clear_history_for_user(phone=phone)
    
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
        