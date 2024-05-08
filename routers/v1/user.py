import traceback
from datetime import timedelta

from fastapi import APIRouter
from fastapi.requests import Request
from fastapi.responses import JSONResponse, HTMLResponse
from sqlalchemy.exc import IntegrityError

from internal.app_config import mail_config
from internal.html_msg import html_ok_msg, html_ng_msg
from internal.jwt_auth import create_access_token, create_refresh_token, auth
from internal.log import logger
from internal.mysql_db import SessionLocal
from internal.utils import verify_password, generate_hash, send_mail
from messages.jwt_auth import AccessRefreshTokenMsg, SQLIntegrityErrorMsg
from messages.user import LoginFailMsg, UserNotFoundMsg, UserPasswordNotMatchMsg, UserLoginRequest, UserCreateMsg, \
    UserCreateRequest, UserCreateFailMsg, UserEmailDuplicateMsg, UserResendMsg, UserResendFailMsg, UserEmailRequest, \
    UserEmailAuthFailMsg, UserEmailConfirmMsg, InvalidUuidMsg
from models.user import get_user_by_email, make_user
from models.user_check import make_user_check, get_user_check_by_id

router = APIRouter()


@router.post(
    "/login",
    responses={
        200: {"model": AccessRefreshTokenMsg},
        461: {"model": LoginFailMsg},
        462: {"model": UserNotFoundMsg},
        463: {"model": UserPasswordNotMatchMsg},
    },
)
async def post_login_user_api(request: Request, user: UserLoginRequest):
    """
    Login user

    :param request:
    :param user:
    :return:
    """
    logger.info(f"post_login_user_api start: {user}")
    db = None
    try:

        db = SessionLocal()

        user_db = get_user_by_email(db, user.email)
        logger.info(f"post_login_user_api: {user_db}")
        if not user_db:
            msg = {"code": 462, "content": "User not found."}
            logger.error(f"post_login_user_api: {msg}")
            return UserNotFoundMsg(**msg)

        if not verify_password(user.password, user_db.hashed_pwd):
            msg = {"code": 463, "content": "Password is wrong."}
            logger.error(f"post_login_user_api: {msg}")
            return UserPasswordNotMatchMsg(**msg)

        access_token_expires = timedelta(minutes=auth["access_token_expires"])
        refresh_token_expires = timedelta(minutes=auth["refresh_token_expires"])

        access_token = create_access_token(
            data={"email": user.email},
            expires_delta=access_token_expires,
        )
        refresh_token = create_refresh_token(
            data={"email": user.email, "refresh": True},
            expires_delta=refresh_token_expires,
        )
        token_msg = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
        msg = {"code": 200, "content": token_msg}
        logger.info(f"post_login_user_api: {msg}")
        return AccessRefreshTokenMsg(**token_msg)

    finally:
        logger.info(f"post_login_user_api end")
        if db:
            db.close()


@router.post(
    "/create",
    responses={
        200: {"model": UserCreateMsg},
        461: {"model": UserCreateFailMsg},
        701: {"model": SQLIntegrityErrorMsg},
        464: {"model": UserEmailDuplicateMsg},
    },
)
async def post_create_user_api(user: UserCreateRequest):
    """
    사용자 생성<p>

    :param user: UserCreateRequest 모델
    :return: UserCreateMsg 모델
    """
    logger.info(f"post_create_user_api: {user}")
    db = None
    try:
        db = SessionLocal()

        user_check = get_user_by_email(db, user.email)
        if user_check is not None:
            msg = {"code": 464, "content": "User Email Duplicate"}
            logger.error(f"post_create_user_api - msg: {msg}")
            return JSONResponse(status_code=464, content=msg)

        name = user.name
        email = user.email
        password = user.password

        db_user = make_user(name=name, email=email, password=password)

        # user 생성
        db.add(db_user)

        logger.info(f"post_create_user_api - db_user: {db_user}")

        db.commit()

        checker = generate_hash()
        send_mail(mail_config, db_user.email, checker)

        db_check = make_user_check(id=db_user.uid, checker=checker)
        db.add(db_check)
        db.commit()

        return UserCreateMsg(code=200, content="User create success")

    except IntegrityError as _:
        db.rollback()
        logger.error(f"post_create_user_api: {traceback.format_exc()}")
        msg = {"code": 701, "content": "SQL Integrity Error"}
        logger.error(f"post_create_user_api - msg: {msg}")
        return JSONResponse(status_code=701, content=msg)

    finally:
        logger.info(f"post_create_user_api end")
        if db:
            db.close()


