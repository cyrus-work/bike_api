from internal.mysql_db import Base, SessionLocal
from sqlalchemy import Column, Integer, Float, String

from internal.utils import exception_handler


class WorkoutSummary(Base):
    __tablename__ = "workout_summary_with_email"
    owner_id = Column(Integer, primary_key=True)
    email = Column(String(120))
    total_token_status_0 = Column(Float)
    total_point_status_0 = Column(Float)
    total_token_status_1 = Column(Float)
    total_point_status_1 = Column(Float)
    total_token = Column(Float)
    total_point = Column(Float)


@exception_handler
def get_workout_summary(db: SessionLocal, offset: int = 0, limit: int = 50):
    return db.query(WorkoutSummary).offset(offset).limit(limit).all()


@exception_handler
def get_workout_summary_by_owner_id(db: SessionLocal, owner_id: int):
    return db.query(WorkoutSummary).filter_by(owner_id=owner_id).first()


@exception_handler
def get_workout_summary_by_email(db: SessionLocal, email: str):
    return db.query(WorkoutSummary).filter_by(email=email).first()
