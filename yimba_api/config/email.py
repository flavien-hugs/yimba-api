from pydantic import Field

from yimba_api.config import YimbaBaseSettings


class EmailSettings(YimbaBaseSettings):
    smtp_port: int = Field(..., env="SMTP_PORT")
    smtp_server: str = Field(..., env="SMTP_SERVER")
    sender_email_address: str = Field(..., env="EMAIL_ADDRESS")
    email_password: str = Field(..., env="EMAIL_PASSWORD")


settings = EmailSettings()
