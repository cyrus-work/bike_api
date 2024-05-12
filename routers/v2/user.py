from datetime import timedelta

from fastapi import APIRouter, Depends
from fastapi.requests import Request
from fastapi.responses import JSONResponse, HTMLResponse

from internal.app_config import mail_config
from internal.exceptions import UserExistsException
from internal.html_msg import html_ok_msg, html_ng_msg
from internal.jwt_auth import create_access_token, create_refresh_token, auth, get_info_from_refresh_token, \
    oauth2_scheme, encoded_data_to_jwt
from internal.log import logger
from internal.mysql_db import SessionLocal, get_db
from internal.utils import verify_password, send_mail, get_password_hash, generate_hash
from messages.jwt_auth import AccessRefreshTokenMsg, SQLIntegrityErrorMsg, TokenEmailNotExistsMsg, \
    TokenRefreshNotExistsMsg, AccessTokenMsg
from messages.user import LoginFailMsg, UserNotFoundMsg, UserPasswordNotMatchMsg, UserLoginRequest, UserCreateMsg, \
    UserResendMsg, UserCreateFailMsg, UserEmailDuplicateMsg, UserCreateRequest, UserEmailRequest, UserEmailConfirmMsg, \
    InvalidUuidMsg
from models.user import get_user_by_email, make_user, get_users, get_user_exist_by_email
from models.user_agree import make_user_agree
from models.user_check import make_user_check, get_user_check_by_email

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
        name = user.name
        email = user.email
        password = user.password
        checker = user.checker

        db_user = get_user_by_email(db, user.email)
        if db_user is not None:
            msg = {"code": 464, "content": "User Email Duplicate"}
            logger.error(f"post_create_user_api msg: {msg}")
            return JSONResponse(status_code=464, content=msg)

        db_user = make_user(name=name, email=email, password=password)

        # user 생성
        db.add(db_user)
        db.flush()

        db_agree = make_user_agree(db_user.uid)
        db.add(db_agree)
        db.flush()

        logger.info(f"post_create_user_api db_user: {db_user}")

        db.commit()

        return UserCreateMsg(code=200, content="User create success")

    finally:
        logger.info(f">>> post_create_user_api end")


@router.post(
    "/email_send",
)
async def post_user_email_send_api(data: UserEmailRequest, db: SessionLocal = Depends(get_db)):
    """
    이메일 인증을 요청함.

    table [user_check]
    :param data: UserResendRequest 모델
    :param db: db session
    :return: UserResendMsg 모델
    """
    logger.info(f">>> post_user_email_send_api start: {data}")

    try:
        email = data.email

        checker = generate_hash()
        logger.info(f"post_user_email_send_api checker: {checker}")

        db_user = make_user(email=email, password='', name='', email_verified="N")
        db_user_exist = get_user_by_email(db, email)
        logger.info(f"post_user_email_send_api db_user_exist: {db_user_exist}")
        if db_user_exist is not None:
            if db_user_exist.email_verified == "Y":
                logger.info(f"post_user_email_send_api: user exists")
                raise UserExistsException
            else:
                logger.info(f"post_user_email_send_api: delete user")
                db.delete(db_user_exist)
                db.commit()

        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        logger.info(f"post_user_email_send_api db_user: {db_user}")

        user_json = {"email": email, "uid": db_user.uid, "created_at": db_user.created_at.isoformat()}

        db_user = get_user_exist_by_email(db, email)
        logger.info(f"post_user_email_send_api: {db_user}")
        if db_user is not None:
            msg = {"code": 462, "content": "User founded"}
            logger.error(f"post_user_email_send_api msg: {msg}")
            return JSONResponse(status_code=462, content=msg)

        db_check = get_user_check_by_email(db, email)
        if db_check is None:
            logger.info(f"post_user_email_send_api: new user")
            db_checkout = make_user_check(email=email, checker=checker)
            db.add(db_checkout)
            db.commit()
        else:
            logger.info(f"post_user_email_send_api: resend user")
            db_check.checker = checker
            db.merge(db_check)
            db.commit()

        user_json["checker"] = checker

        checker_msg = encoded_data_to_jwt(user_json)

        send_mail(mail_config, email, checker_msg)

        logger.info(f"post_user_email_send_api db_check: {email}, {checker}")
        return UserResendMsg(code=200, content="Send email", email=email)

    finally:
        logger.info(f">>> post_user_email_send_api end")


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

        db_check = get_user_check_by_email(db, email)
        if db_check is None:
            msg = {"code": 463, "content": "User auth checker not found"}
            logger.error(f"email_confirm_user_api msg: {msg}")
            return JSONResponse(status_code=463, content=msg)

        if db_check.checker == checker:
            db_user = make_user(email=email, password='', name='', email_verified="Y")
            db.add(db_user)
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


@router.post("/update")
async def update_user_by_email_api(req: UserCreateRequest, db: SessionLocal = Depends(get_db)):
    """
    사용자 업데이트

    :param req: UserCreateRequest 모델
    :param db: db session
    :return:
    """
    logger.info(f">>> update_user_by_email_api: {req}")

    try:
        email = req.email
        password = req.password

        db_user = get_user_by_email(db, email)
        if db_user is None:
            msg = {"code": 462, "content": "User not found"}
            logger.error(f"update_user_by_email_api msg: {msg}")
            return JSONResponse(status_code=462, content=msg)

        db_user.name = req.name
        db_user.hashed_pwd = get_password_hash(password)

        db.merge(db_user)
        db.commit()

        logger.info(f"update_user_by_email_api: {email} update success")
        return {"message": "update success"}

    finally:
        logger.info(f">>> update_user_by_email_api end")


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


@router.post(
    "/refresh",
)
async def refresh_token_api(db: SessionLocal = Depends(get_db), token: str = Depends(oauth2_scheme)):
    logger.info(f">>> refresh_token_api: {token}")
    try:
        info = get_info_from_refresh_token(token)

        email = info.get("email")
        refresh = info.get("refresh")
        if email is None:
            msg = {"code": 463, "content": "email is not exist"}
            logger.error(f"refresh_token_api: {msg}")
            return TokenEmailNotExistsMsg(**msg)

        if refresh is None:
            msg = {"code": 464, "content": "refresh token is not exist"}
            logger.error(f"refresh_token_api: {msg}")
            return TokenRefreshNotExistsMsg(**msg)

        user = get_user_by_email(db, email)
        if user is None:
            msg = {"code": 462, "content": "User not found."}
            logger.error(f"refresh_token_api: {msg}")
            return UserNotFoundMsg(**msg)

        access_token_expires = timedelta(minutes=auth["access_token_expires"])
        access_token = create_access_token(
            data={"email": email}, expires_delta=access_token_expires
        )

        token_msg = {"access_token": access_token, "token_type": "bearer"}
        logger.info(f"refresh_token_api: {token_msg}")
        return AccessTokenMsg(**token_msg)

    finally:
        logger.info(f">>> refresh_token_api end")
