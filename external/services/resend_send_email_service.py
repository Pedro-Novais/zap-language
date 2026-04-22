import os
import re
from typing import List

from loguru import logger
import resend

from core.interface.service import SendEmailService
from core.shared.errors import (
    SendEmailError,
    SMTPConnectionError,
    SMTPAuthenticationError,
    InvalidEmailAddressError,
    EmailSendingTimeoutError,
)


class ResendSendEmailService(SendEmailService):

    def __init__(self) -> None:

        self.api_key = os.getenv("RESEND_API_KEY")
        self.from_email = os.getenv("RESEND_FROM_EMAIL")
        if not self.api_key or not self.from_email:
            raise ValueError("RESEND_API_KEY and RESEND_FROM_EMAIL environment variables must be set")

    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
    ) -> None:
        
        if not self._is_valid_email(email=to):
            raise InvalidEmailAddressError(email=to)

        try:
            logger.info(f"Sending email via Resend to {to} with subject: {subject}")
            resend.api_key = self.api_key
            params: resend.Emails.SendParams = {
                "from": self.from_email,
                "to": [to],
                "subject": subject,
                "html": "<strong>it works!</strong>",
            }

            response = resend.Emails.send(params)
            logger.debug(f"Resend response: {response}")
            logger.info("Email sent successfully via Resend")

        except Exception as e:
            err_str = str(e)
            logger.error(f"Failed to send email via Resend: {err_str}")
            raise SendEmailError(message_error="Failed to send email via Resend", extra={"original_error": err_str})

    def _is_valid_email(self, email: str) -> bool:
        email_regex = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
        return re.match(email_regex, email) is not None
