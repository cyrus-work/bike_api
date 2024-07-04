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
from internal.utils import generate_hash, exception_handler


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
    :param result_at: 전송 처리 시간
    :param created_at: 생성 시간
    :param updated_at: 수정 시간
    :return: TransactionHistory
    """

    __tablename__ = "transaction_out"
    __table_args__ = {"comment": "트랜젝션 테이블"}

    tid = Column(String(64, collation="latin1_swedish_ci"), primary_key=True)
    owner_id = Column(String(64, collation="latin1_swedish_ci"), nullable=False)
    wallet = Column(String(42, collation="latin1_swedish_ci"), nullable=False)
    amount = Column(DECIMAL(36, 18), nullable=False, default=0)
    operating_fee = Column(DECIMAL(36, 18), nullable=False, default=0)
    txn_hash = Column(CHAR(66, collation="latin1_swedish_ci"))
    msg = Column(String(255), nullable=True, default=None)
    status = Column(SmallInteger, nullable=False, default=0)
    request_at = Column(DateTime, nullable=True, default=None)  # 전송 요청 시간
    operating_at = Column(DateTime, nullable=True, default=None)  # 전송 처리 시간
    result_at = Column(DateTime, nullable=True, default=None)  # 전송 결과 시간
    created_at = Column(DateTime, nullable=False, default=datetime.now())
    updated_at = Column(DateTime, onupdate=datetime.now())

    def __repr__(self):
        return (
            f"<TransactionOut(tid={self.tid}, owner_id={self.owner_id}, wallet={self.wallet}, "
            f"amount={self.amount}, operating_fee={self.operating_fee}, txn_hash={self.txn_hash}, "
            f"msg={self.msg}, status={self.status}, request_at={self.request_at}, "
            f"operating_at={self.operating_at}, result_at={self.result_at}, "
            f"created_at={self.created_at}, updated_at={self.updated_at})>"
        )


def make_transaction_out(
    wallet: str,
    owner_id: str,
    amount: float = 0,
) -> TransactionOut:
    """
    Make transaction out

    :param wallet: wallet value
    :param owner_id: owner_id value
    :param amount: coin value
    :return: TransactionOut
    """

    tid = generate_hash()
    operating_fee = amount * 0.12
    return TransactionOut(
        tid=tid,
        owner_id=owner_id,
        wallet=wallet,
        amount=amount,
        operating_fee=operating_fee,
        status=0,
        request_at=datetime.now(),
    )


@exception_handler
def get_txn_out_by_txn_hash_is_null(db):
    return db.query(TransactionOut).filter_by(status=0, txn_hash=None).all()


@exception_handler
def get_txn_out_by_status_not_clear(db):
    return (
        db.query(TransactionOut)
        .filter(TransactionOut.status != 5, TransactionOut.status != 0)
        .all()
    )


@exception_handler
def get_txn_out_by_owner_id(db, owner_id, offset=0, limit=50) -> list:
    return (
        db.query(TransactionOut)
        .filter_by(owner_id=owner_id)
        .order_by(TransactionOut.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


@exception_handler
def get_count_txn_out_by_owner_id(db, owner_id):
    return db.query(TransactionOut).filter_by(owner_id=owner_id).count()


@exception_handler
def get_txn_out_by_wallet(db, wallet):
    return db.query(TransactionOut).filter_by(wallet=wallet).all()


@exception_handler
def get_txns_by_owner_id(
    db, owner_id, start_date: datetime.date, end_date: datetime.date
):
    return (
        db.query(TransactionOut)
        .filter(
            TransactionOut.owner_id == owner_id,
            TransactionOut.operating_at >= start_date,
            TransactionOut.operating_at < end_date,
        )
        .all()
    )


@exception_handler
def get_txns_all(db, offset=0, limit=50):
    return (
        db.query(TransactionOut)
        .order_by(TransactionOut.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


@exception_handler
def get_count_txns_all(db):
    return db.query(TransactionOut).count()


@exception_handler
def get_txn_out_by_date(db, start_date, end_date, offset=0, limit=50):
    return (
        db.query(TransactionOut)
        .filter(
            TransactionOut.operating_at >= start_date,
            TransactionOut.operating_at < end_date,
        )
        .order_by(TransactionOut.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


@exception_handler
def get_count_txn_out_by_date(db, start_date, end_date):
    return (
        db.query(TransactionOut)
        .filter(
            TransactionOut.operating_at >= start_date,
            TransactionOut.operating_at < end_date,
        )
        .count()
    )


@exception_handler
def get_txn_out_by_email_and_date(db, email, start_date, end_date, offset=0, limit=50):
    return (
        db.query(TransactionOut)
        .filter(
            TransactionOut.email == email,
            TransactionOut.operating_at >= start_date,
            TransactionOut.operating_at < end_date,
        )
        .order_by(TransactionOut.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


@exception_handler
def get_count_txn_out_by_date(db, start_date, end_date):
    return (
        db.query(TransactionOut)
        .filter(
            TransactionOut.operating_at >= start_date,
            TransactionOut.operating_at < end_date,
        )
        .count()
    )
