from typing import Optional


class WorkerError(Exception):
    def __init__(
        self, 
        message: Optional[str] = None,
    ) -> None:

        self.message = message


class RetryWhitoutCountAttempt(WorkerError):

    def __init__(
        self,
    ) -> None:
            
        super().__init__(message="Phone number must be processed again")
        

class RetryCountAttempt(WorkerError):

    def __init__(
        self,
    ) -> None:
            
        super().__init__(message="Error processing phone number, try again later")
        

class ConversationManagerError(Exception):
    def __init__(
        self, 
        message: Optional[str] = None,
    ) -> None:

        self.message = message


class SessionActiveError(ConversationManagerError):

    def __init__(
        self,
    ) -> None:
            
        super().__init__(message="User already has a session active")
        

class SessionStateInvalidError(ConversationManagerError):

    def __init__(
        self,
    ) -> None:
            
        super().__init__(message="User session state is invalid")
        

class AiWithQuotaLimitReachedError(ConversationManagerError):

    def __init__(
        self,
    ) -> None:
            
        super().__init__(message="Ai with quota limit reached")
        
        
class CommandDoesNotExistError(ConversationManagerError):

    def __init__(
        self,
    ) -> None:
            
        super().__init__(message="Command does not exist")
        

class GlobalIALockError(ConversationManagerError):

    def __init__(
        self,
    ) -> None:
            
        super().__init__(message="Ai with global lock enable")


class UserBannedError(ConversationManagerError):

    def __init__(
        self,
    ) -> None:
            
        super().__init__(message="User baneed error")
    