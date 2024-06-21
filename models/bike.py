from datetime import datetime

from sqlalchemy import Column, String, DateTime

from internal.mysql_db import Base, SessionLocal
from internal.utils import generate_hash, exception_handler


class Bike(Base):
    __tablename__ = "bike"

    bid = Column(
        String(64, collation="latin1_swedish_ci"), primary_key=True, index=True
    )
    bike_no = Column(String(12), index=True)
    cpu_version = Column(String(10))
    board_version = Column(String(10))
    create_at = Column(DateTime, default=datetime.now)
    update_at = Column(DateTime, onupdate=datetime.now)

    def __repr__(self):
        return (
            f"Bike(bid={self.bid}, bike_no={self.bike_no}, cpu_version={self.cpu_version}, "
            f"board_version={self.board_version}, create_at={self.create_at}, update_at={self.update_at})"
        )


def is_bid_duplicate(bid: str) -> bool:
    """
    Check if wid is duplicate

    :param bid: bid 값
    :return: bool
        True if duplicate, False if not duplicate
    """
    db = SessionLocal()
    return db.query(Bike).filter_by(bid=bid).first()


@exception_handler
def make_bike(bike_no: str, cpu_version: str, board_version: str) -> Bike:
    """
    Make bike

    :param bike_no: bike_no 값
    :param cpu_version: cpu_version 값
    :param board_version: board_version 값
    :return: Bike
    """
    while True:
        bid = generate_hash()
        # bid가 중복되지 않는지 확인
        if not is_bid_duplicate(bid):
            break

    return Bike(
        bid=bid,
        bike_no=bike_no,
        cpu_version=cpu_version,
        board_version=board_version,
    )


@exception_handler
def get_bike_by_bid(db: SessionLocal, bid: str) -> Bike:
    """
    Get bike by bid

    :param db: database session
    :param bid: bid value
    :return: Bike
    """
    return db.query(Bike).filter_by(bid=bid).first()


@exception_handler
def get_bike_by_bike_no(db: SessionLocal, bike_no: str) -> Bike:
    """
    Get bike by bike_no

    :param db: database session
    :param bike_no: bike_no value
    :return: Bike
    """
    return db.query(Bike).filter_by(bike_no=bike_no).first()


@exception_handler
def get_bike_by_bike_no_like(db: SessionLocal, bike_no: str) -> list[Bike]:
    """
    Get bike by bike_no like

    :param db: database session
    :param bike_no: bike_no value
    :return: list[Bike]
    """
    return db.query(Bike).filter(Bike.bike_no.like(f"%{bike_no}%")).all()


@exception_handler
def get_bikes_all(db: SessionLocal, offset: int = 0, limit: int = 50) -> list[Bike]:
    """
    Get all bikes

    :param db: database session
    :param offset: offset value
    :param limit: limit value
    :return: list[Bike]
    """
    return db.query(Bike).offset(offset).limit(limit).all()


@exception_handler
def get_bikes_count_all(db: SessionLocal) -> int:
    """
    Get all bikes count

    :param db: database session
    :return: int
    """
    return db.query(Bike).count()
