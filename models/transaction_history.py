from datetime import datetime

from sqlalchemy import Column, DateTime, String, ForeignKey, Float, DECIMAL, Integer, SmallInteger
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

from internal.mysql_db import Base, SessionLocal
from internal.utils import generate_hash, exception_handler


class TransactionHistory(Base):
    """
    TransactionHistory Model

    이 테이블은 자전거에서 채굴한 토큰을 사용자에게 지급하는 트랜잭션을 기록합니다.
    플랫폼에서 채굴하여 얻은 토큰을 출금할 경우에 작성되기 때문에 별도의 받는 지갑 주소는 없습니다.

    tid: transaction id (transaction hash)
    wid: wallet id
    amount_req: 요청된 코인 수량
    amount_res: 지급된 코인 수량
    fee_operation: 운영 수수료
    request_at: 요청 시간
    result_at: 전송 처리 시간
    txn_completed_at: 전송 완료 시간
    operation_at: 정산 일시
    txn_hash: transaction hash
    msg: message
    status: status
            0: 출금 요청
            1: 전송 요청
            2: 전송 요청 진행 - transaction hash 발급
            3: 전송 완료
            4: 운영 수수료 전송 요청 진행 - transaction hash 발급
            5: 운영 수수료 전송 완료
            7: 전송 요청 실패 - transaction hash 발급 실패, 전송 실패
    created_at: created time
    updated_at: updated time
    """
    __tablename__ = "transaction_history"

    tid = Column(String(64, collation="latin1_swedish_ci"), primary_key=True, index=True)
    wid = Column(String(64, collation="latin1_swedish_ci"), ForeignKey("wallets.wid"))
    amount_req = Column(DECIMAL(36, 10))
    amount_res = Column(DECIMAL(36, 10))
    fee_operation = Column(Float, index=True)
    deposit_at = Column(DateTime, default=datetime.now)
    result_at = Column(DateTime, default=None)
    txn_completed_at = Column(DateTime, default=None)
    operation_at = Column(DateTime, default=None)
    txn_hash = Column(String(66, collation="latin1_swedish_ci"), index=True)
    msg = Column(String(255, collation="latin1_swedish_ci"))
    status = Column(SmallInteger, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return (
            f"TransactionHistory(tid={self.tid}, wid={self.wid}, request_coin={self.request_coin}, amount_req={self.amount_req}, "
            f"amount_res={self.amount_res}, amount={self.amount}, fee_operation={self.fee_operation}, deposit_at={self.deposit_at}, "
            f"result_at={self.result_at}, txn_completed_at={self.txn_completed_at}, operation_at={self.operation_at}, "
            f"txn_hash={self.txn_hash}, msg={self.msg}, status={self.status})"
        )


def make_transaction_history(wid: str, request_coin: float, amount_req: float, amount_res: float, amount: float,
                             fee_operation: float, txn_hash: str, msg: str, status: int) -> TransactionHistory:
    tid = generate_hash()
    return TransactionHistory(tid=tid, wid=wid, request_coin=request_coin, amount_req=amount_req, amount_res=amount_res,
                              amount=amount, fee_operation=fee_operation, txn_hash=txn_hash, msg=msg, status=status)


@exception_handler
def get_transaction_history(db: SessionLocal, tid: str) -> TransactionHistory:
    return db.query(TransactionHistory).filter_by(tid=tid).first()


@exception_handler
def get_transaction_history_by_txn_hash(db: SessionLocal, txn_hash: str) -> TransactionHistory:
    return db.query(TransactionHistory).filter_by(txn_hash=txn_hash).first()


@exception_handler
def get_transaction_history_by_wallet_id(db: SessionLocal, wid: str, offset: int = 0,
                                         limit: int = 50) -> TransactionHistory:
    return db.query(TransactionHistory).filter_by(wid=wid).offset(offset).limit(limit).all()


@exception_handler
def get_transaction_history_by_txn_completed_at_later_than(db: SessionLocal, txn_completed_at: datetime,
                                                           offset: int = 0, limit: int = 50) -> TransactionHistory:
    return db.query(TransactionHistory).filter(TransactionHistory.txn_completed_at > txn_completed_at).offset(
        offset).limit(limit).all()


@exception_handler
def get_transaction_history_by_txn_completed_at_earlier_than(db: SessionLocal, txn_completed_at: datetime,
                                                             offset: int = 0, limit: int = 50) -> TransactionHistory:
    return db.query(TransactionHistory).filter(TransactionHistory.txn_completed_at < txn_completed_at).offset(
        offset).limit(limit).all()


@exception_handler
def update_transaction_history_by_tid(db: SessionLocal, tid: int, **kwargs) -> TransactionHistory:
    # 데이터베이스에서 TransactionHistory 객체 조회
    transaction_history = db.query(TransactionHistory).filter_by(tid=tid).first()

    # 조회된 객체가 없는 경우 예외 처리
    if transaction_history is None:
        raise NoResultFound(f"No TransactionHistory found with tid={tid}")

    # 전달받은 키워드 인자를 바탕으로 속성 업데이트
    for key, value in kwargs.items():
        if hasattr(transaction_history, key):
            setattr(transaction_history, key, value)
        else:
            raise AttributeError(f"{key} is not a valid attribute of TransactionHistory")

    return transaction_history


@exception_handler
def update_transaction_history_by_txn_hash(db: SessionLocal, txn_hash: str, **kwargs) -> TransactionHistory:
    transaction_history = db.query(TransactionHistory).filter_by(txn_hash=txn_hash).first()

    if transaction_history is None:
        raise NoResultFound(f"No TransactionHistory found with txn_hash={txn_hash}")

    for key, value in kwargs.items():
        if hasattr(transaction_history, key):
            setattr(transaction_history, key, value)
        else:
            raise AttributeError(f"{key} is not a valid attribute of TransactionHistory")

    return transaction_history


@exception_handler
def delete_transaction_history_by_tid(db: SessionLocal, tid: int) -> None:
    transaction_history = db.query(TransactionHistory).filter_by(tid=tid).first()

    if transaction_history is None:
        raise NoResultFound(f"No TransactionHistory found with tid={tid}")

    transaction_history.delete()
