from typing import Optional

from pydantic import BaseModel

from messages.messages import Message


### User Request Models ###
class UserLoginRequest(BaseModel):
    email: str
    password: str

    class Config:
        schema_extra = {"example": {"email": "test@test.com", "password": "test"}}


class UserCreateRequest(BaseModel):
    """
    User create model

    password: User password
    email: User email
    checker: str
    name: Username (optional)
    email_confirm: User email confirm(default = 'N') (optional)
    """

    email: str
    password: str
    checker: str

    agreement1: Optional[str] = None
    agreement2: Optional[str] = None
    agreement3: Optional[str] = None

    name: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "password": "test",
                "email": "test@test.com",
                "name": "test",
                "checker": "test",
                "agreement1": "Y",
                "agreement2": "Y",
                "agreement3": "Y"
            }
        }


class USerCreateRequestV2(BaseModel):
    data: str

    class Config:
        schema_extra = {
            "example": {
                "data": "test"
            }
        }


class UserUpdateRequest(BaseModel):
    """
    User create model

    password: User password
    email: User email
    name: Username (optional)
    email_confirm: User email confirm(default = 'N') (optional)
    """

    email: str
    password: str
    name: Optional[str] = None
    email_confirm: Optional[str] = "Y"

    class Config:
        schema_extra = {
            "example": {
                "password": "test",
                "email": "test@test.com",
                "name": "test",
                "email_confirm": "Y"
            }
        }


class UserEmailRequest(BaseModel):
    """
    User email model
    email: User email(str)
    """

    email: str

    class Config:
        schema_extra = {"example": {"email": "test@test.com"}}


### User Success Messages ###
class UserCreateMsg(Message):
    class Config:
        schema_extra = {"example": {"code": 200, "content": "User create"}}


class UserResendMsg(Message):
    """
    User resend email model
    email: User email(str)
    """

    email: str

    class Config:
        schema_extra = {
            "example": {"code": 200, "content": "Email sent", "email": "test@test.com"}
        }


class UserEmailConfirmMsg(Message):
    class Config:
        schema_extra = {"example": {"code": 200, "content": "User email confirm"}}


### User Fail Messages ###
class LoginFailMsg(Message):
    class Config:
        schema_extra = {"example": {"code": 461, "content": "Login fail"}}


class UserEmailAuthFailMsg(Message):
    class Config:
        schema_extra = {
            "example": {"code": 461, "content": "User auth checker not found"}
        }


class UserResendFailMsg(Message):
    class Config:
        schema_extra = {"example": {"code": 461, "content": "Email send fail"}}


class UserCreateFailMsg(Message):
    """
    User create fail message
    """

    class Config:
        schema_extra = {"example": {"code": 461, "content": "User create fail"}}


class UserNotFoundMsg(Message):
    class Config:
        schema_extra = {
            "example": {"detail": {"code": 462, "content": "User not found"}}
        }


class UserPasswordNotMatchMsg(Message):
    class Config:
        schema_extra = {"example": {"code": 463, "content": "User password not match"}}


class UserEmailDuplicateMsg(Message):
    """
    User email duplicate message
    """

    class Config:
        schema_extra = {"example": {"code": 464, "content": "User Email duplicate."}}


class InvalidUuidMsg(Message):
    class Config:
        schema_extra = {"example": {"code": 465, "content": "uuid is invalid"}}
