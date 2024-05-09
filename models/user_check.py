import traceback

from sqlalchemy import Column, String, DateTime, func, ForeignKey

from internal.log import logger
from internal.mysql_db import Base, SessionLocal
from internal.utils import generate_hash, exception_handler


class UserCheck(Base):
    """
    UserCheck Model
    사용자의 이메일 인증을 확인한다.

    id: user id
    checker: checker
    created_at: created time
    """

    __tablename__ = "user_check"

    id = Column(String(64, collation="latin1_swedish_ci"), ForeignKey("users.uid", ondelete="CASCADE"),
                primary_key=True, index=True)
    checker = Column(String(64))
    created_at = Column(DateTime, default=func.now())

    def __repr__(self):
        return f"UserCheck(id={self.id}, checker={self.checker})"


@exception_handler
def make_user_check(id: str, checker: str) -> UserCheck:
    """
    사용자의 이메일 인증을 확인한다.

    :param id: user id
    :param checker: checker
    :return: UserCheck
    """
    return UserCheck(id=id, checker=checker)


@exception_handler
def get_user_check_by_id(db: SessionLocal, id: str) -> UserCheck:
    """
    사용자의 이메일 인증을 확인한다.

    :param db: SessionLocal
    :param id: user id
    :return: checker
    """
    logger.info("=== get_user_check_by_id start.")
    try:
        return db.query(UserCheck).filter(UserCheck.id == id).first()

    except Exception as _:
        logger.error(f"=== get_user_check_by_id error: {traceback.format_exc()}")

    finally:
        logger.info("=== get_user_check_by_id end.")
