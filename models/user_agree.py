from internal.mysql_db import Base
from sqlalchemy import Column, String, Boolean, ForeignKey


class UserAgree(Base):
    __tablename__ = 'user_agree'

    uid = Column(String(64, collation="latin1_swedish_ci"),
                 ForeignKey("users.uid", ondelete="CASCADE"),
                 primary_key=True, index=True)
    agree1 = Column(Boolean, default=False)
    agree2 = Column(Boolean, default=False)
    agree3 = Column(Boolean, default=False)
    agree4 = Column(Boolean, default=False)

    def __repr__(self):
        return (
            f"UserAgree(uid={self.uid}, agree1={self.agree1}, agree2={self.agree2}, agree3={self.agree3}, agree4={self.agree4})"
        )


def make_user_agree(uid: str) -> UserAgree:
    return UserAgree(uid=uid)


def get_user_agree_by_uid(db, uid: str):
    return db.query(UserAgree).filter_by(uid=uid).first()


def update_user_agree(db, uid: str, agree1: bool, agree2: bool, agree3: bool, agree4: bool):
    db.query(UserAgree).filter_by(uid=uid).update({
        'agree1': agree1,
        'agree2': agree2,
        'agree3': agree3,
        'agree4': agree4
    })
    db.commit()
    return db.query(UserAgree).filter_by(uid=uid).first()


def delete_user_agree(db, uid: str):
    db.query(UserAgree).filter_by(uid=uid).delete()
    db.commit()
    return db.query(UserAgree).filter_by(uid=uid).first()
