import os
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from loguru import logger

from core.interface.service import SendEmailService
from core.shared.errors import (
    SendEmailError,
    SMTPConnectionError,
    SMTPAuthenticationError,
    InvalidEmailAddressError,
    EmailSendingTimeoutError,
)


class SMTPSendEmailService(SendEmailService):

    def __init__(self) -> None:
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_password = os.getenv("SMTP_PASSWORD")

        if not self.smtp_user or not self.smtp_password:
            raise ValueError("SMTP_USER and SMTP_PASSWORD environment variables must be set")

    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
    ) -> None:

        if not self._is_valid_email(to):
            raise InvalidEmailAddressError(email=to)

        try:
            logger.info(f"Sending email to {to} with subject: {subject}")

            msg = MIMEMultipart()
            msg['From'] = self.smtp_user
            msg['To'] = to
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30)
            server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            text = msg.as_string()
            server.sendmail(self.smtp_user, to, text)
            server.quit()

            logger.info("Email sent successfully")

        except smtplib.SMTPConnectError as e:
            logger.error(f"SMTP connection error: {e}")
            raise SMTPConnectionError(
                smtp_server=self.smtp_server,
                smtp_port=self.smtp_port,
                extra={"original_error": str(e)}
            )
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP authentication error: {e}")
            raise SMTPAuthenticationError(
                smtp_user=self.smtp_user,
                extra={"original_error": str(e)}
            )
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error: {e}")
            raise SendEmailError(
                message_error=f"SMTP error occurred: {str(e)}",
                extra={"original_error": str(e)}
            )
        except TimeoutError as e:
            logger.error(f"Email sending timeout: {e}")
            raise EmailSendingTimeoutError(
                timeout=30,
                extra={"original_error": str(e)}
            )
        except Exception as e:
            logger.error(f"Unexpected error sending email: {e}")
            raise SendEmailError(
                message_error="Unexpected error occurred while sending email",
                extra={"original_error": str(e)}
            )

    def _is_valid_email(self, email: str) -> bool:
        """Simple email validation using regex."""
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_regex, email) is not None