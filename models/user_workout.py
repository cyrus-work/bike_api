from sqlalchemy import Column, String, Date, Integer, DECIMAL
from internal.mysql_db import Base, SessionLocal


class UserWorkoutView(Base):
    __tablename__ = "user_workout_view"

    workout_id = Column(String(64), primary_key=True)
    user_id = Column(String(64))
    user_name = Column(String(100))
    user_email = Column(String(120))
    workout_date = Column(Date)
    workout_type = Column(Integer)
    energy = Column(DECIMAL(36, 18))
    calories = Column(DECIMAL(36, 18))
    status = Column(Integer)
    workout_created_at = Column(Date)
    workout_updated_at = Column(Date)
    duration_sec = Column(Integer)
    duration = Column(Integer)

    def __repr__(self):
        return (
            f"<UserWorkoutView("
            f"workout_id={self.workout_id}, "
            f"user_id={self.user_id}, "
            f"user_name={self.user_name}, "
            f"user_email={self.user_email}, "
            f"workout_date={self.workout_date}, "
            f"workout_type={self.workout_type}, "
            f"energy={self.energy}, "
            f"calories={self.calories}, "
            f"status={self.status}, "
            f"workout_created_at={self.workout_created_at}, "
            f"workout_updated_at={self.workout_updated_at}), "
            f"duration_sec={self.duration_sec}, "
            f"duration={self.duration}>"
        )


def get_user_workout_view(db: SessionLocal, offset: int = 0, limit: int = 50):
    return db.query(UserWorkoutView).offset(offset).limit(limit).all()


def get_user_workout_view_by_id(
    db: SessionLocal, user_id: str, offset: int = 0, limit: int = 50
):
    return (
        db.query(UserWorkoutView)
        .filter_by(user_id=user_id)
        .order_by(UserWorkoutView.workout_date.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


def get_user_workout_view_by_bid(
    db: SessionLocal, bid: str, offset: int = 0, limit: int = 50
):
    return (
        db.query(UserWorkoutView)
        .filter_by(bid=bid)
        .order_by(UserWorkoutView.workout_date.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
