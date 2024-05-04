from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey, UniqueConstraint

from internal.mysql_db import Base, SessionLocal
from internal.utils import generate_hash


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


def make_wallet(owner_id: str, address: str) -> Wallet:
    uid = generate_hash()
    return Wallet(wid=uid, owner_id=owner_id, address=address)


def get_wallet_by_address(db: SessionLocal, address: str) -> Wallet:
    return db.query(Wallet).filter(Wallet.address == address).first()


def get_wallet_by_id(db: SessionLocal, wid: str) -> Wallet:
    return db.query(Wallet).filter(Wallet.wid == wid).first()


def get_wallet_by_owner_id(db: SessionLocal, owner_id: str) -> Wallet:
    return db.query(Wallet).filter(Wallet.owner_id == owner_id).first()


def get_wallets(db: SessionLocal, offset: int = 0, limit: int = 50) -> Wallet:
    return db.query(Wallet).order_by(Wallet.created_at.desc()).offset(offset).limit(limit).all()


def update_wallet(db: SessionLocal, wid: str, address: str, enable: str) -> Wallet:
    wallet = db.query(Wallet).filter(Wallet.wid == wid).first()
    wallet.address = address
    wallet.enable = enable
    db.commit()
    return wallet


def delete_wallet(db: SessionLocal, wid: str) -> Wallet:
    wallet = db.query(Wallet).filter(Wallet.wid == wid).first()
    db.delete(wallet)
    db.commit()
    return wallet
