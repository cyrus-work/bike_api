from datetime import datetime

from sqlalchemy import (
    Column,
    String,
    DateTime,
    ForeignKey,
    Integer,
    Date,
    DECIMAL,
    func,
)

from internal.log import logger
from internal.mysql_db import Base, SessionLocal
from internal.utils import generate_hash, exception_handler


class DailyWorkout(Base):
    __tablename__ = "workout"

    wid = Column(
        String(64, collation="latin1_swedish_ci"), primary_key=True, index=True
    )
    owner_id = Column(
        String(64, collation="latin1_swedish_ci"),
        ForeignKey("users.uid", ondelete="CASCADE"),
        index=True,
    )
    bid = Column(String(64, collation="latin1_swedish_ci"), ForeignKey("bike.bid"))
    date = Column(Date, default=datetime.now)
    ptype = Column(Integer, default=0)  # 0: token, 1: point
    energy = Column(DECIMAL(36, 18), index=True, default=0)
    calorie = Column(DECIMAL(36, 18), index=True, default=0)
    status = Column(Integer, default=0)  # 0: 미정산, 1: 포인트 정산
    token = Column(DECIMAL(36, 18), default=0)
    point = Column(Integer, default=0)
    duration = Column(Integer, default=0)
    duration_sec = Column(Integer, default=0)
    transaction_id = Column(String(64, collation="latin1_swedish_ci"))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.now)

    def __repr__(self):
        return (
            f"<DailyWorkout(wid={self.wid}, owner_id={self.owner_id}, bid={self.bid}, "
            f"date={self.date}, ptype={self.ptype}, energy={self.energy}, "
            f"calorie={self.calorie}, status={self.status}, token={self.token}, "
            f"point={self.point}, duration={self.duration}, duration_sec={self.duration_sec}, "
            f"created_at={self.created_at}, updated_at={self.updated_at})>"
        )


def is_wid_duplicate(wid: str) -> bool:
    """
    Check if wid is duplicate

    :param wid: wid 값
    :return: bool
        True if duplicate, False if not duplicate
    """
    db = SessionLocal()
    return db.query(DailyWorkout).filter_by(wid=wid).first()


@exception_handler
def make_workout(uid: str, bid: str, point_type: int) -> DailyWorkout:
    """
    Make workout

    :param uid: owner_id 값
    :param bid: bid 값
    :param point_type: point_type 값
    :return: DailyWorkout
        생성된 workout 객체
    """
    while True:
        wid = generate_hash()
        # wid가 중복되지 않는지 확인
        if not is_wid_duplicate(wid):
            break

    return DailyWorkout(wid=wid, owner_id=uid, bid=bid, ptype=point_type)


@exception_handler
def get_workout_by_wid(db: SessionLocal, wid: str) -> DailyWorkout:
    """
    Get workout by wid

    :param db: SessionLocal
    :param wid: wid 값
    :return: DailyWorkout
        해당하는 wid의 workout
    """
    return db.query(DailyWorkout).filter_by(wid=wid).first()


@exception_handler
def get_workout_by_bid(db: SessionLocal, bid: str) -> DailyWorkout:
    """
    Get workout by bid

    :param db: SessionLocal
    :param bid: bid 값
    :return: DailyWorkout
        해당하는 bid의 workout
    """
    return db.query(DailyWorkout).filter_by(bid=bid).first()


