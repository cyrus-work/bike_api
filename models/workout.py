from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Date, DECIMAL

from internal.mysql_db import Base, SessionLocal
from internal.utils import generate_hash


class DailyWorkout(Base):
    __tablename__ = 'workout'

    did = Column(String(64, collation="latin1_swedish_ci"), primary_key=True, index=True)
    owner_id = Column(String(64, collation="latin1_swedish_ci"), ForeignKey("users.uid", ondelete="CASCADE"),
                      index=True)
    bid = Column(String(64, collation="latin1_swedish_ci"), ForeignKey("bike.bid"))
    date = Column(Date, default=datetime.now)
    ptype = Column(Integer, default=0)  # 0: token, 1: point
    energy = Column(DECIMAL(36, 18), index=True, default=0)
    calorie = Column(DECIMAL(36, 18), index=True, default=0)
    status = Column(Integer, default=0)  # 0: 미정산, 1: 포인트 정산
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.now)

    def __repr__(self):
        return (
            f"DailyWorkout(did={self.did}, owner_id={self.owner_id}, bid={self.bid}, date={self.date}, "
            f"ptype={self.ptype}, energy={self.energy}, calorie={self.calorie}, status={self.status}, "
            f"created_at={self.created_at}, updated_at={self.updated_at})"
        )


def is_did_duplicate(did: str) -> bool:
    db = SessionLocal()
    return db.query(DailyWorkout).filter_by(did=did).first()


def make_workout(uid: str, bid: str, point_type: int) -> DailyWorkout:
    while True:
        did = generate_hash()
        # did가 중복되지 않는지 확인
        if not is_did_duplicate(did):
            break

    return DailyWorkout(did=did, owner_id=uid, bid=bid, ptype=point_type)


def get_workout_by_did(db: SessionLocal, did: str) -> DailyWorkout:
    return db.query(DailyWorkout).filter_by(did=did).first()


def get_workout_by_bid(db: SessionLocal, bid: str) -> DailyWorkout:
    return db.query(DailyWorkout).filter_by(bid=bid).first()


def get_workout_by_date(db: SessionLocal, owner_id: str, date: datetime.date, offset: int = 0, limit: int = 50) -> list[
    DailyWorkout]:
    return db.query(DailyWorkout).filter_by(owner_id=owner_id, date=date).offset(offset).limit(limit).all()


def get_workout_by_owner_id(db: SessionLocal, owner_id: str, offset: int = 0, limit: int = 50) -> list[DailyWorkout]:
    return db.query(DailyWorkout).filter_by(owner_id=owner_id).offset(offset).limit(limit).all()


def update_workout_values_by_did(db: SessionLocal, did: str, coin: float, point: int, wattage: float,
                                 calorie: float) -> int:
    return db.query(DailyWorkout).filter_by(did=did).update(
        {"coin": coin, "point": point, "wattage": wattage, "calorie": calorie})
