from sqlalchemy import Column, Integer, String, DateTime, CHAR

from internal.mysql_db import Base
from internal.utils import exception_handler
from models.user import User


class UserWalletView(Base):
    __tablename__ = "user_wallets_view"

    uid = Column(String(64, collation="latin1_swedish_ci"), primary_key=True)
    type = Column(Integer)
    name = Column(String(100, collation="utf8mb4_unicode_ci"))
    email = Column(String(120, collation="latin1_swedish_ci"))
    hashed_pwd = Column(String(60, collation="latin1_swedish_ci"))
    email_verified = Column(CHAR(1))
    agreement1 = Column(CHAR(1))
    agreement2 = Column(CHAR(1))
    agreement3 = Column(CHAR(1))
    status = Column(Integer)
    level = Column(Integer)
    user_created_at = Column(DateTime)
    user_updated_at = Column(DateTime)
    wid = Column(String(64, collation="latin1_swedish_ci"))
    address = Column(String(42, collation="latin1_swedish_ci"))
    enable = Column(CHAR(1))
    wallet_created_at = Column(DateTime)
    wallet_updated_at = Column(DateTime)

    def __repr__(self):
        return (
            f"UserWalletView(uid={self.uid}, type={self.type}, name={self.name}, email={self.email}, "
            f"hashed_pwd={self.hashed_pwd}, email_verified={self.email_verified}, "
            f"agreement1={self.agreement1}, agreement2={self.agreement2}, agreement3={self.agreement3}, "
            f"status={self.status}, level={self.level}, user_created_at={self.user_created_at}, "
            f"user_updated_at={self.user_updated_at}, wid={self.wid}, address={self.address}, "
            f"enable={self.enable}, wallet_created_at={self.wallet_created_at}, wallet_updated_at={self.wallet_updated_at})"
        )


@exception_handler
def get_user_wallets(session):
    """
    Get user wallets

    :param session: session
    :return: UserWalletView
    """
    return session.query(UserWalletView).all()


@exception_handler
def get_user_info_by_uid(session, uid):
    """
    Get user info by uid

    :param session: session
    :param uid: uid
    :return: User
    """
    return session.query(User).filter_by(uid=uid).first()
