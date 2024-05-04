from fastapi import APIRouter

import traceback

from internal.log import logger
from internal.mysql_db import SessionLocal
from messages.wallets import WalletMsg, WalletFailMsg, WalletInfo, WalletCreateMsg
from models.wallet import make_wallet, Wallet, get_wallets

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

    except Exception as _:
        logger.error(f">>> post_wallets_create_api: {traceback.format_exc()}")
        msg = {"code": 461, "content": "Create wallet failed."}
        logger.error(f">>> post_wallets_create_api: {msg}")
        return WalletFailMsg(**msg)

    finally:
        logger.info(f">>> post_wallets_create_api end <<<")
        if db:
            db.close()


@router.get('/get_wallets')
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
    except Exception as e:
        logger.error(f"get_wallets_api: {e}")
        return WalletFailMsg(
            error_code=500,
            error_message="Internal Server Error",
            error_detail=str(e),
        )
    finally:
        logger.info(f">>> get_wallets_api end")
        if db:
            db.close()
