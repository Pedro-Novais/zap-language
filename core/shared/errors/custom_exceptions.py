from typing import (
    Any,
    Dict,
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
        field: str,
    ) -> None:

        super().__init__(
            message_error=f"Missing required field: {field}",
            status_code=400,
            )
        