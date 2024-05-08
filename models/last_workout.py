from sqlalchemy import Column, String, DateTime, ForeignKey
from internal.mysql_db import Base, SessionLocal


class LastWorkout(Base):
    __tablename__ = 'last_workout'

    wid = Column(String(64, collation="latin1_swedish_ci"), primary_key=True, index=True)
    owner_id = Column(String(64, collation="latin1_swedish_ci"), ForeignKey("users.uid", ondelete="CASCADE"),
                      index=True)
    created_at = Column(DateTime)

    def __repr__(self):
        return (
            f"LastWorkout(wid={self.wid}, owner_id={self.owner_id}, created_at={self.created_at})"
        )


def get_last_workout_by_owner_id(db: SessionLocal, owner_id: str):
    return db.query(LastWorkout).filter_by(owner_id=owner_id).first()
