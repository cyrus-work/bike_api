# jwt_auth.py
import traceback
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from fastapi import Header, Depends
from fastapi.requests import Request
from fastapi.security import OAuth2PasswordBearer
from jwt import ExpiredSignatureError, DecodeError, PyJWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from internal.app_config import auth
from internal.exceptions import (
    JWTDataExpiredException,
    EmailNotExistException,
    JWTErrorsException,
    CredentialException,
    AdminRequiredException,
)
from internal.log import logger
from internal.mysql_db import SessionLocal, get_db
from internal.utils import verify_password, exception_handler
from messages.jwt_auth import TokenData
from models.user import get_user_by_email, User, get_active_user_by_email

SECRET_KEY = auth["secret"]
DATA_SECRET_KEY = auth["data_secret"]
data_expires = auth["data_expires"]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="http://localhost:8000/users/login")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def authenticate_user(email: str, password: str) -> bool | User:
    """
    사용자 인증 - 사용자 정보 확인

    :param email: 사용자 이메일
    :param password: 사용자 비밀번호
    :return: 사용자 정보
    """
    logger.info(f"  -- authenticate_user: {email}, {password}")
    db = SessionLocal()
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def get_active_auth_user(email: str, password: str):
    """
    사용자 인증 - 활성화된 사용자

    :param email: 사용자 이메일
    :param password: 사용자 비밀번호
    """
    logger.info(f"  -- get_active_auth_user: {email}")
    db = SessionLocal()
    db_user = get_active_user_by_email(db, email)
    if not db_user:
        return False
    if not verify_password(password, db_user.hashed_pwd):
        return False
    return db_user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Access Token 생성

    :param data: 사용자 정보
    :param expires_delta: 만료 시간
    :return: Access Token
    """
    logger.info(f"  -- create_access_token: {data}, {expires_delta}")
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=auth["access_token_expires"])
    expire = expire.astimezone(timezone.utc)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Refresh Token 생성

    :param data: 사용자 정보
    :param expires_delta: 만료 시간
    :return: Refresh Token
    """
    logger.info(f"  -- create_refresh_token: {data}, {expires_delta}")
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(days=7)
    expire = expire.astimezone(timezone.utc)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt


