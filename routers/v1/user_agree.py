from fastapi import APIRouter, Depends
from internal.jwt_auth import oauth2_scheme
from internal.log import logger
from internal.mysql_db import SessionLocal, get_db
from internal.jwt_auth import get_email_from_jwt
from messages.user import UserEmailRequest
from models.user import get_user_by_email
from models.user_agree import get_user_agree_by_uid, make_user_agree

router = APIRouter()


@router.post("/create")
async def create_user_agree_api(req: UserEmailRequest, db: SessionLocal = Depends(get_db)):
    """
    Create user agree API
    """
    logger.info(f">>> create_user_agree_api start")
    try:
        email = req.email

        db_user = get_user_by_email(db, email)
        db_user_agree = make_user_agree(db_user.uid)

        db.add(db_user_agree)
        db.commit()

        return db_user_agree

    finally:
        logger.info(f">>> create_user_agree_api end")


@router.post("/get")
async def get_user_agree_api(db: SessionLocal = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """
    Get user agree API
    """
    logger.info(f">>> get_user_agree_api start")
    try:
        email = get_email_from_jwt(token)

        db_user = get_user_by_email(db, email)
        db_user_agree = get_user_agree_by_uid(db, db_user.uid)

        return db_user_agree

    finally:
        logger.info(f">>> get_user_agree_api end")


@router.post("/update")
async def update_user_agree_api(db: SessionLocal = Depends(get_db), token: str = Depends(oauth2_scheme),
                                agree1: bool = False, agree2: bool = False, agree3: bool = False, agree4: bool = False):
    """
    Update user agree API
    """
    logger.info(f">>> update_user_agree_api start")
    try:
        email = get_email_from_jwt(token)

        db_user = get_user_by_email(db, email)
        db_user_agree = get_user_agree_by_uid(db, db_user.uid)

        db_user_agree.agree1 = agree1
        db_user_agree.agree2 = agree2
        db_user_agree.agree3 = agree3
        db_user_agree.agree4 = agree4

        return db_user_agree

    finally:
        logger.info(f">>> update_user_agree_api end")
