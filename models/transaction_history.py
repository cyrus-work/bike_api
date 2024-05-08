from datetime import datetime

from sqlalchemy import Column, DateTime, String, ForeignKey, Float, DECIMAL, SmallInteger
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


def is_tid_duplicate(tid: str) -> bool:
    """
    Check if wid is duplicate

    :param tid: tid 값
    :return: bool
        True if duplicate, False if not duplicate
    """
    db = SessionLocal()
    return db.query(TransactionHistory).filter_by(tid=tid).first()


@exception_handler
def make_transaction_history(wid: str, amount_req: float, amount_res: float, fee_operation: float, deposit_at: datetime,
                             result_at: datetime, txn_completed_at: datetime, operation_at: datetime, txn_hash: str,
                             msg: str, status: int) -> TransactionHistory:
    """
    Make transaction history

    :param wid: wallet id
    :param amount_req: 요청된 코인 수량
    :param amount_res: 지급된 코인 수량
    :param fee_operation: 운영 수수료
    :param deposit_at: 요청 시간
    :param result_at: 전송 처리 시간
    :param txn_completed_at: 전송 완료 시간
    :param operation_at: 정산 일시
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
    :return: TransactionHistory
    """
    while True:
        tid = generate_hash()
        # tid가 중복되지 않는지 확인
        if not is_tid_duplicate(tid):
            break

    return TransactionHistory(tid=tid, wid=wid, amount_req=amount_req, amount_res=amount_res,
                              fee_operation=fee_operation,
                              deposit_at=deposit_at, result_at=result_at, txn_completed_at=txn_completed_at,
                              operation_at=operation_at, txn_hash=txn_hash, msg=msg, status=status)


@exception_handler
def get_transaction_history(db: SessionLocal, tid: str) -> TransactionHistory:
    """
    Get transaction history by tid

    :param db: database session
    :param tid: tid value
    :return: TransactionHistory
    """
    return db.query(TransactionHistory).filter_by(tid=tid).first()


@exception_handler
def get_transaction_history_by_txn_hash(db: SessionLocal, txn_hash: str) -> TransactionHistory:
    """
    Get transaction history by txn_hash

    :param db: database session
    :param txn_hash: txn_hash value
    :return: TransactionHistory
    """
    return db.query(TransactionHistory).filter_by(txn_hash=txn_hash).first()


@exception_handler
def get_transaction_history_by_wallet_id(db: SessionLocal, wid: str, offset: int = 0,
                                         limit: int = 50) -> TransactionHistory:
    """
    Get transaction history by wallet id

    :param db: database session
    :param wid: wallet id
    :param offset: offset value
    :param limit: limit value
    :return: TransactionHistory
    """
    return db.query(TransactionHistory).filter_by(wid=wid).offset(offset).limit(limit).all()


@exception_handler
def get_transaction_history_by_txn_completed_at_later_than(db: SessionLocal, txn_completed_at: datetime,
                                                           offset: int = 0, limit: int = 50) -> TransactionHistory:
    """
    Get transaction history by txn_completed_at later than

    :param db: database session
    :param txn_completed_at: txn_completed_at value
    :param offset: offset value
    :param limit: limit value
    :return: TransactionHistory
    """
    return db.query(TransactionHistory).filter(TransactionHistory.txn_completed_at > txn_completed_at).offset(
        offset).limit(limit).all()


@exception_handler
def get_transaction_history_by_txn_completed_at_earlier_than(db: SessionLocal, txn_completed_at: datetime,
                                                             offset: int = 0, limit: int = 50) -> TransactionHistory:
    """
    Get transaction history by txn_completed_at earlier than

    :param db: database session
    :param txn_completed_at: txn_completed_at value
    :param offset: offset value
    :param limit: limit value
    :return: TransactionHistory
    """
    return db.query(TransactionHistory).filter(TransactionHistory.txn_completed_at < txn_completed_at).offset(
        offset).limit(limit).all()


@exception_handler
def update_transaction_history_by_tid(db: SessionLocal, tid: int, **kwargs) -> TransactionHistory:
    """
    Update transaction history by tid

    :param db: database session
    :param tid: tid value
    :param kwargs: update values
    :return: TransactionHistory
    """
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
    """
    Update transaction history by txn_hash

    :param db: database session
    :param txn_hash: txn_hash value
    :param kwargs: update values
    :return: TransactionHistory
    """
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
    """
    Delete transaction history by tid

    :param db: database session
    :param tid: tid value
    """
    transaction_history = db.query(TransactionHistory).filter_by(tid=tid).first()

    if transaction_history is None:
        raise NoResultFound(f"No TransactionHistory found with tid={tid}")

    db.delete(transaction_history)
    db.commit()

    return None