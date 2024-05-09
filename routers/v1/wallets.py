from fastapi import APIRouter, Depends

from internal.jwt_auth import oauth2_scheme, get_email_from_jwt
from internal.log import logger
from internal.mysql_db import SessionLocal, get_db
from messages.wallets import WalletMsg, WalletFailMsg, WalletInfo
from models.user import get_user_by_email
from models.wallet import make_wallet, get_wallets, get_wallet_by_owner_id

router = APIRouter()


@router.post("/create",
             responses={
                 200: {"model": WalletInfo},
                 461: {"model": WalletFailMsg},
             }, )
async def post_wallets_create_api(wallet: WalletMsg, db: SessionLocal = Depends(get_db)):
    """
    Create wallet

    :param wallet:
    :param db:
    :return:
    """
    logger.info(f">>> post_wallets_create_api start: {wallet}")

    try:
        owner_id = wallet.owner_id
        address = wallet.address

        db = SessionLocal()

        db_wallet = make_wallet(owner_id=owner_id, address=address)

        db.add(db_wallet)
        db.commit()
        db.refresh(db_wallet)

        logger.info(f"post_wallets_create_api db_wallet: {db_wallet}")
        return db_wallet

    finally:
        logger.info(f">>> post_wallets_create_api end")


@router.get('/get')
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


@router.post("/get_own")
async def get_wallets_own_api(db: SessionLocal = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """
    Get wallet by owner_id

    :return:
    """
    logger.info(f">>> get_wallets_own_api start")

    try:
        email = get_email_from_jwt(token)
        db_user = get_user_by_email(db, email)
        owner_id = db_user.uid

        wallets = get_wallet_by_owner_id(db, owner_id=owner_id)
        logger.info(f"get_wallets_own_api wallets: {wallets}")
        return wallets

    finally:
        logger.info(f">>> get_wallets_own_api end")
