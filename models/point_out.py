from sqlalchemy import Column, DECIMAL, DateTime, String
from datetime import datetime

from internal.mysql_db import SessionLocal, Base
from internal.utils import generate_hash


class PointOut(Base):
    """
    Make point out

    :param pid: point id
    :param owner_id: owner id
    :param email: email
    :param amount: point value
    :param msg: message
    :param created_at: created time
    :param updated_at: updated time
    :return: PointOut
    """

    __tablename__ = "point_out"

    pid = Column(String(64, collation="latin1_swedish_ci"), primary_key=True)
    owner_id = Column(String(64, collation="latin1_swedish_ci"), nullable=False)
    email = Column(String(255, collation="latin1_swedish_ci"), nullable=False)
    amount = Column(DECIMAL(36, 18), nullable=False, default=0)
    msg = Column(String(255), nullable=True, default=None)
    created_at = Column(DateTime, nullable=False, default=datetime.now())
    updated_at = Column(DateTime, onupdate=datetime.now())

    def __repr__(self):
        return (
            f"<PointOut(pid={self.pid}, owner_id={self.owner_id}, email={self.email}, "
            f"amount={self.amount}, created_at={self.created_at}, updated_at={self.updated_at})>"
        )


def is_pid_duplicate(pid: str) -> bool:
    """
    Check if pid is duplicate

    :param pid: pid value
    :return: bool
        True if duplicate, False if not duplicate
    """
    db = SessionLocal()
    return db.query(PointOut).filter_by(ptid=pid).first()


def make_point_out(
    owner_id: str,
    email: str,
    amount: float = 0,
) -> PointOut:
    """
    Make point out

    :param owner_id: owner_id value
    :param email: email value
    :param amount: point value
    :return: PointOut
    """

    while True:
        pid = generate_hash()
        if not is_pid_duplicate(pid):
            break

    return PointOut(
        pid=pid,
        owner_id=owner_id,
        email=email,
        amount=amount,
    )


def get_point_out_by_email(db, email):
    return db.query(PointOut).filter_by(email=email).all()


def get_point_out_by_pid(db, pid, start_date, end_date):
    db.query(PointOut).filter(
        PointOut.owner_id == pid,
        PointOut.created_at >= start_date,
        PointOut.created_at <= end_date,
    ).all()
