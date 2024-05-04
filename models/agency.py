from datetime import datetime

from sqlalchemy import ForeignKey, Column, String, DateTime, Integer

from internal.mysql_db import Base, SessionLocal
from internal.utils import generate_hash


class Agency(Base):
    __tablename__ = 'agencies'

    aid = Column(String(64, collation="latin1_swedish_ci"), primary_key=True, index=True)
    owner_id = Column(String(64, collation="latin1_swedish_ci"), ForeignKey("users.uid", ondelete="CASCADE"),
                      index=True)
    name = Column(String(100, collation="utf8mb4_unicode_ci"), index=True, unique=True)
    address = Column(String(255, collation="latin1_swedish_ci"))
    phone = Column(String(16, collation="latin1_swedish_ci"))
    status = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.now)

    def __repr__(self):
        return (
            f"Agency(aid={self.aid}, owner_id={self.owner_id}, name={self.name}, "
            f"address={self.address}, phone={self.phone}, status={self.status}, "
            f"created_at={self.created_at}, updated_at={self.updated_at})"
        )


def make_agency(owner_id: str, name: str, address: str, phone: str) -> Agency:
    return Agency(aid=generate_hash(), owner_id=owner_id, name=name, address=address, phone=phone)


def get_agency(db: SessionLocal, aid: str) -> Agency:
    return db.query(Agency).filter_by(aid=aid).first()


def get_agency_by_email(db: SessionLocal, email: str) -> Agency:
    return db.query(Agency).filter_by(email=email).first()


def get_agency_by_name(db: SessionLocal, name: str) -> Agency:
    return db.query(Agency).filter_by(name=name).first()


def get_agency_by_owner_id(db: SessionLocal, owner_id: str, offset: int = 0, limit: int = 50) -> list[Agency]:
    return db.query(Agency).filter_by(owner_id=owner_id).offset(offset).limit(limit).all()


def update_agency_status(db: SessionLocal, aid: str, status: int) -> int:
    return db.query(Agency).filter_by(aid=aid).update({"status": status})


def update_agency_by_owner_id(db: SessionLocal, owner_id: str, name: str, address: str, phone: str) -> int:
    return db.query(Agency).filter_by(owner_id=owner_id).update({"name": name, "address": address, "phone": phone})
