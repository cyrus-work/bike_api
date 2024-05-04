from datetime import datetime, time

from sqlalchemy import Column, String, DateTime, Float, ForeignKey, Integer, Date, Time

from internal.mysql_db import Base, SessionLocal
from internal.utils import generate_hash


class DailyProduction(Base):
    __tablename__ = 'daily_production'

    did = Column(String(64, collation="latin1_swedish_ci"), primary_key=True, index=True)
    wid = Column(String(64, collation="latin1_swedish_ci"), ForeignKey("wallets.wid"))
    date = Column(Date, default=datetime.now)
    bid = Column(String(36, collation="latin1_swedish_ci"), ForeignKey("bike_management.bid"))
    coin = Column(Float, index=True, default=0)
    point = Column(Float, index=True, default=0)
    wattage = Column(Float, index=True, default=0)
    start_at = Column(DateTime, default=datetime.now())
    during_at = Column(Time)  # datetime.now().time() 날짜부분만 입력함.
    status = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.now)

    def __repr__(self):
        return (
            f"DailyProduction(did={self.did}, wid={self.wid}, date={self.date}, bid={self.bid}, "
            f"coin={self.coin}, point={self.point}, wattage={self.wattage}, start_at={self.start_at}, "
            f"during_at={self.during_at}, status={self.status}, created_at={self.created_at}, updated_at={self.updated_at})"
        )


def make_daily_production(wid: str, bid: str, coin: float, point: float, wattage: float,
                          during_at: time) -> DailyProduction:
    return DailyProduction(did=generate_hash(), wid=wid, bid=bid, coin=coin, point=point, wattage=wattage,
                           during_at=during_at)


def get_daily_production_by_did(db: SessionLocal, did: str) -> DailyProduction:
    return db.query(DailyProduction).filter_by(did=did).first()


def get_daily_production_by_bid(db: SessionLocal, bid: str) -> DailyProduction:
    return db.query(DailyProduction).filter_by(bid=bid).first()


def get_daily_production_by_wid(db: SessionLocal, wid: str) -> DailyProduction:
    return db.query(DailyProduction).filter_by(wid=wid).first()
