from fastapi import APIRouter, Depends
from fastapi.requests import Request
from fastapi.responses import JSONResponse, HTMLResponse

from internal.app_config import mail_config
from internal.exceptions import (
    UserExistsException,
    UserEmailNotConfirmException,
    UserNotExistsException,
    UserCheckerNotExistException,
    UserCheckerNotMatchException,
    UserEmailNotExistException,
    JWTRefreshTokenNotExistException,
    UserPasswordNotMatchException,
)
from internal.html_msg import html_ok_msg, html_ng_msg
from internal.jwt_auth import (
    get_info_from_refresh_token,
    oauth2_scheme,
    encoded_data_to_jwt,
    decode_data_from_jwt,
    token_make_function,
    access_token_make_function,
    get_current_user,
)
from internal.log import logger
from internal.mysql_db import SessionLocal, get_db
from internal.utils import verify_password, send_mail, get_password_hash, generate_hash
from messages.jwt_auth import AccessRefreshTokenMsg, AccessTokenMsg
from messages.user import (
    UserLoginRequest,
    UserCreateMsg,
    UserCreateRequest,
    UserEmailRequest,
    UserSendMsg,
    UserUpdateRequest,
    UserPwChangeRequest,
)
from models.user import (
    get_user_by_email,
    make_user,
    get_users,
    get_user_exist_by_email,
    User,
)
from models.user_check import (
    make_user_check,
    get_user_check_by_email,
    get_user_checks_by_email,
    clean_checkers,
)
from models.user_wallet import get_user_wallets, get_user_info_by_uid

router = APIRouter()


@router.post(
    "/login",
)
async def post_login_user_api(
    request: Request, user: UserLoginRequest, db: SessionLocal = Depends(get_db)
):
    """
    Login user

    :param request:
    :param user:
    :param db:
    :return:
    """

    logger.info(f">>> post_login_user_api start: {user}")
    try:
        email = user.email

        db_user = get_user_by_email(db, email)
        logger.info(f"post_login_user_api: {db_user}")
        if db_user is None:
            raise UserNotExistsException

        if not verify_password(user.password, db_user.hashed_pwd):
            raise UserPasswordNotMatchException

        token_msg = token_make_function(email)

        msg = {"code": 200, "content": token_msg}
        logger.info(f"post_login_user_api msg: {msg}")
        return AccessRefreshTokenMsg(**token_msg)

    finally:
        logger.info(f">>> post_login_user_api end")


@router.post(
    "/create",
)
async def post_create_user_api(
    user: UserCreateRequest, db: SessionLocal = Depends(get_db)
):
    """
    사용자 생성<p>

    :param user: UserCreateRequest 모델
    :param db: db session
    :return: UserCreateMsg 모델
    """
    logger.info(f">>> post_create_user_api: {user}")

    try:
        # 작성할 사용자 정보를 입력받는다.
        name = user.name
        email = user.email
        password = user.password
        checker = user.checker

        agree1 = user.agreement1
        agree2 = user.agreement2
        agree3 = user.agreement3

        logger.info(
            f"post_create_user_api: {name}, {email}, {password}, {checker}, {agree1}, {agree2}, {agree3}"
        )

        # 사용자 이메일로 정보를 조회한다.
        db_user = get_user_by_email(db, user.email)
        if db_user is None:
            # 사용자 정보가 없으면 가입절차 위반임.
            raise UserEmailNotExistException
        elif db_user.status != 0:
            # status 값이 0이 아니면 사용자가 존재하는 것으로 간주한다.
            raise UserExistsException

        db_user_checker = get_user_check_by_email(db, email)
        if db_user_checker is None:
            # 사용자 check용 키가 없다면 절차를 제대로 이행하지 못한 것임.
            raise UserCheckerNotExistException

        if db_user_checker.checker != checker:
            # 사용자 check용 키가 잘못되었다면 제대로된 키를 사용하여야 함.
            raise UserCheckerNotMatchException

        db_user = get_user_by_email(db, email)
        db_user.hashed_pwd = get_password_hash(password)
        db_user.name = name
        db_user.status = 1
        # 사용자 약관 동의 정보
        db_user.agreement1 = agree1
        db_user.agreement2 = agree2
        db_user.agreement3 = agree3

        # user 생성을 위해서 업데이트
        db.merge(db_user)
        db.flush()

        logger.info(f"post_create_user_api db_user: {db_user}")

        # 사용한 checker는 삭제한다.
        db.delete(db_user_checker)

        db.commit()

        return UserCreateMsg(code=200, content="User create success")

    finally:
        logger.info(f">>> post_create_user_api end")


