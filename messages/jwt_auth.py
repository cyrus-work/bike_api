from typing import Optional

from pydantic import BaseModel

from messages.messages import Message, ExceptionMsg


class TokenData(BaseModel):
    email: Optional[str] = None
    ip: Optional[str] = None


class IPNotMatchException(Exception):
    def __init__(self, msg):
        self.msg = msg


class AccessRefreshTokenMsg(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

    class Config:
        schema_extra = {
            "example": {
                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6InlhcmFuZ0BnbWFpbC5jb20iLCJleHAiOjE2ODEyOTE1MTV9.xmMUv1mdyezr-uLahm_fW97R_Jrvx1R05jlGj_YjQz8",
                "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6InlhcmFuZ0BnbWFpbC5jb20iLCJleHAiOjE2ODEzNzQzMTV9.ogGGzNPZYtFUHLsyE36gY8qYc3YqiBR3UrC_vDLoSNo",
                "token_type": "bearer"
            }
        }


class AccessTokenMsg(BaseModel):
    access_token: str
    token_type: str

    class Config:
        schema_extra = {
            "example": {
                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6InlhcmFuZ0BnbWFpbC5jb20iLCJleHAiOjE2ODEyOTE1MTV9.xmMUv1mdyezr-uLahm_fW97R_Jrvx1R05jlGj_YjQz8",
                "token_type": "bearer"
            }
        }


class RefreshTokenMsg(BaseModel):
    refresh_token: str

    class Config:
        schema_extra = {
            "Example": {
                "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6InlhcmFuZ0BnbWFpbC5jb20iLCJleHAiOjE2ODEzNzQzMTV9.ogGGzNPZYtFUHLsyE36gY8qYc3YqiBR3UrC_vDLoSNo",
            }
        }


class LoginTokenMsg(AccessRefreshTokenMsg, RefreshTokenMsg):
    token_type: str

    class Config:
        schema_extra = {
            "example": {
                "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6InlhcmFuZ0BnbWFpbC5jb20iLCJleHAiOjE2ODEzNzQzMTV9.ogGGzNPZYtFUHLsyE36gY8qYc3YqiBR3UrC_vDLoSNo",
                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6InlhcmFuZ0BnbWFpbC5jb20iLCJleHAiOjE2ODEyOTE1MTV9.xmMUv1mdyezr-uLahm_fW97R_Jrvx1R05jlGj_YjQz8",
                "token_type": "bearer"
            }
        }


class VerifyTokenMsg(BaseModel):
    code: int
    content: str
    is_verify: bool

    class Config:
        schema_extra = {
            "example": {
                "code": 200,
                "content": "Token is valid",
                "is_verify": True
            }
        }


class UserInfoJWT(BaseModel):
    email: str = None
    uuid: str = None
    is_deleted: str = None
    is_blocked: str = None
    permission: str = None
    extra: str = None


class TokenExpiredMsg(Message):
    class Config:
        schema_extra = {
            "example": {
                "code": 451,
                "content": "Token is expired"
            }
        }


class TokenInvalidMsg(Message):
    class Config:
        schema_extra = {
            "example": {
                "code": 452,
                "content": "Token is invalid"
            }
        }


class SQLIntegrityErrorMsg(ExceptionMsg):
    class Config:
        schema_extra = {
            "example": {
                "detail": {
                    "code": 701,
                    "content": "Integrity Error"
                }
            }
        }


class TokenEmailNotExistsMsg(Message):
    class Config:
        schema_extra = {
            "example": {
                "code": 453,
                "content": "email is not exist"
            }
        }


class TokenRefreshNotExistsMsg(Message):
    class Config:
        schema_extra = {
            "example": {
                "code": 454,
                "content": "refresh token is not exist"
            }
        }


class TokenVerifyFailedMsg(Message):
    class Config:
        schema_extra = {
            "example": {
                "code": 455,
                "content": "Token verify failed"
            }
        }


class InvalidSignatureErrorMsg(ExceptionMsg):
    class Config:
        schema_extra = {
            "example": {
                "detail": {
                    "code": 456,
                    "content": "Signature Expired Error"
                }
            }
        }


class DataErrorMsg(Message):
    class Config:
        schema_extra = {
            "example": {
                "code": 457,
                "content": "Data Error"
            }
        }
