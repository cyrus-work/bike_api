from datetime import datetime

from sqlalchemy import ForeignKey, Column, String, DateTime, Integer

from internal.mysql_db import Base, SessionLocal
from internal.utils import generate_hash, exception_handler


class Agency(Base):
    __tablename__ = "agencies"

    aid = Column(
        String(64, collation="latin1_swedish_ci"), primary_key=True, index=True
    )
    owner_id = Column(
        String(64, collation="latin1_swedish_ci"),
        ForeignKey("users.uid", ondelete="CASCADE"),
        index=True,
    )
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


def is_aid_duplicate(aid: str) -> bool:
    """
    Check if wid is duplicate

    :param aid: aid 값
    :return: bool
        True if duplicate, False if not duplicate
    """
    db = SessionLocal()
    return db.query(Agency).filter_by(aid=aid).first()


@exception_handler
def make_agency(owner_id: str, name: str, address: str, phone: str) -> Agency:
    """
    Make agency

    :param owner_id: owner_id value
    :param name: name value
    :param address: address value
    :param phone: phone value
    :return: Agency
    """
    try:
        while True:
            aid = generate_hash()
            # aid가 중복되지 않는지 확인
            if not is_aid_duplicate(aid):
                break

        return Agency(
            aid=aid, owner_id=owner_id, name=name, address=address, phone=phone
        )

    except Exception as e:
        raise e


@exception_handler
def get_agency(db: SessionLocal, aid: str) -> Agency:
    """
    Get agency by aid

    :param db: database session
    :param aid: aid value
    :return: Agency
    """
    return db.query(Agency).filter_by(aid=aid).first()


@exception_handler
def get_agency_by_email(db: SessionLocal, email: str) -> Agency:
    """
    Get agency by email

    :param db: database session
    :param email: agency email
    :return: Agency
    """
    return db.query(Agency).filter_by(email=email).first()


@exception_handler
def get_agency_by_name(db: SessionLocal, name: str) -> Agency:
    """
    Get agencies by name pattern

    :param db: database session
    :param name: agency name for search
    :return: Agency
    """
    return db.query(Agency).filter_by(name=name).first()


@exception_handler
def get_agencies_by_name(db: SessionLocal, name: str) -> list[Agency]:
    """
    Get agencies by name pattern

    :param db: database session
    :param name: agency name for search
    :return: list[Agency]
    """
    pattern = f"%{name}%"
    return db.query(Agency).filter_by(Agency.name.like(pattern)).all()


@exception_handler
def get_agency_by_owner_id(
    db: SessionLocal, owner_id: str, offset: int = 0, limit: int = 50
) -> list[Agency]:
    """
    Get agency by owner_id

    :param db: database session
    :param owner_id: owner_id value
    :param offset: offset value, default 0
    :param limit: limit value, default 50
    :return: list[Agency]
    """
    return (
        db.query(Agency).filter_by(owner_id=owner_id).offset(offset).limit(limit).all()
    )


@exception_handler
def update_agency_status(db: SessionLocal, aid: str, status: int) -> int:
    """
    Update agency status

    :param db: database session
    :param aid: agency id
    :param status: status value
    :return: int
    """
    return db.query(Agency).filter_by(aid=aid).update({"status": status})


@exception_handler
def update_agency_by_owner_id(
    db: SessionLocal, owner_id: str, name: str, address: str, phone: str
) -> int:
    """
    Update agency by owner_id

    :param db: database session
    :param owner_id: owner_id value
    :param name: name value
    :param address: address value
    :param phone: phone value
    :return: int
    """
    return (
        db.query(Agency)
        .filter_by(owner_id=owner_id)
        .update({"name": name, "address": address, "phone": phone})
    )