@router.post(
    "/email_send",
)
async def post_user_email_send_api(
    data: UserEmailRequest, db: SessionLocal = Depends(get_db)
):
    """
    이메일 인증을 요청함.

    table [user_check]
    :param data: UserResendRequest 모델
    :param db: db session
    :return: UserSendMsg 모델
    """
    logger.info(f">>> post_user_email_send_api start: {data}")

    try:
        email = data.email

        checker = generate_hash()
        logger.info(f"post_user_email_send_api checker: {checker}")

        db_user = make_user(email=email, password=None, name=None, email_verified="N")
        db_user_exist = get_user_by_email(db, email)
        logger.info(f"post_user_email_send_api db_user_exist: {db_user_exist}")
        if db_user_exist is not None:
            if db_user_exist.status != 0:
                raise UserExistsException
            else:
                logger.info(f"post_user_email_send_api: delete user")
                db.delete(db_user_exist)
                db.commit()

        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        logger.info(f"post_user_email_send_api db_user: {db_user}")

        user_json = {
            "email": email,
            "uid": db_user.uid,
            "created_at": db_user.created_at.isoformat(),
        }

        db_user = get_user_exist_by_email(db, email)
        logger.info(f"post_user_email_send_api: {db_user}")

        # 이전에 사용한 db_check를 삭제
        clean_checkers(db, email)

        logger.info(f"post_user_email_send_api: new user")
        db_checkout = make_user_check(email=email, checker=checker)
        db.add(db_checkout)
        db.commit()

        user_json["checker"] = checker

        checker_msg = encoded_data_to_jwt(user_json)

        send_mail(mail_config, email, checker_msg)

        logger.info(f"post_user_email_send_api db_check: {email}, {checker}")
        return UserSendMsg(code=200, content="Send email", email=email, checker=checker)

    finally:
        logger.info(f">>> post_user_email_send_api end")


@router.post("/email_auth")
async def post_user_email_resend_api(
    data: UserEmailRequest, db: SessionLocal = Depends(get_db)
):
    """
    이메일 재전송

    :param data: UserEmailRequest 모델
    :param db: db session
    :return: UserSendMsg 모델
    """
    logger.info(f">>> post_user_email_resend_api start: {data}")

    try:
        email = data.email

        # 이전에 사용한 db_check를 삭제
        clean_checkers(db, email)

        db_user = get_user_by_email(db, email)
        if db_user is None:
            raise UserNotExistsException
        if db_user.status == 0:
            raise UserNotExistsException

        checker = generate_hash()
        db_checker = make_user_check(email=email, checker=checker)
        db.add(db_checker)
        db.commit()

        user_json = {
            "email": email,
            "uid": db_user.uid,
            "created_at": db_user.created_at.isoformat(),
            "checker": checker,
        }

        checker_msg = encoded_data_to_jwt(user_json)

        send_mail(mail_config, email, checker_msg)

        logger.info(f"post_user_email_resend_api db_check: {email}, {checker}")
        return UserSendMsg(
            code=200, content="Auth email send", email=email, checker=checker
        )

    finally:
        logger.info(f">>> post_user_email_resend_api end")


@router.get(
    "/email_confirm",
)
async def email_confirm_user_api(
    email: str, checker: str, db: SessionLocal = Depends(get_db)
):
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

        decoded_data = decode_data_from_jwt(checker)
        logger.info(f"email_confirm_user_api decoded_data: {decoded_data}")
        check_key = decoded_data["checker"]

        db_check = get_user_check_by_email(db, email)
        if db_check is None:
            raise UserCheckerNotExistException

        if db_check.checker == check_key:

            # checker 정보의 verify를 Y로 변경
            db_check.verified = "Y"
            db.merge(db_check)
            db.commit()
            logger.info(f"email_confirm_user_api db_check: {db_check}")

            db_user = get_user_by_email(db, email)
            db_user.email_verified = "Y"
            db.merge(db_user)
            db.commit()

            logger.info(f"email_confirm_user_api: {email} confirm success")

            msg = {"code": 200, "content": "Email confirm success"}
            logger.info(f"email_confirm_user_api msg: {msg}")
            return HTMLResponse(content=html_ok_content, status_code=200)

        else:
            raise UserCheckerNotMatchException

    finally:
        logger.info(f">>> email_confirm_user_api end")


@router.post(
    "/email_confirm_check",
)
async def email_confirm_check_user_api(
    data: UserEmailRequest, db: SessionLocal = Depends(get_db)
):
    """
    이메일 인증 확인

    :param data: UserEmailRequest 모델
    :param db: db session
    :return:
    """
    logger.info(f">>> email_confirm_check_user_api: {data}")

    try:
        email = data.email
        db_user = get_user_by_email(db, email)
        if db_user is None:
            raise UserNotExistsException

        if db_user.email_verified == "Y":
            msg = {"code": 200, "content": "Email confirmed"}
            logger.info(f"email_confirm_check_user_api msg: {msg}")
            return JSONResponse(status_code=200, content=msg)
        else:
            raise UserEmailNotConfirmException

    finally:
        logger.info(f">>> email_confirm_check_user_api end")


