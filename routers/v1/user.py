from datetime import timedelta

from fastapi import APIRouter, Depends
from fastapi.requests import Request
from fastapi.responses import JSONResponse, HTMLResponse

from internal.app_config import mail_config
from internal.html_msg import html_ok_msg, html_ng_msg
from internal.jwt_auth import create_access_token, create_refresh_token, auth
from internal.log import logger
from internal.mysql_db import SessionLocal, get_db
from internal.utils import verify_password, generate_hash, send_mail
from messages.jwt_auth import AccessRefreshTokenMsg, SQLIntegrityErrorMsg
from messages.user import LoginFailMsg, UserNotFoundMsg, UserPasswordNotMatchMsg, UserLoginRequest, UserCreateMsg, \
    UserResendMsg, UserEmailAuthFailMsg, UserCreateFailMsg, UserEmailDuplicateMsg, UserCreateRequest, UserResendFailMsg, \
    UserEmailRequest, UserEmailConfirmMsg, InvalidUuidMsg
from models.user import get_user_by_email, make_user, get_users
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
async def post_login_user_api(request: Request, user: UserLoginRequest, db: SessionLocal = Depends(get_db)):
    """
    Login user

    :param request:
    :param user:
    :param db:
    :return:
    """

    logger.info(f">>> post_login_user_api start: {user}")
    try:
        user_db = get_user_by_email(db, user.email)
        logger.info(f"post_login_user_api: {user_db}")
        if not user_db:
            msg = {"code": 462, "content": "User not found."}
            logger.error(f"post_login_user_api msg: {msg}")
            return UserNotFoundMsg(**msg)

        if not verify_password(user.password, user_db.hashed_pwd):
            msg = {"code": 463, "content": "Password is wrong."}
            logger.error(f"post_login_user_api msg: {msg}")
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
        logger.info(f"post_login_user_api msg: {msg}")
        return AccessRefreshTokenMsg(**token_msg)

    finally:
        logger.info(f">>> post_login_user_api end")


@router.post(
    "/create",
    responses={
        200: {"model": UserCreateMsg},
        461: {"model": UserCreateFailMsg},
        701: {"model": SQLIntegrityErrorMsg},
        464: {"model": UserEmailDuplicateMsg},
    },
)
async def post_create_user_api(user: UserCreateRequest, db: SessionLocal = Depends(get_db)):
    """
    사용자 생성<p>

    :param user: UserCreateRequest 모델
    :param db: db session
    :return: UserCreateMsg 모델
    """
    logger.info(f">>> post_create_user_api: {user}")

    try:
        user_check = get_user_by_email(db, user.email)
        if user_check is not None:
            msg = {"code": 464, "content": "User Email Duplicate"}
            logger.error(f"post_create_user_api msg: {msg}")
            return JSONResponse(status_code=464, content=msg)

        name = user.name
        email = user.email
        password = user.password

        db_user = make_user(name=name, email=email, password=password)

        # user 생성
        db.add(db_user)

        logger.info(f"post_create_user_api db_user: {db_user}")

        db.commit()

        checker = generate_hash()
        send_mail(mail_config, db_user.email, checker)

        db_check = make_user_check(id=db_user.uid, checker=checker)
        db.add(db_check)
        db.commit()

        return UserCreateMsg(code=200, content="User create success")

    finally:
        logger.info(f">>> post_create_user_api end")


@router.post(
    "/resend",
    responses={
        200: {"model": UserResendMsg},
        461: {"model": UserNotFoundMsg},
        462: {"model": UserResendFailMsg},
    },
)
async def resend_user_api(data: UserEmailRequest, db: SessionLocal = Depends(get_db)):
    """
    이메일 인증을 다시 요청함.

    table [user_check]
    :param data: UserResendRequest 모델
    :param db: db session
    :return: UserResendMsg 모델
    """
    logger.info(f"resend_user_api start: {data}")

    try:
        email_str = data.email

        db_user = get_user_by_email(db, email_str)
        logger.info(f"resend_user_api db_user: {db_user}")
        if db_user is None:
            msg = {"code": 462, "content": "User not found"}
            logger.error(f"resend_user_api msg: {msg}")
            return UserNotFoundMsg(**msg)

        db_check = get_user_check_by_id(db, db_user.uid)
        if db_check is None:
            msg = {"code": 463, "content": "User auth checker not found"}
            logger.error(f"resend_user_api msg: {msg}")
            return UserEmailAuthFailMsg(**msg)

        logger.info(f"resend_user_api db_user: {db_user}")

        checker = generate_hash()
        send_mail(mail_config, db_user.email, checker)
        db_check.checker = checker
        db.merge(db_check)
        db.commit()

        logger.info(f"resend_user_api db_check: {email_str}, {checker}")
        return UserResendMsg(code=200, content="Resend email", email=email_str)

    finally:
        logger.info(f">>> resend_user_api end")


@router.get(
    "/email_confirm",
    responses={
        200: {"model": UserEmailConfirmMsg},
        461: {"model": UserNotFoundMsg},
        465: {"model": InvalidUuidMsg},
    },
)
async def email_confirm_user_api(email: str, checker: str, db: SessionLocal = Depends(get_db)):
    """
    이메일 인증

    :param email: 이메일
    :param checker: 인증 코드
    :param db: db session
    :return: UserEmailConfirmMsg 모델
    """
    logger.info(f">>> email_confirm_user_api: {email}, {checker}")

    try:
        web_url = mail_config["web"]
        html_ok_content = html_ok_msg(web_url)
        html_ng_content = html_ng_msg(web_url)

        db_user = get_user_by_email(db, email)
        if db_user is None:
            msg = {"code": 462, "content": "User not found"}
            logger.error(f"email_confirm_user_api msg: {msg}")
            return JSONResponse(status_code=462, content=msg)

        db_check = get_user_check_by_id(db, db_user.uid)
        if db_check is None:
            msg = {"code": 463, "content": "User auth checker not found"}
            logger.error(f"email_confirm_user_api msg: {msg}")
            return JSONResponse(status_code=463, content=msg)

        if db_check.checker == checker:
            db_user.email_verified = "Y"
            db.merge(db_user)
            db.delete(db_check)
            db.commit()

            logger.info(f"email_confirm_user_api: {email} confirm success")
            msg = {"code": 200, "content": "Email confirm success"}
            logger.info(f"email_confirm_user_api msg: {msg}")
            return HTMLResponse(content=html_ok_content, status_code=200)

        else:
            msg = {"code": 464, "content": "Invalid checker"}
            logger.error(f"email_confirm_user_api msg: {msg}")
            return HTMLResponse(content=html_ng_content, status_code=464)

    finally:
        logger.info(f">>> email_confirm_user_api end")

@router.get("/users")
async def read_users(db: SessionLocal = Depends(get_db)):
    users = get_users(db, offset=0, limit=100)
    return users


@router.post("/delete")
async def delete_user_by_email_api(req: UserEmailRequest, db: SessionLocal = Depends(get_db)):
    """
    사용자 삭제

    :param req: UserEmailRequest 모델
    :param db: db session
    :return:
    """
    logger.info(f">>> delete_user_by_email_api: {req}")

    try:
        email = req.email
        db_user = get_user_by_email(db, email)
        if db_user is None:
            msg = {"code": 462, "content": "User not found"}
            logger.error(f"delete_user_by_email_api msg: {msg}")
            return JSONResponse(status_code=462, content=msg)

        db.delete(db_user)
        db.commit()

        logger.info(f"delete_user_by_email_api: {email} delete success")
        return {"message": "delete success"}

    finally:
        logger.info(f">>> delete_user_by_email_api end")