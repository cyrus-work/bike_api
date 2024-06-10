from sqlalchemy import Column, String, Integer, DECIMAL
from internal.mysql_db import Base


class WorkoutSummary(Base):
    __tablename__ = "user_workout_summary_view"

    uid = Column(String(64, collation="latin1_swedish_ci"), primary_key=True)
    email = Column(String(255, collation="latin1_swedish_ci"))
    token = Column(DECIMAL(36, 18), nullable=False, default=0)
    point = Column(DECIMAL(36, 18), nullable=False, default=0)
    duration = Column(Integer, nullable=False, default=0)

    def __repr__(self):
        return (
            f"WorkoutSummary(uid={self.uid}, email={self.email}, token={self.token}, "
            f"point={self.point}, duration={self.duration})"
        )


def get_summary_by_email(db, email: str):
    db_workout_summary = db.query(WorkoutSummary).filter_by(email=email).first()
    if db_workout_summary:
        delattr(db_workout_summary, 'uid')
    return db_workout_summary
