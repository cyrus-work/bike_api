from datetime import datetime
from typing import Tuple

from sqlalchemy import Column, Integer, String, DateTime, CHAR

from internal.log import logger
from internal.mysql_db import Base, SessionLocal
from internal.utils import get_password_hash, generate_hash, exception_handler


class User(Base):
    __tablename__ = "users"

    uid = Column(String(64, collation="latin1_swedish_ci"), primary_key=True)
    type = Column(Integer, default=0)
    name = Column(String(100, collation="utf8mb4_unicode_ci"))
    email = Column(String(120, collation="latin1_swedish_ci"), unique=True)
    hashed_pwd = Column(String(60, collation="latin1_swedish_ci"))
    email_verified = Column(CHAR(1), default="N", comment="Y: 인증됨, N: 미인증")
    agreement1 = Column(CHAR(1), default="N")
    agreement2 = Column(CHAR(1), default="N")
    agreement3 = Column(CHAR(1), default="N")
    status = Column(Integer, default=0, comment="0: 가입대기, 1: 가입, 2: 탈퇴")
    level = Column(Integer, default=0, comment="0: disable, 1: 일반유저, 9: 관리자")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return (
            f"User(uid={self.uid}, type={self.type}, name={self.name}, email={self.email}, "
            f"hashed_pwd={self.hashed_pwd}, email_verified={self.email_verified}, "
            f"agreement1={self.agreement1}, agreement2={self.agreement2}, agreement3={self.agreement3}, "
            f"status={self.status}, created_at={self.created_at}, updated_at={self.updated_at})"
        )


def is_uid_duplicate(uid: str) -> bool:
    """
    Check if wid is duplicate

    :param uid: uid 값
    :return: bool
        True if duplicate, False if not duplicate
    """
    db = SessionLocal()
    return db.query(User).filter_by(uid=uid).first()


@exception_handler
def make_user(
    name: str or None, email: str, password: str or None, email_verified: str = "N"
) -> User:
    """
    Make user

    :param name: name value
    :param email: email value
    :param password: password value
    :param email_verified: email_verified value
    :return: User
    """
    while True:
        uid = generate_hash()
        # uid가 중복되지 않는지 확인
        if not is_uid_duplicate(uid):
            break

    if password is not None:
        hashed_pwd = get_password_hash(password)
    else:
        hashed_pwd = None
    return User(
        uid=uid,
        name=name,
        email=email,
        hashed_pwd=hashed_pwd,
        email_verified=email_verified,
    )


"""
database operations
"""


@exception_handler
def get_user_by_email(db: SessionLocal, email: str) -> User:
    """
    email로 사용자를 조회한다.

    :param db: db session
    :param email: user email
    :return: user
    """
    return db.query(User).filter(User.email == email).first()


@exception_handler
def get_user_exist_by_email(db: SessionLocal, email: str):
    """
    email로 사용자가 존재하는지 확인한다.

    :param db: db session
    :param email: user email
    :return: bool
    """
    return (
        db.query(User).filter(User.email == email, User.email_verified == "Y").first()
    )


@exception_handler
def get_users(db: SessionLocal, offset: int = 0, limit: int = 50) -> User:
    """
    사용자의 이메일 인증을 확인한다.

    :param db: SessionLocal
    :param offset: offset
    :param limit: limit
    :return: checker
    """
    logger.info(">>> get_user_check_by_id start.")
    try:
        return (
            db.query(User)
            .order_by(User.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    finally:
        logger.info(">>> get_user_check_by_id end.")


@exception_handler
def delete_user_by_uid(db: SessionLocal, uid: str) -> None:
    """
    사용자를 삭제한다.

    :param db: SessionLocal
    :param uid: uid
    """
    logger.info(">>> delete_user_by_uid start.")
    try:
        user = db.query(User).filter(User.uid == uid).first()
        db.delete(user)
        db.commit()

    finally:
        logger.info(">>> delete_user_by_uid end.")


@exception_handler
def delete_user_by_email(db: SessionLocal, email: str) -> None:
    """
    사용자를 삭제한다.

    :param db: SessionLocal
    :param email: email
    """
    logger.info(">>> delete_user_by_email start.")
    try:
        user = db.query(User).filter(User.email == email).first()
        db.delete(user)
        db.commit()

    finally:
        logger.info(">>> delete_user_by_email end.")


@exception_handler
def update_user_email_verified(db: SessionLocal, email: str) -> None:
    """
    사용자의 이메일 인증을 확인한다.

    :param db: SessionLocal
    :param email: email
    """
    logger.info(">>> update_user_email_verified start.")
    try:
        user = db.query(User).filter(User.email == email).first()
        user.email_verified = "Y"
        db.commit()

    finally:
        logger.info(">>> update_user_email_verified end.")


@exception_handler
def update_user_status(db: SessionLocal, uid: str, status: int) -> None:
    """
    사용자의 상태를 변경한다.

    :param db: SessionLocal
    :param uid: uid
    :param status: status
    """
    logger.info(">>> update_user_status start.")
    try:
        user = db.query(User).filter(User.uid == uid).first()
        user.status = status
        db.merge(user)
        db.commit()

    finally:
        logger.info(">>> update_user_status end.")


def update_user_agreement(
    db: SessionLocal, uid: str, agreement1: str, agreement2: str, agreement3: str
) -> None:
    """
    사용자의 약관 동의를 변경한다.

    :param db: SessionLocal
    :param uid: uid
    :param agreement1: agreement1
    :param agreement2: agreement2
    :param agreement3: agreement3
    """
    logger.info(">>> update_user_agreement start.")
    try:
        user = db.query(User).filter(User.uid == uid).first()
        user.agreement1 = agreement1
        user.agreement2 = agreement2
        user.agreement3 = agreement3
        db.commit()

    finally:
        logger.info(">>> update_user_agreement end.")


@exception_handler
def get_user_agreement_by_email(db: SessionLocal, email: str) -> Tuple[str, str, str]:
    """
    사용자의 약관 동의를 조회한다.

    :param db: SessionLocal
    :param email: email
    :return: Tuple[str, str, str]
    """
    logger.info(">>> get_user_agreement_by_email start.")
    try:
        user = db.query(User).filter(User.email == email).first()
        return user.agreement1, user.agreement2, user.agreement3

    finally:
        logger.info(">>> get_user_agreement_by_email end.")


@exception_handler
def get_user_status_by_email(db: SessionLocal, email: str) -> int:
    """
    사용자의 상태를 조회한다.

    :param db: SessionLocal
    :param email: email
    :return: int
    """
    logger.info(">>> get_user_status_by_email start.")
    try:
        user = db.query(User).filter(User.email == email).first()
        return user.status

    finally:
        logger.info(">>> get_user_status_by_email end.")
