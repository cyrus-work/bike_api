from datetime import datetime

from sqlalchemy import Column, String, Integer, CHAR, DECIMAL, Date, DateTime
from sqlalchemy.ext.declarative import declarative_base

from internal.mysql_db import SessionLocal

Base = declarative_base()


class UserWorkoutDurationView(Base):
    __tablename__ = "user_workout_duration_view"
    __table_args__ = {
        "extend_existing": True
    }  # Allow extending existing table if it exists

    uid = Column(String(64, collation="latin1_swedish_ci"), primary_key=True)
    type = Column(Integer)
    name = Column(String(100, collation="utf8mb4_unicode_ci"))
    email = Column(String(120, collation="latin1_swedish_ci"))
    hashed_pwd = Column(String(60, collation="latin1_swedish_ci"))
    email_verified = Column(CHAR(1), comment="Y: 인증됨, N: 미인증")
    agreement1 = Column(CHAR(1))
    agreement2 = Column(CHAR(1))
    agreement3 = Column(CHAR(1))
    user_status = Column(Integer, comment="0: 가입대기, 1: 가입")
    level = Column(Integer, comment="0: disable, 1: 일반유저, 9: 관리자")
    user_created_at = Column(DateTime)
    user_updated_at = Column(DateTime)
    wid = Column(String(64, collation="latin1_swedish_ci"))
    bid = Column(String(64, collation="latin1_swedish_ci"))
    date = Column(Date, default=datetime.now)
    ptype = Column(Integer)  # 0: token, 1: point
    energy = Column(DECIMAL(36, 18))
    calorie = Column(DECIMAL(36, 18))
    workout_status = Column(Integer)  # 0: 미정산, 1: 포인트 정산
    workout_created_at = Column(DateTime)
    workout_updated_at = Column(DateTime)

    def __repr__(self):
        return (
            f"UserWorkoutDurationView(uid={self.uid}, type={self.type}, name={self.name}, email={self.email}, "
            f"hashed_pwd={self.hashed_pwd}, email_verified={self.email_verified}, "
            f"agreement1={self.agreement1}, agreement2={self.agreement2}, agreement3={self.agreement3}, "
            f"user_status={self.user_status}, level={self.level}, user_created_at={self.user_created_at}, "
            f"user_updated_at={self.user_updated_at}, wid={self.wid}, bid={self.bid}, date={self.date}, "
            f"ptype={self.ptype}, energy={self.energy}, calorie={self.calorie}, workout_status={self.workout_status}, "
            f"workout_created_at={self.workout_created_at}, workout_updated_at={self.workout_updated_at})"
        )


def get_user_workout_duration(db: SessionLocal):
    """
    Get user workout duration

    :param db: db
    :return: UserWorkoutDurationView
    """
    return db.query(UserWorkoutDurationView).all()
