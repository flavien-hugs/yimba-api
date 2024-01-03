from typing import Optional
from datetime import datetime

from pydantic import BaseModel, EmailStr

from yimba_api import BaseMongoModel
from yimba_api.shared import authentication as handler


class User(BaseModel):
    role: str
    fullname: Optional[str] = None


class SignupUser(User):
    email: EmailStr
    password: str


class LoginUser(BaseModel):
    email: EmailStr
    password: str


class LogoutUser(BaseModel):
    refresh_token: str


class ManageAccount(BaseModel):
    is_active: bool = True


class ChangePassword(BaseModel):
    email: EmailStr


class UserInDB(BaseMongoModel, SignupUser):
    is_active: bool = True

    @staticmethod
    def hash_password(password: str):
        return handler.password_hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str):
        return handler.verify_password(plain_password, hashed_password)


class UserOutBase(BaseModel):
    role: str
    email: EmailStr
    is_active: bool = True
    fullname: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class UserOutSchema(UserOutBase):
    id: str


class UserLoginOutDB(BaseModel):
    access_token: str
    refresh_token: str
    user: UserOutSchema
