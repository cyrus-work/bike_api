from sqlalchemy import Column, Integer, Float, String

from internal.mysql_db import Base, SessionLocal
from internal.utils import exception_handler


class WorkoutSummary(Base):
    __tablename__ = "workout_summary_with_email"
    owner_id = Column(Integer, primary_key=True)
    email = Column(String(120))
    total_token_status_0 = Column(Float)
    total_point_status_0 = Column(Float)
    total_duration_status_0 = Column(Integer)
    total_token_status_1 = Column(Float)
    total_point_status_1 = Column(Float)
    total_duration_status_1 = Column(Integer)
    total_token = Column(Float)
    total_point = Column(Float)
    total_duration = Column(Integer)

    def __repr__(self):
        return (
            f"WorkoutSummary("
            f"owner_id={self.owner_id}, email={self.email}, total_token_status_0={self.total_token_status_0}, "
            f"total_point_status_0={self.total_point_status_0}, total_duration_status_0={self.total_duration_status_0}, "
            f"total_token_status_1={self.total_token_status_1}, total_point_status_1={self.total_point_status_1}, "
            f"total_duration_status_1={self.total_duration_status_1}, total_token={self.total_token}, "
            f"total_point={self.total_point}, total_duration={self.total_duration}"
        )


@exception_handler
def get_workout_summary(db: SessionLocal, offset: int = 0, limit: int = 50):
    return db.query(WorkoutSummary).offset(offset).limit(limit).all()


@exception_handler
def get_workout_summary_by_owner_id(db: SessionLocal, owner_id: int):
    return db.query(WorkoutSummary).filter_by(owner_id=owner_id).first()


@exception_handler
def get_workout_summary_by_email(db: SessionLocal, email: str):
    return db.query(WorkoutSummary).filter_by(email=email).first()