@router.post("/email_auth_confirm")
async def post_user_email_auth_confirm_api(
    data: UserEmailRequest, db: SessionLocal = Depends(get_db)
):
    """
    이메일 인증 확인

    :param data: UserEmailRequest 모델
    :param db: db session
    :return:
    """
    logger.info(f">>> post_user_email_auth_confirm_api: {data}")

    try:
        email = data.email
        db_check = get_user_check_by_email(db, email)
        if db_check is None:
            raise UserCheckerNotExistException

        if db_check.verified == "Y":
            msg = {"code": 200, "content": "Email confirmed"}
            logger.info(f"post_user_email_auth_confirm_api msg: {msg}")
            return JSONResponse(status_code=200, content=msg)
        else:
            raise UserEmailNotConfirmException

    finally:
        logger.info(f">>> post_user_email_auth_confirm_api end")


@router.post("/update")
async def update_user_by_email_api(
    req: UserUpdateRequest, db: SessionLocal = Depends(get_db)
):
    """
    사용자 업데이트

    :param req: UserCreateRequest 모델
    :param db: db session
    :return:
    """
    logger.info(f">>> update_user_by_email_api: {req}")

    try:
        email = req.email
        checker = req.checker
        name = req.name

        db_checker = get_user_check_by_email(db, email)
        if db_checker is None:
            raise UserCheckerNotExistException

        if db_checker.checker != checker:
            raise UserCheckerNotMatchException

        if db_checker.verified != "Y":
            raise UserEmailNotConfirmException

        db.merge(db_checker)
        db.flush()

        db_user = get_user_by_email(db, email)
        if db_user is None:
            raise UserNotExistsException

        if req.name is not None:
            db_user.name = name
        if req.password is not None:
            db_user.hashed_pwd = get_password_hash(req.password)
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
async def delete_user_by_email_api(
    req: UserEmailRequest, db: SessionLocal = Depends(get_db)
):
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
            raise UserNotExistsException

        db.delete(db_user)
        db.commit()

        logger.info(f"delete_user_by_email_api: {email} delete success")
        return {"message": "delete success"}

    finally:
        logger.info(f">>> delete_user_by_email_api end")


@router.post(
    "/refresh",
)
async def refresh_token_api(
    db: SessionLocal = Depends(get_db), token: str = Depends(oauth2_scheme)
):
    logger.info(f">>> refresh_token_api: {token}")
    try:
        info = get_info_from_refresh_token(token)

        email = info.get("email")
        refresh = info.get("refresh")

        if email is None:
            raise UserEmailNotExistException

        if refresh is None:
            raise JWTRefreshTokenNotExistException

        user = get_user_by_email(db, email)
        if user is None:
            raise UserNotExistsException

        access_token = access_token_make_function(email)

        token_msg = {"access_token": access_token, "token_type": "bearer"}
        logger.info(f"refresh_token_api: {token_msg}")
        return AccessTokenMsg(**token_msg)

    finally:
        logger.info(f">>> refresh_token_api end")


@router.get("/all_users_info")
async def get_user_info(db: SessionLocal = Depends(get_db)):
    """
    사용자 정보 조회

    :param db: db session
    :return:
    """
    logger.info(f">>> get_user_info start")

    try:
        db_user_info = get_user_wallets(db)
        logger.info(f"get_user_info: {db_user_info}")
        return db_user_info

    finally:
        logger.info(f">>> get_user_info end")


@router.get("/info")
async def get_user_info_by_owner(user: User = Depends(get_current_user)):
    """
    사용자 정보 조회

    :param user: User 모델
    :return:
    """
    logger.info(f">>> get_user_info_by_owner start")

    db_user, db = user
    try:
        db_user_info = get_user_info_by_uid(db, db_user.uid)
        user_dict = db_user_info.__dict__.copy()
        user_dict.pop("_sa_instance_state")
        user_dict.pop("uid")
        user_dict.pop("hashed_pwd")
        user_dict.pop("wid")
        user_dict.pop("wallet_created_at")
        user_dict.pop("wallet_updated_at")
        logger.info(f"get_user_info_by_owner: {user_dict}")
        return user_dict

    finally:
        logger.info(f">>> get_user_info_by_owner end")


@router.post("/pw_change")
async def post_user_pw_change_api(
    req: UserPwChangeRequest, user: User = Depends(get_current_user)
):
    """
    사용자 비밀번호 변경

    :param req: UserUpdateRequest 모델
    :param user: User 모델
    :return:
    """
    logger.info(f">>> post_user_pw_change_api: {req}")

    try:
        db_user, db = user

        prev_password = req.prev_password
        password = req.password
        email = db_user.email

        if not verify_password(prev_password, db_user.hashed_pwd):
            raise UserPasswordNotMatchException

        db_user.hashed_pwd = get_password_hash(password)

        db.merge(db_user)
        db.commit()

        logger.info(f"post_user_pw_change_api: {email} password change success")
        return {"message": "password change success"}

    finally:
        logger.info(f">>> post_user_pw_change_api end")
