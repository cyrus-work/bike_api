import traceback

from fastapi import APIRouter, Depends
from sqlalchemy.exc import IntegrityError
from fastapi.responses import JSONResponse

from internal.jwt_auth import oauth2_scheme, get_email_from_jwt
from internal.log import logger
from internal.mysql_db import SessionLocal
from messages.wallets import WalletMsg, WalletFailMsg, WalletInfo
from models.user import get_user_by_email
from models.wallet import make_wallet, get_wallets, get_wallet_by_owner_id

router = APIRouter()


@router.post("/create",
             responses={
                 200: {"model": WalletInfo},
                 461: {"model": WalletFailMsg},
             }, )
async def post_wallets_create_api(wallet: WalletMsg):
    """
    Create wallet
    :param request:
    :param wallet:
    :return:
    """
    logger.info(f">>> post_wallets_create_api start: {wallet}")
    db = None

    owner_id = wallet.owner_id
    address = wallet.address
    try:
        db = SessionLocal()

        db_wallet = make_wallet(owner_id=owner_id, address=address)

        db.add(db_wallet)
        db.commit()
        db.refresh(db_wallet)

        logger.info(f">>> post_wallets_create_api: {db_wallet}")
        return db_wallet

    except IntegrityError as e:
        db.rollback()
        logger.error(f">>> post_wallets_create_api error: {traceback.format_exc()}")
        msg = {"code": 461, "content": f"{e}"}
        logger.error(f">>> post_wallets_create_api: {msg}")
        return JSONResponse(status_code=461, content=msg)

    finally:
        logger.info(f">>> post_wallets_create_api end <<<")
        if db:
            db.close()


@router.get('/get')
async def get_wallets_api():
    """
    Get all wallets
    :return:
    """
    logger.info(f">>> get_wallets_api start")
    db = None

    try:
        db = SessionLocal()

        wallets = get_wallets(db)
        logger.info(f"get_wallets_api: {wallets}")
        return wallets

    except IntegrityError as e:
        db.rollback()
        logger.error(f"get_wallets_api error: {traceback.format_exc()}")
        msg = {"code": 461, "content": "{e}"}
        logger.error(f"get_wallets_api: {e}")
        return WalletFailMsg(**msg)

    finally:
        logger.info(f">>> get_wallets_api end")
        if db:
            db.close()

@router.post("/get_own")
async def get_wallets_own_api(token: str = Depends(oauth2_scheme)):
    """
    Get wallet by owner_id

    :return:
    """
    logger.info(f">>> get_wallets_own_api start:")
    db = None

    try:
        db = SessionLocal()

        email = get_email_from_jwt(token)
        db_user = get_user_by_email(db, email)
        owner_id = db_user.uid

        wallets = get_wallet_by_owner_id(db, owner_id=owner_id)
        logger.info(f"get_wallets_own_api: {wallets}")
        return wallets

    except IntegrityError as e:
        db.rollback()
        logger.error(f"get_wallets_own_api error: {traceback.format_exc()}")
        msg = {"code": 461, "content": "{e}"}
        logger.error(f"get_wallets_own_api: {e}")
        return WalletFailMsg(**msg)

    finally:
        logger.info(f">>> get_wallets_own_api end")
        if db:
            db.close()
