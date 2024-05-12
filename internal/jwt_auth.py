import json
import traceback
from datetime import datetime, timedelta
from typing import Optional

import jwt
from fastapi import Header, Depends
from fastapi.security import OAuth2PasswordBearer
from jwt import ExpiredSignatureError, InvalidTokenError
from passlib.context import CryptContext
from starlette.exceptions import HTTPException
from starlette.requests import Request

from internal.exceptions import JWTDataExpiredException
from internal.log import logger
from internal.mysql_db import SessionLocal
from internal.utils import verify_password
from messages.jwt_auth import TokenData
from models.user import get_user_by_email

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
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=auth["access_token_expires"])
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
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=7)
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
        expire = datetime.utcnow() + expires_delta
    else:
        # 기본 값으로 data_expires를 사용 (60 분)
        expire = datetime.utcnow() + timedelta(minutes=data_expires)
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


