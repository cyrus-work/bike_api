from datetime import datetime

from sqlalchemy import (
    Column,
    String,
    DECIMAL,
    DateTime,
    SmallInteger,
    CHAR,
)

from internal.mysql_db import Base
from internal.utils import generate_hash


class TransactionOut(Base):
    __tablename__ = "transaction_out"
    __table_args__ = {"comment": "트랜젝션 테이블"}

    tid = Column(String(64, collation="latin1_swedish_ci"), primary_key=True)
    wallet = Column(String(128), nullable=False)
    coin = Column(DECIMAL(36, 18), nullable=False, default=0)
    operating_fee = Column(DECIMAL(36, 18), nullable=False, default=0)
    transaction_hash = Column(
        CHAR(64, collation="latin1_swedish_ci"), nullable=True, default=None
    )
    msg = Column(String(255), nullable=True, default=None)
    tx_completed_at = Column(DateTime, nullable=True, default=None)
    operating_at = Column(DateTime, nullable=True, default=datetime.now())
    operating_history_id = Column(
        String(64, collation="latin1_swedish_ci"), nullable=True, default=None
    )
    status = Column(SmallInteger, nullable=False, default=0)
    deposit_at = Column(DateTime, nullable=True, default=None)
    result_at = Column(DateTime, nullable=True, default=None)
    created_at = Column(DateTime, nullable=False, default=datetime.now())
    updated_at = Column(DateTime, nullable=False, onupdate=datetime.now())

    def __repr__(self):
        return (
            f"<TransactionHistory(tid={self.tid}, wallet={self.wallet}, coin={self.coin}, "
            f"operating_fee={self.operating_fee}, deposit_at={self.deposit_at}, "
            f"result_at={self.result_at}, transaction_hash={self.transaction_hash}, "
            f"msg={self.msg}, tx_completed_at={self.tx_completed_at}, operating_at={self.operating_at}, "
            f"operating_history_id={self.operating_history_id}, status={self.status}, "
            f"created_at={self.created_at}, updated_at={self.updated_at})>"
        )


def make_transaction_out(
    wallet: str,
    coin: float,
) -> TransactionOut:
    """
    Make transaction out

    :param wallet: wallet value
    :param coin: coin value
    :return: TransactionOut
    """

    tid = generate_hash()
    operating_fee = coin * 0.2
    return TransactionOut(
        tid=tid,
        wallet=wallet,
        coin=coin,
        operating_fee=operating_fee,
        status=0,
    )
