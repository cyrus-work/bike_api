from fastapi import APIRouter, Depends

from internal.jwt_auth import oauth2_scheme, get_email_from_jwt, get_current_user
from internal.log import logger
from internal.mysql_db import SessionLocal, get_db
from messages.wallets import WalletMsg
from models.user import get_user_by_email, User
from models.wallet import make_wallet, get_wallets, get_wallet_by_owner_id

router = APIRouter()


@router.post(
    "/set",
)
async def post_wallets_create_api(
    req: WalletMsg,
    user: User = Depends(get_current_user),
):
    """
    Create wallet

    :param req:
    :param user:
    :return:
    """
    logger.info(f">>> post_wallets_create_api start: {req}")

    try:
        address = req.address

        db_user, db = user

        db_wallet = get_wallet_by_owner_id(db, owner_id=db_user.uid)
        if db_wallet:
            db.merge(db_wallet)
        else:
            db_wallet = make_wallet(owner_id=db_user.uid, address=address)
            db.add(db_wallet)

        db.commit()
        db.refresh(db_wallet)

        logger.info(f"post_wallets_create_api db_wallet: {db_wallet}")
        return db_wallet

    finally:
        logger.info(f">>> post_wallets_create_api end")


@router.get("/get")
async def get_wallets_api(db: SessionLocal = Depends(get_db)):
    """
    Get all wallets

    :return:
    """
    logger.info(f">>> get_wallets_api start")

    try:
        wallets = get_wallets(db)
        logger.info(f"get_wallets_api wallets: {wallets}")
        return wallets

    finally:
        logger.info(f">>> get_wallets_api end")


@router.get("/get_own")
async def get_wallets_own_api(user: User = Depends(get_current_user)):
    """
    Get wallet by owner_id

    :return:
    """
    logger.info(f">>> get_wallets_own_api start")

    try:
        db_user, db = user
        owner_id = db_user.uid

        wallets = get_wallet_by_owner_id(db, owner_id=owner_id)
        logger.info(f"get_wallets_own_api wallets: {wallets}")
        return wallets

    finally:
        logger.info(f">>> get_wallets_own_api end")
