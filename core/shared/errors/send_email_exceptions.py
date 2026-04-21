from .application_exceptions import ApplicationError


class SendEmailError(ApplicationError):
    """Base exception for email sending errors."""

    def __init__(
        self,
        message_error: str = "Failed to send email",
        status_code: int = 500,
        extra: dict = None,
    ) -> None:
        super().__init__(
            status_code=status_code,
            message_error=message_error,
            extra=extra or {},
        )


class SMTPConnectionError(SendEmailError):
    """Exception raised when unable to connect to SMTP server."""

    def __init__(
        self,
        smtp_server: str,
        smtp_port: int,
        extra: dict = None,
    ) -> None:
        super().__init__(
            message_error=f"Failed to connect to SMTP server {smtp_server}:{smtp_port}",
            status_code=500,
            extra=extra or {},
        )


class SMTPAuthenticationError(SendEmailError):
    """Exception raised when SMTP authentication fails."""

    def __init__(
        self,
        smtp_user: str,
        extra: dict = None,
    ) -> None:
        super().__init__(
            message_error=f"SMTP authentication failed for user {smtp_user}",
            status_code=500,
            extra=extra or {},
        )


class InvalidEmailAddressError(SendEmailError):
    """Exception raised when the email address is invalid."""

    def __init__(
        self,
        email: str,
        extra: dict = None,
    ) -> None:
        super().__init__(
            message_error=f"Invalid email address: {email}",
            status_code=400,
            extra=extra or {},
        )


class EmailSendingTimeoutError(SendEmailError):
    """Exception raised when email sending times out."""

    def __init__(
        self,
        timeout: int,
        extra: dict = None,
    ) -> None:
        super().__init__(
            message_error=f"Email sending timed out after {timeout} seconds",
            status_code=500,
            extra=extra or {},
        )