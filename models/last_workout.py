from sqlalchemy import Column, String, DateTime, ForeignKey
from internal.mysql_db import Base, SessionLocal
from internal.utils import exception_handler


class LastWorkout(Base):
    """
    LastWorkout Model - View
    """

    __tablename__ = "last_workout"

    wid = Column(
        String(64, collation="latin1_swedish_ci"), primary_key=True, index=True
    )
    bid = Column(String(64, collation="latin1_swedish_ci"))
    owner_id = Column(String(64, collation="latin1_swedish_ci"), index=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    active = Column(String(1, collation="latin1_swedish_ci"))

    def __repr__(self):
        return (
            f"LastWorkout(wid={self.wid}, bid={self.bid}, owner_id={self.owner_id}, "
            f"created_at={self.created_at}, updated_at={self.updated_at}, active={self.active})"
        )


@exception_handler
def get_last_workout_by_owner_id(db: SessionLocal, owner_id: str):
    """
    Get last workout by owner_id

    :param db: SessionLocal
    :param owner_id: owner_id value
    :return: LastWorkout
    """
    return db.query(LastWorkout).filter_by(owner_id=owner_id).first()


@exception_handler
def get_last_workout_active_by_owner_id(db: SessionLocal, owner_id: str):
    """
    Get last workout by owner_id

    :param db: SessionLocal
    :param owner_id: owner_id value
    :return: LastWorkout
    """
    return (
        db.query(LastWorkout)
        .filter_by(owner_id=owner_id)
        .filter(LastWorkout.active == "Y")
        .first()
    )
