from datetime import datetime

from sqlalchemy import Column, String, DateTime, Integer

from internal.mysql_db import Base, SessionLocal
from internal.utils import exception_handler


class BikeManagement(Base):
    """
        BikeManagement Model - View

        create definer = hegsdev@`%` view bike_management as
    select `b`.`bid`             AS `bid`,
           `b`.`bike_no`         AS `bike_no`,
           `b`.`cpu_version`     AS `cpu_version`,
           `b`.`board_version`   AS `board_version`,
           `b`.`production_date` AS `production_date`,
           `b`.`sale_date`       AS `sale_date`,
           `b`.`description`     AS `description`,
           `b`.`status`          AS `status`,
           `b`.`owner_id`        AS `owner_id`,
           `u`.`name`            AS `owner_name`,
           `a`.`aid`             AS `agency_id`,
           `a`.`name`            AS `agency_name`,
           `b`.`create_at`       AS `create_at`,
           `b`.`update_at`       AS `update_at`
    from ((`hegs_bike`.`bike` `b` left join `hegs_bike`.`users` `u`
           on (`b`.`owner_id` = `u`.`uid`)) left join `hegs_bike`.`agencies` `a` on (`b`.`agency_id` = `a`.`aid`));
    """

    __tablename__ = "bike_management"

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


@exception_handler
def get_bike_management(db: SessionLocal, bid: str):
    """
    Get bike management by bid

    :param db: database session
    :param bid: bid value
    :return: BikeManagement
    """
    return db.query(BikeManagement).filter_by(bid=bid).first()


@exception_handler
def get_bike_management_by_bike_no(db: SessionLocal, bike_no: str):
    """
    Get bike management by bike_no

    :param db: database session
    :param bike_no: bike_no value
    :return: BikeManagement
    """
    return db.query(BikeManagement).filter_by(bike_no=bike_no).first()


@exception_handler
def get_bike_management_by_owner_id(
    db: SessionLocal, owner_id: str, offset: int = 0, limit: int = 50
) -> list:
    """
    Get bike management by owner_id

    :param db: database session
    :param owner_id: owner_id value
    :param offset: offset value
    :param limit: limit value
    :return: list
    """
    return (
        db.query(BikeManagement)
        .filter_by(owner_id=owner_id)
        .offset(offset)
        .limit(limit)
        .all()
    )


@exception_handler
def get_bike_management_all(db: SessionLocal, offset: int = 0, limit: int = 50) -> list:
    """
    Get bike management by agency_id

    :param db: database session
    :param agency_id: agency_id value
    :param offset: offset value
    :param limit: limit value
    :return: list
    """
    return (
        db.query(BikeManagement)
        .order_by(BikeManagement.create_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
