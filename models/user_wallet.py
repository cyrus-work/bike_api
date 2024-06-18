from sqlalchemy import Column, Integer, String, DateTime, CHAR

from internal.mysql_db import Base, SessionLocal
from internal.utils import exception_handler


class UserWalletView(Base):
    __tablename__ = "user_wallets_view"

    uid = Column(String(64, collation="latin1_swedish_ci"), primary_key=True)
    type = Column(Integer)
    name = Column(String(100, collation="utf8mb4_unicode_ci"))
    email = Column(String(120, collation="latin1_swedish_ci"))
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
            f"email_verified={self.email_verified}, agreement1={self.agreement1}, agreement2={self.agreement2}, "
            f"agreement3={self.agreement3}, status={self.status}, level={self.level}, "
            f"user_created_at={self.user_created_at}, user_updated_at={self.user_updated_at}, "
            f"wid={self.wid}, address={self.address}, enable={self.enable}, "
            f"wallet_created_at={self.wallet_created_at}, wallet_updated_at={self.wallet_updated_at})"
        )


@exception_handler
def get_user_wallets(session, offset=0, limit=50):
    """
    Get user wallets

    :param session: session
    :return: UserWalletView
    """
    return session.query(UserWalletView).offset(offset).limit(limit).all()


@exception_handler
def get_user_info_by_uid(session, uid):
    """
    Get user info by uid

    :param session: session
    :param uid: uid
    :return: User
    """
    return session.query(UserWalletView).filter_by(uid=uid).first()


@exception_handler
def get_user_info_by_email_verified(session, email_verified):
    """
    Get user info by email_verified

    :param session: session
    :param email_verified: email_verified
    :return: User
    """
    return session.query(UserWalletView).filter_by(email_verified=email_verified).all()


@exception_handler
def get_user_info_by_wallet_exist(db: SessionLocal, wallet_exist: bool):
    """
    Get user info by wallet_exist
    if True is not None, if False is None

    :param db: SessionLocal: session
    :param wallet_exist: wallet_exist
    :return: User
    """
    if wallet_exist:
        return (
            db.query(UserWalletView)
            .filter(UserWalletView.address.isnot(None))
            .order_by(UserWalletView.user_created_at.desc())
            .all()
        )
    else:
        return (
            db.query(UserWalletView)
            .filter(UserWalletView.address.is_(None))
            .order_by(UserWalletView.user_created_at.desc())
            .all()
        )


@exception_handler
def get_user_info_by_wallet(db, wallet):
    """
    Get user info by wallet

    :param db: SessionLocal: session
    :param wallet: wallet
    :return: User
    """
    return db.query(UserWalletView).filter_by(address=wallet).first()


@exception_handler
def get_counts_of_user_wallets(session):
    """
    Get counts of user wallets

    :param session: session
    :return: int
    """
    return session.query(UserWalletView).count()
