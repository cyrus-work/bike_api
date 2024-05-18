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

    uid = Column(String(64), primary_key=True)
    name = Column(String(100, collation="utf8mb4_unicode_ci"))
    email = Column(String(120, collation="latin1_swedish_ci"))
    bid = Column(String(64, collation="latin1_swedish_ci"))
    date = Column(Date, default=datetime.now)
    energy = Column(DECIMAL(36, 18))
    calorie = Column(DECIMAL(36, 18))
    workout_status = Column(Integer)  # 0: 미정산, 1: 포인트 정산
    workout_created_at = Column(DateTime)
    workout_updated_at = Column(DateTime)
    duration_sec = Column(Integer)
    duration = Column(Integer)

    def __repr__(self):
        return (
            f"<UserWorkoutDurationView("
            f"uid={self.uid}, "
            f"name={self.name}, "
            f"email={self.email}, "
            f"bid={self.bid}, "
            f"date={self.date}, "
            f"energy={self.energy}, "
            f"calorie={self.calorie}, "
            f"workout_status={self.workout_status}, "
            f"workout_created_at={self.workout_created_at}, "
            f"workout_updated_at={self.workout_updated_at}), "
            f"duration_sec={self.duration_sec}, "
            f"duration={self.duration}>"
        )


def get_user_workout_duration(db: SessionLocal):
    """
    Get user workout duration

    :param db: db
    :return: UserWorkoutDurationView
    """
    return db.query(UserWorkoutDurationView).all()
