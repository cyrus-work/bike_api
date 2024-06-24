from datetime import datetime

from sqlalchemy import Column, String, Integer, DateTime, CHAR, Float

from internal.mysql_db import Base
from internal.utils import exception_handler


class UserWithWorkoutAndWalletSummary(Base):
    __tablename__ = "user_with_workout_and_wallet_summary"

    uid = Column(String(64, collation="latin1_swedish_ci"), primary_key=True)
    type = Column(Integer, default=0)
    name = Column(String(100, collation="utf8mb4_unicode_ci"))
    email = Column(String(120, collation="latin1_swedish_ci"), unique=True)
    email_verified = Column(CHAR(1), default="N", comment="Y: 인증됨, N: 미인증")
    agreement1 = Column(CHAR(1), default="N")
    agreement2 = Column(CHAR(1), default="N")
    agreement3 = Column(CHAR(1), default="N")
    status = Column(Integer, default=0, comment="0: 가입대기, 1: 가입, 2: 탈퇴")
    level = Column(Integer, default=0, comment="0: disable, 1: 일반유저, 9: 관리자")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    total_token_0 = Column(Float)
    total_point_0 = Column(Float)
    total_duration_0 = Column(Integer)
    total_token_1 = Column(Float)
    total_point_1 = Column(Float)
    total_duration_1 = Column(Integer)
    total_token = Column(Float)
    total_point = Column(Float)
    total_duration = Column(Integer)

    wallet_id = Column(String(64, collation="latin1_swedish_ci"))
    address = Column(String(42, collation="latin1_swedish_ci"))
    wallet_enable = Column(CHAR(1))
    wallet_created_at = Column(DateTime)
    wallet_updated_at = Column(DateTime)

    def __repr__(self):
        return (
            f"UserWithWorkoutAndWalletSummary(uid={self.uid}, type={self.type}, name={self.name}, email={self.email}, "
            f"email_verified={self.email_verified}, agreement1={self.agreement1}, agreement2={self.agreement2}, "
            f"agreement3={self.agreement3}, status={self.status}, level={self.level}, created_at={self.created_at}, "
            f"updated_at={self.updated_at}, total_token_0={self.total_token_0}, "
            f"total_point_0={self.total_point_0}, total_duration_0={self.total_duration_0}, "
            f"total_token_1={self.total_token_1}, total_point_1={self.total_point_1}, "
            f"total_duration_1={self.total_duration_1}, total_token={self.total_token}, "
            f"total_point={self.total_point}, total_duration={self.total_duration}, "
            f"wallet_id={self.wallet_id}, address={self.address}, wallet_enable={self.wallet_enable}, "
            f"wallet_created_at={self.wallet_created_at}, wallet_updated_at={self.wallet_updated_at})"
        )


@exception_handler
def get_user_with_workout_wallet_summary_like_email(
    db, email: str, offset: int = 0, limit: int = 50
):
    return (
        db.query(UserWithWorkoutAndWalletSummary)
        .filter(
            UserWithWorkoutAndWalletSummary.email.like(f"%{email}%"),
            UserWithWorkoutAndWalletSummary.status == 1,
        )
        .order_by(UserWithWorkoutAndWalletSummary.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


@exception_handler
def get_count_user_with_workout_summary_wallet_like_email(db, email: str):
    return (
        db.query(UserWithWorkoutAndWalletSummary)
        .filter(
            UserWithWorkoutAndWalletSummary.email.like(f"%{email}%"),
            UserWithWorkoutAndWalletSummary.status == 1,
        )
        .count()
    )
