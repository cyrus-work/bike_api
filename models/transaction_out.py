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
    """
    Make transaction out

    :param tid: transaction id
    :param wallet: wallet address
    :param amount: 요청된 코인 수량
    :param operating_fee: 운영 수수료
    :param txn_hash: transaction hash
    :param msg: message
    :param status: status
            0: 출금 요청
            1: 전송 요청
            2: 전송 요청 진행 - transaction hash 발급
            3: 전송 완료
            4: 운영 수수료 전송 요청 진행 - transaction hash 발급
            5: 운영 수수료 전송 완료
            7: 전송 요청 실패 - transaction hash 발급 실패, 전송 실패
    :param request_at: 전송 요청 시간
    :param operating_at: 전송 처리 시간
    :param tx_completed_at: 전송 완료 시간
    :param result_at: 전송 처리 시간
    :param created_at: 생성 시간
    :param updated_at: 수정 시간
    :return: TransactionHistory
    """

    __tablename__ = "transaction_out"
    __table_args__ = {"comment": "트랜젝션 테이블"}

    tid = Column(String(64, collation="latin1_swedish_ci"), primary_key=True)
    wallet = Column(String(42, collation="latin1_swedish_ci"), nullable=False)
    amount = Column(DECIMAL(36, 18), nullable=False, default=0)
    operating_fee = Column(DECIMAL(36, 18), nullable=False, default=0)
    txn_hash = Column(CHAR(66, collation="latin1_swedish_ci"))
    msg = Column(String(255), nullable=True, default=None)
    status = Column(SmallInteger, nullable=False, default=0)
    request_at = Column(DateTime, nullable=True, default=None)  # 전송 요청 시간
    operating_at = Column(DateTime, nullable=True, default=None)  # 전송 처리 시간
    tx_completed_at = Column(DateTime, nullable=True, default=None)
    result_at = Column(DateTime, nullable=True, default=None)  # 전송 결과 시간
    created_at = Column(DateTime, nullable=False, default=datetime.now())
    updated_at = Column(DateTime, onupdate=datetime.now())

    def __repr__(self):
        return (
            f"<TransactionOut(tid={self.tid}, wallet={self.wallet}, amount={self.amount}, "
            f"operating_fee={self.operating_fee}, txn_hash={self.txn_hash}, msg={self.msg}, "
            f"status={self.status}, request_at={self.request_at}, operating_at={self.operating_at}, "
            f"tx_completed_at={self.tx_completed_at}, result_at={self.result_at}, "
            f"created_at={self.created_at}, updated_at={self.updated_at})>"
        )


def make_transaction_out(
    wallet: str,
    amount: float = 0,
) -> TransactionOut:
    """
    Make transaction out

    :param wallet: wallet value
    :param amount: coin value
    :return: TransactionOut
    """

    tid = generate_hash()
    operating_fee = amount * 0.2
    return TransactionOut(
        tid=tid,
        wallet=wallet,
        amount=amount,
        operating_fee=operating_fee,
        status=0,
        request_at=datetime.now(),
    )


def get_txn_out_by_txn_hash_is_null(db):
    return db.query(TransactionOut).filter_by(status=0, txn_hash=None).all()


def get_txn_out_by_status_not_clear(db):
    return db.query(TransactionOut).filter(TransactionOut.status != 5).all()


def get_txn_out_by_wallet(db, wallet):
    return db.query(TransactionOut).filter_by(wallet=wallet).all()
