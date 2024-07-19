from datetime import datetime

from sqlalchemy import Column, String, DECIMAL, SmallInteger, DateTime, CHAR

from internal.mysql_db import Base


class OperationFee(Base):
    """
    Make operation fee out

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

    __tablename__ = "operation_fee"
    __table_args__ = {"comment": "운영비 수익 테이블"}

    oid = Column(String(64, collation="latin1_swedish_ci"), primary_key=True)
    wallet = Column(String(42, collation="latin1_swedish_ci"), nullable=False)
    amount = Column(DECIMAL(36, 18), nullable=False, default=0)
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
            f"OperationFee(oid={self.oid}, wallet={self.wallet}, amount={self.amount}, "
            f"txn_hash={self.txn_hash}, msg={self.msg}, status={self.status}, "
            f"request_at={self.request_at}, operating_at={self.operating_at}, "
            f"result_at={self.result_at}, created_at={self.created_at}, updated_at={self.updated_at})"
        )


def is_oid_duplicate(oid: str) -> bool:
    """
    Check if oid is duplicate

    :param oid: oid value
    :return: bool
        True if duplicate, False if not duplicate
    """
    return False

def make_transaction_out(
    wallet: str,
    owner_id: str,
    amount: float = 0,
) -> OperationFee:
    """
    Make transaction out

    :param wallet: wallet value
    :param owner_id: owner_id value
    :param amount: coin value
    :return: TransactionOut
    """

    operating_fee = amount * 0.12
    return OperationFee(
    )
