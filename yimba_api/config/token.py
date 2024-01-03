from pydantic import Field

from yimba_api.config import YimbaBaseSettings


class JwtTokenSettings(YimbaBaseSettings):
    secret: str = Field(..., env="JWT_SECRET")
    algorithm: str = Field(..., env="JWT_ALGORITHM")
    access_token_expire: int = Field(..., env="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire: int = Field(..., env="REFRESH_TOKEN_EXPIRE_MINUTES")


settings = JwtTokenSettings()
