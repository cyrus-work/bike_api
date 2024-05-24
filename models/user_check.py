from sqlalchemy import Column, String, DateTime, func

from internal.log import logger
from internal.mysql_db import Base, SessionLocal
from internal.utils import exception_handler, generate_hash


class UserCheck(Base):
    """
    UserCheck Model
    사용자의 이메일 인증을 확인한다.

    id: user id
    checker: checker
    created_at: created time
    """

    __tablename__ = "user_check"

    cid = Column(
        String(64, collation="latin1_swedish_ci"), primary_key=True, index=True
    )
    email = Column(String(120, collation="latin1_swedish_ci"))
    checker = Column(String(64))
    verified = Column(String(1), default="N", comment="Y: 확인됨, N: 미인증")
    created_at = Column(DateTime, default=func.now())

    def __repr__(self):
        return (
            f"UserCheck(cid={self.cid}, email={self.email}, checker={self.checker}, "
            f"verified={self.verified}, created_at={self.created_at})"
        )


def is_cid_duplicate(cid: str) -> bool:
    """
    Check if wid is duplicate

    :param cid: cid 값
    :return: bool
        True if duplicate, False if not duplicate
    """
    db = SessionLocal()
    return db.query(UserCheck).filter_by(cid=cid).first()


@exception_handler
def make_user_check(email: str, checker: str) -> UserCheck:
    """
    사용자의 이메일 인증을 확인한다.

    :param email: email value
    :param checker: checker
    :return: UserCheck
    """
    while True:
        cid = generate_hash()
        # cid가 중복되지 않는지 확인
        if not is_cid_duplicate(cid):
            break

    return UserCheck(cid=cid, email=email, checker=checker)


@exception_handler
def get_user_check_by_email(db: SessionLocal, email: str):
    """
    Get user check by email

    :param db: database session
    :param email: email value
    :return: UserCheck
    """
    return db.query(UserCheck).filter_by(email=email).order_by(UserCheck.created_at.desc()).first()


@exception_handler
def get_user_checks_by_email(db: SessionLocal, email: str) -> list[UserCheck]:
    """
    Get user checks by email

    :param db: database session
    :param email: email value
    :return: list[UserCheck]
    """
    return db.query(UserCheck).filter_by(email=email).all()


@exception_handler
def update_user_check_verified(db: SessionLocal, email: str):
    """
    Update user check verified

    :param db: database session
    :param email: email value
    """
    db.query(UserCheck).filter_by(email=email).update({"verified": "Y"})
    return True


@exception_handler
def clean_checkers(db: SessionLocal, email: str):
    db_check = get_user_checks_by_email(db, email)
    for item in db_check:
        db.delete(item)
    db.commit()
