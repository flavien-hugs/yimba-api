from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, Request
from fastapi.security import HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from starlette import status

from yimba_api.config.token import settings as token_env

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TokenPayload(BaseModel):
    exp: float
    iat: float
    sub: str
    email: str
    role_or_type: str


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_context.verify(plain_password, hashed_password)


def password_hash(password: str) -> str:
    return password_context.hash(password)


def create_token_payload(
    user: str, role_or_type: str, email: str, lifetime: timedelta or None = None
) -> TokenPayload:
    expire = (
        datetime.timestamp(datetime.utcnow() + lifetime)
        if lifetime
        else datetime.timestamp(
            datetime.utcnow() + timedelta(minutes=token_env.access_token_expire)
        )
    )
    return TokenPayload(
        exp=expire,
        iat=datetime.timestamp(datetime.utcnow()),
        sub=user,
        role_or_type=role_or_type,
        email=email,
    )


def create_token(payload: TokenPayload, secret: str, algorithm: str) -> str:
    return jwt.encode(payload.dict(), secret, algorithm=algorithm)


def decode_token(
    token: str,
    secret: str,
    algorithm: str,
    lifetime: Optional[timedelta] = None,
) -> TokenPayload:
    try:
        payload = jwt.decode(
            token,
            secret,
            algorithms=[algorithm],
        )
        token_payload = TokenPayload(**payload)
        if datetime.fromtimestamp(token_payload.exp) < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(err),
            headers={"WWW-Authenticate": "Bearer"},
        ) from err

    return token_payload


def create_access_token(user: str, role_or_type: str, email: str) -> str:
    payload = create_token_payload(
        user, role_or_type, email, timedelta(minutes=token_env.access_token_expire)
    )
    return create_token(payload, token_env.secret, token_env.algorithm)


def decode_access_token(token: str) -> TokenPayload:
    return decode_token(
        token,
        token_env.secret,
        token_env.algorithm,
        timedelta(minutes=token_env.access_token_expire),
    )


def create_refresh_token(user: str, role_or_type: str, email: str) -> str:
    payload = create_token_payload(
        user, role_or_type, email, timedelta(minutes=token_env.refresh_token_expire)
    )
    return create_token(payload, token_env.secret, token_env.algorithm)


def decode_refresh_token(token: str) -> TokenPayload:
    return decode_token(
        token,
        token_env.secret,
        token_env.algorithm,
        timedelta(minutes=token_env.refresh_token_expire),
    )


class AuthTokenBearer(HTTPBearer):
    def __init__(self, allowed_role: list):
        self._allowed_role = allowed_role
        super().__init__()

    def verify_access_token(self, token: str) -> bool:
        try:
            _ = decode_access_token(token)
            return True
        except JWTError:
            return False

    async def __call__(self, request: Request):
        if auth := await super().__call__(request=request):
            if not auth.scheme.lower() == "bearer":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Schéma d'authentification non valide.",
                )
            if not self.verify_access_token(auth.credentials):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Jeton invalide ou expiré.",
                )
            token = decode_access_token(auth.credentials)
            if token.role_or_type not in self._allowed_role:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Vous n'avez pas les autorisations nécessaires pour accéder à cette ressource.",  # noqa: E501
                )
            return auth.credentials

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Impossible de valider les informations d'identification",
            headers={"WWW-Authenticate": "Bearer"},
        )
