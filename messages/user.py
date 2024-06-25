from typing import Optional

from pydantic import BaseModel

from messages.messages import Message

"""
User Request Models
"""


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
                "agreement3": "Y",
            }
        }


class UserCreateRequestV2(BaseModel):
    data: str

    class Config:
        schema_extra = {"example": {"data": "test"}}


class UserUpdateRequest(BaseModel):
    """
    User create model

    password: User password
    email: User email
    name: Username (optional)
    email_confirm: User email confirm(default = 'N') (optional)
    """

    email: str
    checker: str
    password: Optional[str] = None
    name: Optional[str] = None
    level: Optional[int] = None

    class Config:
        schema_extra = {
            "example": {
                "password": "test",
                "checker": "T1A1249c606548eee1b5e1736ccad255da646a09de4fdc971614e11c73683a63",
                "email": "test@test.com",
                "name": "test",
                "level": 1,
            }
        }


class UserUpdateAdminReq(BaseModel):
    """
    User update model

    email: User email
    name: Username (optional)
    """

    email: str
    name: Optional[str] = None
    password: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "email": "test@test.com",
                "name": "test",
                "password": "test",
            }
        }


class UserPwChangeRequest(BaseModel):
    """
    User password change model

    password: User password
    email: User email
    """

    prev_password: str
    password: str

    class Config:
        schema_extra = {
            "example": {
                "prev_password": "test",
                "password": "test_new",
            }
        }


class UserEmailRequest(BaseModel):
    """
    User email model
    email: User email(str)
    """

    email: str
    offset: Optional[int] = 0
    limit: Optional[int] = 50

    class Config:
        schema_extra = {"example": {"email": "test@test.com", "offset": 0, "limit": 50}}


"""
User Success Messages
"""


class UserCreateMsg(Message):
    class Config:
        schema_extra = {
            "example": {
                "code": 200,
                "content": "User create",
            }
        }


class UserSendMsg(Message):
    """
    User resend email model
    email: User email(str)
    """

    email: str
    checker: str

    class Config:
        schema_extra = {
            "example": {
                "code": 200,
                "content": "Email sent",
                "email": "test@test.com",
                "checker": "T1A132b0eb27b18ed63ff2e12d600e16a0d297cfa68d848ff4cc3aaea8704829",
            }
        }


class UserEmailConfirmMsg(Message):
    class Config:
        schema_extra = {"example": {"code": 200, "content": "User email confirm"}}


"""
User Fail Messages
"""


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


class UserSearchFlagRequest(BaseModel):
    """
    User search flag model
    email: User email(str)
    """

    verified: str
    offset: Optional[int] = 0
    limit: Optional[int] = 50

    class Config:
        schema_extra = {
            "example": {
                "verified": "Y",
                "offset": 0,
                "limit": 50,
            }
        }


class UserSearchWalletRequest(BaseModel):
    """
    User search wallet model
    wallet: User wallet(str)
    """

    exist: Optional[bool]
    wallet: Optional[str]
    offset: Optional[int] = 0
    limit: Optional[int] = 50

    class Config:
        schema_extra = {
            "example": {
                "exist": True,
                "wallet": "0x2B00D03AeeAe930Fe5BB5dcf56B82Bb715Ce522A",
                "offset": 0,
                "limit": 50,
            }
        }


"""
Admin messages
"""


class UserListGetReq(BaseModel):
    """
    User list get request model
    email: User email(str)
    """

    offset: Optional[int] = 0
    limit: Optional[int] = 50

    class Config:
        schema_extra = {"example": {"offset": 0, "limit": 50}}
