from datetime import datetime

from sqlalchemy import Column, String, DateTime, Integer

from internal.mysql_db import Base, SessionLocal


class BikeManagement(Base):
    __tablename__ = 'bike_management'

    bid = Column(String(64, collation="latin1_swedish_ci"), primary_key=True)
    bike_no = Column(String(10), index=True)
    cpu_version = Column(String(10))
    board_version = Column(String(10))
    production_date = Column(DateTime, default=datetime.now)
    sale_date = Column(DateTime)
    description = Column(String(500))
    status = Column(Integer, default=0)
    owner_id = Column(String(64, collation="latin1_swedish_ci"))
    owner_name = Column(String(100, collation="utf8mb4_unicode_ci"))
    agency_id = Column(String(64, collation="latin1_swedish_ci"))
    agency_name = Column(String(64, collation="utf8mb4_unicode_ci"))
    create_at = Column(DateTime, default=datetime.now)
    update_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return (
            f"BikeManagement(bid={self.bid}, bike_no={self.bike_no}, cpu_version={self.cpu_version}, "
            f"board_version={self.board_version}, production_date={self.production_date}, sale_date={self.sale_date}, "
            f"description={self.description}, status={self.status}, owner_id={self.owner_id}, owner_name={self.owner_name}, "
            f"agency_id={self.agency_id}, agency_name={self.agency_name}, create_at={self.create_at}, update_at={self.update_at})"
        )


def get_bike_management(db: SessionLocal, bid: str):
    return db.query(BikeManagement).filter_by(bid=bid).first()


def get_bike_management_by_bike_no(db: SessionLocal, bike_no: str):
    return db.query(BikeManagement).filter_by(bike_no=bike_no).first()


def get_bike_management_by_owner_id(db: SessionLocal, owner_id: str, offset: int = 0, limit: int = 50) -> list:
    return db.query(BikeManagement).filter_by(owner_id=owner_id).offset(offset).limit(limit).all()
