import json
import traceback
from datetime import datetime, timedelta
from typing import Optional

import jwt
from fastapi import Header, Depends
from fastapi.exceptions import HTTPException
from fastapi.requests import Request
from fastapi.security import OAuth2PasswordBearer
from jwt import ExpiredSignatureError, InvalidTokenError
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from internal.exceptions import (
    JWTDataExpiredException,
    UserEmailNotExistException,
    JWTErrorsException,
    CredentialException,
    AdminRequiredException,
)
from internal.log import logger
from internal.mysql_db import SessionLocal, get_db
from internal.utils import verify_password, exception_handler
from messages.jwt_auth import TokenData
from models.user import get_user_by_email, User

with open("./configs/auth.json") as f:
    auth = json.load(f)
    SECRET_KEY = auth["secret"]
    DATA_SECRET_KEY = auth["data_secret"]
    data_expires = auth["data_expires"]
    f.close()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="http://localhost:8000/users/login")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def authenticate_user(email: str, password: str):
    logger.info(f"authenticate_user: {email}, {password}")
    db = SessionLocal()
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    access token을 만드는 함수.
    :param data:
    :param expires_delta:
    :return:
    """
    logger.info(f"create_access_token: {data}, {expires_delta}")
    logger.info(f"secret_key: {SECRET_KEY}")
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=auth["access_token_expires"])
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    refresh token을 만드는 함수
    :param data:
    :param expires_delta:
    :return:
    """
    logger.info(f"create_refresh_token: {data}, {expires_delta}")
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(days=7)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt


def encoded_data_to_jwt(data: dict, expires_delta: Optional[timedelta] = None):
    """
    data를 jwt로 인코딩하는 함수

    :param data:
    :param expires_delta:
    :return:
    """
    logger.info(f"encoded_data_to_jwt: {data}")
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        # 기본 값으로 data_expires를 사용 (60 분)
        expire = datetime.now() + timedelta(minutes=data_expires)
    data.update({"exp": expire})
    encoded_jwt = jwt.encode(data, DATA_SECRET_KEY, algorithm="HS256")
    return encoded_jwt


def decode_data_from_jwt(token: str):
    """
    jwt를 data로 디코딩하는 함수

    :param token:
    :return:
    """
    logger.info(f"decode_data_from_jwt: {token}")
    try:
        decoded_data = jwt.decode(token, DATA_SECRET_KEY, algorithms=["HS256"])
        return decoded_data
    except ExpiredSignatureError:
        raise JWTDataExpiredException


def get_email_from_jwt(token: str):
    payload = jwt.decode(token, auth["secret"], algorithms=["HS256"])
    email: str = payload.get("email")
    logger.info(f"get_email_from_jwt: {email}")
    return email


def get_email_from_jwt_depends(authorization: str = Header(..., alias="Authorization")):
    try:
        token = authorization.split()[1]
        payload = jwt.decode(token, auth["secret"], algorithms=["HS256"])
        email = payload.get("email")
        if email is None:
            raise InvalidTokenError("Invalid JWT token")
        return email
    except ExpiredSignatureError:
        raise ExpiredSignatureError
    except InvalidTokenError:
        raise InvalidTokenError
    except Exception as _:
        raise Exception


def get_info_from_refresh_token(token: str):
    payload = jwt.decode(token, auth["secret"], algorithms=["HS256"])
    logger.info(f"get_info_from_refresh_token: {payload}")
    return payload


@exception_handler
def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
):
    logger.info(f">>> get_current_user start")
    try:
        payload = jwt.decode(token, auth["secret"], algorithms=["HS256"])
        email: str = payload.get("email")
        if email is None:
            raise UserEmailNotExistException
    except jwt.PyJWTError:
        raise JWTErrorsException
    user = get_user_by_email(db, email)
    if user is None:
        raise CredentialException
    return user, db


def admin_required(current_user: User = Depends(get_current_user)):
    user, db = current_user
    if user.level != 9:
        raise AdminRequiredException
    return current_user


def get_user_from_jwt(db: SessionLocal, token: str):
    try:
        payload = jwt.decode(token, auth["secret"], algorithms=["HS256"])
        email: str = payload.get("email")
        logger.info(f"get_user_from_jwt: {email}")
        db = SessionLocal()
        user = get_user_by_email(db, email)
        return user

    except Exception as _:
        logger.error(f"get_user_from_jwt: {traceback.format_exc()}")
        raise Exception


def verify_token(token: str):
    try:
        decoded_token = jwt.decode(token, auth["secret"], algorithms=["HS256"])
        return decoded_token
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


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
