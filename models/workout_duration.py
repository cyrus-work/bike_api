from datetime import datetime

from internal.mysql_db import Base, SessionLocal
from sqlalchemy import Column, Integer, String, DateTime, func

from internal.utils import generate_hash
from models.workout import DailyWorkout


class WorkoutDuration(Base):
    __tablename__ = 'workout_durations'

    wid = Column(String(64, collation="latin1_swedish_ci"), primary_key=True, index=True)
    owner_id = Column(String(64))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    duration = Column(Integer)

    def __repr__(self):
        return (
            f"WorkoutDurations(wid={self.wid}, owner_id={self.owner_id}, start_time={self.start_time}, "
            f"end_time={self.end_time}, duration={self.duration})"
        )


def is_wid_duplicate(wid: str) -> bool:
    db = SessionLocal()
    return db.query(DailyWorkout).filter_by(wid=wid).first()


def make_workout_duration(owner_id: str, start_time: datetime, end_time: datetime, duration: int) -> WorkoutDuration:
    while True:
        wid = generate_hash()
        # wid가 중복되지 않는지 확인
        if not is_wid_duplicate(wid):
            break

    return WorkoutDuration(wid=wid, owner_id=owner_id, start_time=start_time, end_time=end_time, duration=duration)


def get_workout_duration_by_owner_id_and_date(db: SessionLocal, owner_id: str, date: datetime.date, offset: int = 0,
                                              limit: int = 50) -> list[WorkoutDuration]:
    return db.query(WorkoutDuration).filter_by(owner_id=owner_id, date=date).offset(offset).limit(limit).all()


def get_workout_duration_sum_by_owner_id_and_date(db: SessionLocal, owner_id: str,
                                                  date: datetime.date = datetime.today()) -> int:
    # Construct the start of the day and the end of the day datetime objects
    day_start = datetime.combine(date, datetime.min.time())
    day_end = datetime.combine(date, datetime.max.time())

    # Query the sum of durations for the specified owner_id within the given date range
    total_duration = db.query(func.sum(WorkoutDuration.duration)). \
        filter(WorkoutDuration.owner_id == owner_id). \
        filter(WorkoutDuration.start_time >= day_start, WorkoutDuration.end_time <= day_end). \
        scalar()

    return total_duration if total_duration is not None else 0

def get_workout_duration_by_owner_id(db: SessionLocal, owner_id: str, offset: int = 0, limit: int = 50) -> list[
        WorkoutDuration]:
    return db.query(WorkoutDuration).filter_by(owner_id=owner_id).offset(offset).limit(limit).all()
