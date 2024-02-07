import logging
import smtplib
from email.mime.text import MIMEText

from starlette import status
from fastapi import HTTPException

from yimba_api.config.email import settings as email_env

logger = logging.getLogger(__name__)


async def send_email(receiver_email: str, subject: str, body):
    sender_email = email_env.sender_email_address
    password = email_env.email_password
    smtp_server = email_env.smtp_server
    smtp_port = email_env.smtp_port

    message = MIMEText(body, "html")
    message["Subject"] = subject
    message["From"] = "ireele <no-reply@ireele.com>"
    message["To"] = receiver_email

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        logger.debug("Email sent successfully.")
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc
