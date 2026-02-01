from dataclasses import field
import email
from typing import (
    Any,
    Dict,
    Optional,
)


class ApplicationError(Exception):
    def __init__(
        self, 
        status_code: int = 500,
        message_error: str = "An application error occurred", 
        extra: Dict[str, Any] = {},
    ) -> None:

        self.message_error = message_error
        self.status_code = status_code
        self.extra = extra


class EmailAlreadyExistsError(ApplicationError):

    def __init__(
        self, 
        email: str,
    ) -> None:

        super().__init__(
            message_error=f"Email '{email}' já está em uso",
            status_code=409,
            )
        

class MissingRequiredFieldError(ApplicationError):

    def __init__(
        self,
    ) -> None:

        super().__init__(
            message_error=f"Missing required field",
            status_code=400,
            )
        

class UnhandledConfigurationValueError(ApplicationError):

    def __init__(
        self,
    ) -> None:

        super().__init__(
            message_error=f"Foram enviados valores não tratados para a configuração",
            status_code=406,
            )
        

class UserNotFoundError(ApplicationError):

    def __init__(
        self, 
        email: str,
    ) -> None:
            
        super().__init__(
            message_error=f"Email: '{email}' não está cadastrado!",
            status_code=404,
            )


class IncorrectPasswordProvidedError(ApplicationError):

    def __init__(
        self, 
    ) -> None:
            
        super().__init__(
            message_error="Senha fornecida está incorreta",
            status_code=401,
            )
        

class ErrorSendingMessageToWhatsapp(ApplicationError):

    def __init__(
        self,
        error, 
    ) -> None:
            
        super().__init__(
            message_error="Erro enviando mensagem para o Whatsapp",
            status_code=502,
            extra={"original_error": str(error)},
            )


class ExternalServiceError(ApplicationError):

    def __init__(
        self,
        error, 
    ) -> None:
            
        super().__init__(
            message_error="Erro de comunicação com serviço externo",
            status_code=502,
            extra={"original_error": str(error)},
            )
       

class InvalidPhoneNumberError(ApplicationError):

    def __init__(
        self,
    ) -> None:
            
        super().__init__(
            message_error="Número de telefone inválido",
            status_code=400,
            )
        
class InvalidVerificationCodeError(ApplicationError):

    def __init__(
        self,
    ) -> None:
            
        super().__init__(
            message_error="Código fornecido inválido",
            status_code=400,
            )
        
class MaxAttemptsReachedError(ApplicationError):

    def __init__(
        self,
    ) -> None:
            
        super().__init__(
            message_error="Número máximo de tentativas atingido",
            status_code=400,
            )
        
class UserAlreadyHasPhoneNumberError(ApplicationError):

    def __init__(
        self,
    ) -> None:
            
        super().__init__(
            message_error="Usuário já possui um número de telefone",
            status_code=400,
            )
        
class NoVerificationCodeWasGeneratedError(ApplicationError):

    def __init__(
        self,
    ) -> None:
            
        super().__init__(
            message_error="Nenhum código de verificação foi gerado para o usuário",
            status_code=400,
            )
        
class CodeExpiredError(ApplicationError):

    def __init__(
        self,
    ) -> None:
            
        super().__init__(
            message_error="Código de verificação expirado",
            status_code=400,
            )
        