def encoded_data_to_jwt(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    데이터를 JWT로 인코딩

    :param data: 사용자 정보
    :param expires_delta: 만료 시간
    :return: JWT
    """
    logger.info(f"  -- encoded_data_to_jwt: {data}")
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=data_expires)
    data.update({"exp": expire})
    encoded_jwt = jwt.encode(data, DATA_SECRET_KEY, algorithm="HS256")
    return encoded_jwt


def decode_data_from_jwt(token: str) -> dict:
    """
    JWT에서 데이터 디코딩

    :param token: JWT
    :return: 디코딩된 데이터
    """
    logger.info(f"  -- decode_data_from_jwt: {token}")
    try:
        decoded_data = jwt.decode(token, DATA_SECRET_KEY, algorithms=["HS256"])
        return decoded_data

    except ExpiredSignatureError:
        raise JWTDataExpiredException()


def get_email_from_jwt(token: str) -> str:
    """
    JWT에서 이메일 가져오기

    :param token: JWT
    :return: 이메일
    """
    payload = jwt.decode(token, auth["secret"], algorithms=["HS256"])
    email: str = payload.get("email")
    logger.info(f"get_email_from_jwt: {email}")
    return email


@exception_handler
def get_email_from_jwt_depends(authorization: str = Header(..., alias="Authorization")):
    """
    JWT에서 이메일 가져오기

    :param authorization: Authorization Header
    :return: 이메일
    """
    try:
        token = authorization.split()[1]
        payload = jwt.decode(token, auth["secret"], algorithms=["HS256"])
        email = payload.get("email")
        if email is None:
            raise JWTErrorsException()
        return email

    finally:
        logger.info(f"get_email_from_jwt_depends")


@exception_handler
def get_info_from_refresh_token(token: str):
    """
    Refresh Token에서 정보 가져오기

    :param token: Refresh Token
    :return: 정보
    """
    payload = jwt.decode(token, auth["secret"], algorithms=["HS256"])
    logger.info(f"get_info_from_refresh_token: {payload}")
    return payload


@exception_handler
def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
):
    """
    현재 사용자 정보 가져오기

    :param db: Session
    :param token: Token 정보
    """
    logger.info(f"  -- get_current_user start")
    try:
        payload = jwt.decode(token, auth["secret"], algorithms=["HS256"])
        email: str = payload.get("email")
        if email is None:
            raise EmailNotExistException()

        user = get_active_user_by_email(db, email)
        if user is None:
            logger.error(f"  -- get_current_user: {traceback.format_exc()}")
            raise CredentialException()
        return user, db

    except ExpiredSignatureError:
        logger.error(f"  -- get_current_user: {traceback.format_exc()}")
        raise JWTDataExpiredException()

    except DecodeError:
        logger.error(f"  -- get_current_user: {traceback.format_exc()}")
        raise JWTErrorsException()

    except PyJWTError:
        logger.error(f"  -- get_current_user: {traceback.format_exc()}")
        raise JWTErrorsException()

    finally:
        logger.info(f"  -- get_current_user end")


@exception_handler
def get_access_token_from_cookie(db: Session, token: str = Header(None)):
    """
    쿠키에서 Access Token 가져오기

    :param db: Session
    :param token: Token 정보
    """
    logger.info("  -- get_access_token_from_cookie start")

    try:
        access_token_bytes = token.encode("utf-8")

        payload = jwt.decode(access_token_bytes, auth["secret"], algorithms=["HS256"])
        email: str = payload.get("email")
        if email is None:
            raise EmailNotExistException()

    except ExpiredSignatureError:
        logger.error(f"  -- get_access_token_from_cookie: {traceback.format_exc()}")
        raise JWTDataExpiredException()

    user = get_active_user_by_email(db, email)
    if user is None:
        raise CredentialException()

    return user


@exception_handler
def admin_required(current_user: User = Depends(get_current_user)):
    logger.info(f"  -- admin_required start: {current_user}")
    user, db = current_user
    if user.level != 9:
        raise AdminRequiredException()
    return current_user


def get_user_from_jwt(db: SessionLocal, token: str):
    try:
        payload = jwt.decode(token, auth["secret"], algorithms=["HS256"])
        email: str = payload.get("email")
        logger.info(f"get_user_from_jwt: {email}")
        db = SessionLocal()
        user = get_user_by_email(db, email)
        return user

    except Exception:
        logger.error(f"get_user_from_jwt: {traceback.format_exc()}")
        raise JWTErrorsException()


def verify_token(token: str):
    try:
        decoded_token = jwt.decode(token, auth["secret"], algorithms=["HS256"])
        return decoded_token
    except jwt.ExpiredSignatureError:
        raise JWTDataExpiredException()
    except jwt.InvalidTokenError:
        raise JWTErrorsException()


def get_payload_from_jwt(req: Request, token: str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, auth["secret"], algorithms=["HS256"])
    logger.info(f"get_payload_from_jwt: {payload}")

    result = TokenData(email=payload.get("email"), ip=payload.get("ip"))
    return result


def token_make_function(email: str):
    access_token_expires = timedelta(minutes=auth["access_token_expires"])
    access_token = create_access_token(
        data={"email": email},
        expires_delta=access_token_expires,
    )

    refresh_token_expires = timedelta(minutes=auth["refresh_token_expires"])
    refresh_token = create_refresh_token(
        data={"email": email, "refresh": True},
        expires_delta=refresh_token_expires,
    )
    logger.info(f"token_make_function expires access_token: {access_token_expires}")

    token_msg = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }
    return token_msg


def access_token_make_function(email: str):
    access_token_expires = timedelta(minutes=auth["access_token_expires"])
    access_token = create_access_token(
        data={"email": email},
        expires_delta=access_token_expires,
    )
    return access_token