@exception_handler
def get_workout_by_date(
    db: SessionLocal, date: datetime.date, offset: int = 0, limit: int = 50
) -> list[DailyWorkout]:
    """
    Get workout by date

    :param db: SessionLocal
    :param date: date 값
    :param offset: 시작점, 기본값 0
    :param limit: 결과값의 개수, 기본값 50
    :return: list[DailyWorkout]
        해당하는 date의 workout 리스트
    """
    return (
        db.query(DailyWorkout)
        .filter_by(date=date)
        .order_by(DailyWorkout.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


@exception_handler
def get_workout_by_owner_id(
    db: SessionLocal, owner_id: str, offset: int = 0, limit: int = 50
) -> list[DailyWorkout]:
    """
    Get workout by owner_id

    :param db: SessionLocal
    :param owner_id: owner_id 값
    :param offset: 시작점, 기본값 0
    :param limit: 결과값의 개수, 기본값 50
    :return: list[DailyWorkout]
        해당하는 owner_id의 workout 리스트
    """
    return (
        db.query(DailyWorkout)
        .filter_by(owner_id=owner_id)
        .order_by(DailyWorkout.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


@exception_handler
def get_workout_by_date_and_owner_id(
    db: SessionLocal,
    owner_id: str,
    date: datetime.date = datetime.today().date(),
    offset: int = 0,
    limit: int = 50,
) -> list[DailyWorkout]:
    """
    Get workout by date and owner_id

    :param db: SessionLocal
    :param owner_id: owner_id 값
    :param date: date 값, 기본값 datetime.today()
    :param offset: 시작점, 기본값 0
    :param limit: 결과값의 개수, 기본값 50
    """
    logger.info(f"get_workout_by_date_and_owner_id: {owner_id}, {date}")
    return (
        db.query(DailyWorkout)
        .filter_by(owner_id=owner_id, date=date)
        .order_by(DailyWorkout.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


@exception_handler
def get_workout_duration_by_date_and_owner_id(
    db: SessionLocal,
    owner_id: str,
    start_date: datetime.date,
    end_date: datetime.date,
    offset: int = 0,
    limit: int = 50,
) -> list[DailyWorkout]:
    """
    Get workout duration by date and owner_id

    :param db: SessionLocal
    :param owner_id: owner_id 값
    :param start_date: start_date 값
    :param end_date: end_date 값
    :param offset: 시작점, 기본값 0
    :param limit: 결과값의 개수, 기본값 50
    """
    return (
        db.query(DailyWorkout)
        .filter(
            DailyWorkout.owner_id == owner_id,
            DailyWorkout.date >= start_date,
            DailyWorkout.date <= end_date,
        )
        .order_by(DailyWorkout.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


@exception_handler
def update_workout_values_by_wid(
    db: SessionLocal, wid: str, coin: float, point: int, wattage: float, calorie: float
) -> int:
    """
    Update workout values by wid

    :param db: SessionLocal
    :param wid: wid 값
    :param coin: coin 값
    :param point: point 값
    :param wattage: wattage 값
    :param calorie: calorie 값
    :return: int
        업데이트된 row 수
    """
    return (
        db.query(DailyWorkout)
        .filter_by(wid=wid)
        .update({"coin": coin, "point": point, "wattage": wattage, "calorie": calorie})
    )


@exception_handler
def calculate_workout_daily_by_owner_id(
    db: SessionLocal, owner_id: str, date: datetime.date
) -> int:
    """
    Calculate workout daily by owner_id

    :param db: SessionLocal
    :param owner_id: owner_id 값
    :param date: date 값
    :return: int
        업데이트된 row 수
    """
    return (
        db.query(DailyWorkout)
        .filter_by(owner_id=owner_id, date=date)
        .update({"status": 1})
    )


def get_workouts_all(
    db: SessionLocal, offset: int = 0, limit: int = 50
) -> list[DailyWorkout]:
    return (
        db.query(DailyWorkout)
        .order_by(DailyWorkout.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


def get_sum_of_workout_duration_not_calculated_by_user_id(
    db: SessionLocal, owner_id: str
) -> int:
    return (
        db.query(func.sum(DailyWorkout.duration))
        .filter(DailyWorkout.owner_id == owner_id, DailyWorkout.status == 0)
        .scalar()
    )


def get_workout_duration_not_calculated_by_user_id(
    db: SessionLocal, owner_id: str
) -> list[DailyWorkout]:
    return (
        db.query(DailyWorkout)
        .filter(
            DailyWorkout.owner_id == owner_id,
            DailyWorkout.status == 0,
            DailyWorkout.ptype == 0,
        )
        .order_by(DailyWorkout.created_at.desc())
        .all()
    )
