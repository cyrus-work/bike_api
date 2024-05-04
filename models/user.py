from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime

from internal.mysql_db import Base, SessionLocal
from internal.utils import get_password_hash, generate_hash


class User(Base):
    __tablename__ = 'users'

    uid = Column(String(64, collation="latin1_swedish_ci"), primary_key=True)
    type = Column(Integer, default=0)
    name = Column(String(100, collation="utf8mb4_unicode_ci"))
    email = Column(String(120, collation="latin1_swedish_ci"), unique=True)
    hashed_pwd = Column(String(60, collation="latin1_swedish_ci"))
    email_verified = Column(String(1), default='N')
    status = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return (
            f"User(uid={self.uid}, type={self.type}, name={self.name}, email={self.email}, hashed_pwd={self.hashed_pwd}, "
            f"email_verified={self.email_verified}, status={self.status}, created_at={self.created_at}, updated_at={self.updated_at})"
        )


def make_user(name: str, email: str, password: str) -> User:
    uid = generate_hash()
    hashed_pwd = get_password_hash(password)
    return User(uid=uid, name=name, email=email, hashed_pwd=hashed_pwd)


### database operations ###
def get_user_by_email(db: SessionLocal, email: str) -> User:
    return db.query(User).filter(User.email == email).first()