@router.post(
    "/resend",
    responses={
        200: {"model": UserResendMsg},
        461: {"model": UserNotFoundMsg},
        462: {"model": UserResendFailMsg},
    },
)
async def resend_user_api(data: UserEmailRequest):
    """
    이메일 인증을 다시 요청함.

    table [user_check]
    :param data: UserResendRequest 모델
    :return: UserResendMsg 모델
    """
    logger.info(f"resend_user_api: {data}")
    db = None
    email_str = data.email
    try:
        db = SessionLocal()
        db_user = get_user_by_email(db, email_str)
        logger.info(f"resend_user_api - db_user: {db_user}")
        if db_user is None:
            msg = {"code": 462, "content": "User not found"}
            logger.error(f"resend_user_api - msg: {msg}")
            return UserNotFoundMsg(**msg)

        db_check = get_user_check_by_id(db, db_user.uid)
        if db_check is None:
            msg = {"code": 463, "content": "User auth checker not found"}
            logger.error(f"resend_user_api - msg: {msg}")
            return UserEmailAuthFailMsg(**msg)

        logger.info(f"resend_user_api - db_user: {db_user}")
        checker = generate_hash()
        send_mail(mail_config, db_user.email, checker)
        db_check.checker = checker
        db.merge(db_check)
        db.commit()
        logger.info(f"resend_user_api - db_check: {email_str}, {checker}")
        return UserResendMsg(code=200, content="Resend email", email=email_str)

    finally:
        if db:
            db.close()

@router.get(
    "/email_confirm",
    responses={
        200: {"model": UserEmailConfirmMsg},
        461: {"model": UserNotFoundMsg},
        465: {"model": InvalidUuidMsg},
    },
)
async def email_confirm_user_api(email: str, checker: str):
    """
    이메일 인증

    :param email: 이메일
    :param checker: 인증 코드
    :return: UserEmailConfirmMsg 모델
    """
    logger.info(f"email_confirm_user_api: {email}, {checker}")
    db = None
    web_url = mail_config["web"]
    html_ok_content = html_ok_msg(web_url)
    html_ng_content = html_ng_msg(web_url)
    try:
        db = SessionLocal()
        db_user = get_user_by_email(db, email)
        if db_user is None:
            msg = {"code": 462, "content": "User not found"}
            logger.error(f"email_confirm_user_api - msg: {msg}")
            return JSONResponse(status_code=462, content=msg)

        db_check = get_user_check_by_id(db, db_user.uid)
        if db_check is None:
            msg = {"code": 463, "content": "User auth checker not found"}
            logger.error(f"email_confirm_user_api - msg: {msg}")
            return JSONResponse(status_code=463, content=msg)

        if db_check.checker == checker:
            db_user.email_verified = "Y"
            db.merge(db_user)
            db.delete(db_check)
            db.commit()

            logger.info(f"email_confirm_user_api: {email} confirm success")
            msg = {"code": 200, "content": "Email confirm success"}
            logger.info(f"email_confirm_user_api - msg: {msg}")
            return HTMLResponse(content=html_ok_content, status_code=200)

        else:
            msg = {"code": 464, "content": "Invalid checker"}
            logger.error(f"email_confirm_user_api - msg: {msg}")
            return HTMLResponse(content=html_ng_content, status_code=464)

    finally:
        if db:
            db.close()
