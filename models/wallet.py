from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey, UniqueConstraint

from internal.mysql_db import Base, SessionLocal
from internal.utils import generate_hash, exception_handler


class Wallet(Base):
    __tablename__ = 'wallets'

    wid = Column(String(64, collation="latin1_swedish_ci"), primary_key=True)
    owner_id = Column(String(64, collation="latin1_swedish_ci"), ForeignKey('users.uid'))
    address = Column(String(42, collation="latin1_swedish_ci"), index=True)
    enable = Column(String(1, collation="latin1_swedish_ci"), default='Y')
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    __table_args__ = (
        UniqueConstraint("owner_id", "address", name="uq_audition_video"),
    )

    def __repr__(self):
        return (
            f"Wallet(wid={self.wid}, address={self.address}, enable={self.enable}, "
            f"created_at={self.created_at}, updated_at={self.updated_at})"
        )


def is_wid_duplicate(wid: str) -> bool:
    """
    Check if wid is duplicate

    :param wid: wid 값
    :return: bool
        True if duplicate, False if not duplicate
    """
    db = SessionLocal()
    return db.query(Wallet).filter_by(wid=wid).first()


@exception_handler
def make_wallet(owner_id: str, address: str) -> Wallet:
    """
    Make wallet

    :param owner_id: owner_id value
    :param address: address value
    :return: Wallet
    """
    while True:
        wid = generate_hash()
        # wid가 중복되지 않는지 확인
        if not is_wid_duplicate(wid):
            break
    return Wallet(wid=wid, owner_id=owner_id, address=address)


@exception_handler
def get_wallet_by_address(db: SessionLocal, address: str) -> Wallet:
    """
    Get wallet by address

    :param db: SessionLocal
    :param address: address value
    :return: Wallet
    """
    return db.query(Wallet).filter(Wallet.address == address).first()


@exception_handler
def get_wallet_by_id(db: SessionLocal, wid: str) -> Wallet:
    """
    Get wallet by wid

    :param db: SessionLocal
    :param wid: wid value
    :return: Wallet
    """
    return db.query(Wallet).filter(Wallet.wid == wid).first()


@exception_handler
def get_wallet_by_owner_id(db: SessionLocal, owner_id: str) -> Wallet:
    """
    Get wallet by owner_id

    :param db: SessionLocal
    :param owner_id: owner_id value
    :return: Wallet
    """
    return db.query(Wallet).filter(Wallet.owner_id == owner_id).first()


@exception_handler
def get_wallets(db: SessionLocal, offset: int = 0, limit: int = 50) -> Wallet:
    """
    Get wallets

    :param db: SessionLocal
    :param offset: offset value
    :param limit: limit value
    :return: Wallet
    """
    return db.query(Wallet).order_by(Wallet.created_at.desc()).offset(offset).limit(limit).all()


@exception_handler
def update_wallet(db: SessionLocal, wid: str, address: str, enable: str) -> Wallet:
    """
    Update wallet

    :param db: SessionLocal
    :param wid: wid value
    :param address: address value
    :param enable: enable value
    :return: Wallet
    """
    wallet = db.query(Wallet).filter(Wallet.wid == wid).first()
    wallet.address = address
    wallet.enable = enable
    db.commit()
    return wallet


@exception_handler
def delete_wallet(db: SessionLocal, wid: str) -> Wallet:
    """
    Delete wallet

    :param db: SessionLocal
    :param wid: wid value
    :return: Wallet
    """
    wallet = db.query(Wallet).filter(Wallet.wid == wid).first()
    db.delete(wallet)
    db.commit()
    return wallet
