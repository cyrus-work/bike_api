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

from internal.log import logger
from internal.mysql_db import SessionLocal
from internal.utils import verify_password
from messages.jwt_auth import TokenData
from models.user import get_user_by_email

with open("./configs/auth.json") as f:
    auth = json.load(f)
    SECRET_KEY = auth["secret"]
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
        raise HTTPException(status_code=461, detail="JWT token expired")
    except InvalidTokenError:
        raise HTTPException(status_code=461, detail="Invalid JWT token")
    except Exception as _:
        raise HTTPException(status_code=500, detail=str(e))


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
        logger.error(e)
        return None


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
