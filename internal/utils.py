import hashlib
import secrets
import smtplib
import traceback
from datetime import time
from email.message import EmailMessage
from functools import wraps

from fastapi import HTTPException
from jwt.exceptions import ExpiredSignatureError
from passlib.context import CryptContext
from sqlalchemy import inspect
from sqlalchemy.exc import SQLAlchemyError
from fastapi.responses import JSONResponse

from internal.app_config import platform_env
from internal.html_msg import make_url, auth_msg
from internal.log import logger

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str):
    return pwd_context.hash(password)


# Verify a password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def generate_hash() -> str:
    """
    256바이트 크기의 hash 코드를 작성함.
    반환되는 문자열의 사이즈는 64바이트이다.
    :return: 256 bytes hash code
    """
    current_time = str(time()).encode("utf-8")
    random_bytes = secrets.token_bytes(16)
    hashed_bytes = hashlib.sha256(current_time + random_bytes).hexdigest()
    if platform_env["test_mode"]:
        substring = hashed_bytes[4:64]
        hashed_bytes = platform_env["test_hash"] + substring

    return hashed_bytes


def exception_handler(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)

        except SQLAlchemyError as _:
            # SQLAlchemy의 일반적인 오류 처리
            logger.error(f"Database error: {traceback.format_exc()}")
            # FastAPI의 HTTPException을 사용하여 클라이언트에 적절한 HTTP 상태 코드와 메시지 전달
            raise SQLAlchemyError(status_code=500, detail="Database error, please try again later.")

        except Exception as _:
            # 그 외 모든 예외 처리
            logger.error(f"An unexpected error occurred: {traceback.format_exc()}")
            # 예상치 못한 오류에 대해 500 상태 코드 반환
            raise Exception()

    return wrapper


def send_mail(mailer, uid, checker):
    logger.debug(f"send_mail: {uid}, {checker}")

    uid_t = uid.replace("+", "%2b")
    msg_link = make_url(mailer["host"], uid_t, checker)
    auth_body = auth_msg(msg_link)
    title = "Confirm mail for email"

    auth_email_send(mailer, uid, title, auth_body)


def auth_email_send(mailer, receiver, title, content):
    logger.info('>>> auth_email_send start')
    logger.info(f'receiver: {receiver}')
    logger.info(f'title: {title}')
    logger.info(f'content: {content}')

    s = smtplib.SMTP("smtp.gmail.com", 587)
    s.starttls()
    s.login(mailer["sender"], mailer["password"])

    # message to be sent
    msg = EmailMessage()
    msg["From"] = mailer["sender"]
    msg["To"] = receiver
    msg["Subject"] = title

    # 텍스트와 HTML 버전 모두 추가
    msg.set_content("이 메일을 보려면 HTML을 지원하는 이메일 클라이언트가 필요합니다.")
    msg.add_alternative(content, subtype="html")

    s.send_message(msg)
    s.quit()


def model_to_dict(model):
    """모델 인스턴스를 딕셔너리로 변환합니다."""
    return {c.key: getattr(model, c.key)
            for c in inspect(model).mapper.column_attrs}
