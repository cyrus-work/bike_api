from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey, Integer

from internal.mysql_db import Base, SessionLocal
from internal.utils import generate_hash


class Bike(Base):
    __tablename__ = 'bike'

    bid = Column(String(64, collation="latin1_swedish_ci"), primary_key=True, index=True)
    bike_no = Column(String(12), index=True)
    cpu_version = Column(String(10))
    board_version = Column(String(10))
    production_date = Column(DateTime, default=datetime.now)
    sale_date = Column(DateTime)
    description = Column(String(500), default='')
    status = Column(Integer, default=0)
    owner_id = Column(String(64, collation="latin1_swedish_ci"), ForeignKey("users.uid", ondelete="CASCADE"))
    agency_id = Column(String(64, collation="latin1_swedish_ci"), ForeignKey("agencies.aid", ondelete="CASCADE"))
    create_at = Column(DateTime, default=datetime.now)
    update_at = Column(DateTime, onupdate=datetime.now)

    def __repr__(self):
        return (
            f"Bike(bid={self.bid}, bike_no={self.bike_no}, cpu_version={self.cpu_version}, "
            f"board_version={self.board_version}, production_date={self.production_date}, sale_date={self.sale_date}, "
            f"description={self.description}, status={self.status}, owner_id={self.owner_id}, "
            f"agency_id={self.agency_id}, create_at={self.create_at}, update_at={self.update_at})"
        )


def make_bike(bike_no: str, cpu_version: str, board_version: str, owner_id: str, agency_id: str) -> Bike:
    return Bike(bid=generate_hash(), bike_no=bike_no, cpu_version=cpu_version, board_version=board_version,
                owner_id=owner_id, agency_id=agency_id)


def get_bike_by_bid(db: SessionLocal, bid: str) -> Bike:
    return db.query(Bike).filter_by(bid=bid).first()


def get_bike_by_bike_no(db: SessionLocal, bike_no: str) -> Bike:
    return db.query(Bike).filter_by(bike_no=bike_no).first()


def get_bikes_by_owner_id(db: SessionLocal, owner_id: str, offset: int = 0, limit: int = 50) -> list[Bike]:
    return db.query(Bike).filter_by(owner_id=owner_id).offset(offset).limit(limit).all()


def get_bikes_by_agency_id(db: SessionLocal, agency_id: str, offset: int = 0, limit: int = 50) -> list[Bike]:
    return db.query(Bike).filter_by(agency_id=agency_id).offset(offset).limit(limit).all()
