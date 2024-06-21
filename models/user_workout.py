from sqlalchemy import Column, String, Date, Integer, DECIMAL

from internal.mysql_db import Base, SessionLocal
from internal.utils import exception_handler


class UserWorkoutView(Base):
    __tablename__ = "user_workout_view"

    workout_id = Column(String(64), primary_key=True)
    bike_no = Column(String(12))
    owner_id = Column(String(64))
    user_name = Column(String(100))
    user_email = Column(String(120))
    workout_date = Column(Date)
    workout_type = Column(Integer)
    energy = Column(DECIMAL(36, 18))
    calories = Column(DECIMAL(36, 18))
    status = Column(Integer)
    token = Column(DECIMAL(36, 18))
    point = Column(Integer)
    workout_created_at = Column(Date)
    workout_updated_at = Column(Date)
    duration_sec = Column(Integer)
    duration = Column(Integer)

    def __repr__(self):
        return (
            f"UserWorkoutView("
            f"workout_id={self.workout_id}, bike_no={self.bike_no}, owner_id={self.owner_id}, "
            f"user_name={self.user_name}, user_email={self.user_email}, workout_date={self.workout_date}, "
            f"workout_type={self.workout_type}, energy={self.energy}, calories={self.calories}, "
            f"status={self.status}, token={self.token}, point={self.point}, "
            f"workout_created_at={self.workout_created_at}, workout_updated_at={self.workout_updated_at}, "
            f"duration_sec={self.duration_sec}, duration={self.duration}"
        )


@exception_handler
def get_user_workout_view(db: SessionLocal, offset: int = 0, limit: int = 50):
    return db.query(UserWorkoutView).offset(offset).limit(limit).all()


@exception_handler
def get_count_user_workout_view(db: SessionLocal):
    return db.query(UserWorkoutView).count()


@exception_handler
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


@exception_handler
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


@exception_handler
def get_user_workout_view_by_type(
    db: SessionLocal, workout_type: int, offset: int = 0, limit: int = 50
):
    return (
        db.query(UserWorkoutView)
        .filter_by(workout_type=workout_type)
        .order_by(UserWorkoutView.workout_date.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


@exception_handler
def get_count_of_workout_by_type(db: SessionLocal, workout_type: int):
    return db.query(UserWorkoutView).filter_by(workout_type=workout_type).count()


@exception_handler
def get_user_workout_view_by_email_and_ptype(
    db: SessionLocal, email: str, workout_type: int, offset: int = 0, limit: int = 50
):
    return (
        db.query(UserWorkoutView)
        .filter_by(user_email=email, workout_type=workout_type)
        .order_by(UserWorkoutView.workout_date.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


@exception_handler
def get_count_user_workout_view_by_email_and_ptype(
    db: SessionLocal, email: str, workout_type: int
):
    return (
        db.query(UserWorkoutView)
        .filter_by(user_email=email, workout_type=workout_type)
        .count()
    )


@exception_handler
def get_user_workout_view_by_email_and_date(
    db: SessionLocal,
    email: str,
    start_date: str,
    end_date: str,
    ptype: int = 0,
    offset: int = 0,
    limit: int = 50,
):
    return (
        db.query(UserWorkoutView)
        .filter(
            UserWorkoutView.user_email == email,
            UserWorkoutView.workout_date >= start_date,
            UserWorkoutView.workout_date <= end_date,
            UserWorkoutView.workout_type == ptype,
        )
        .order_by(UserWorkoutView.workout_date.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
