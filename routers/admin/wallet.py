from fastapi import APIRouter, Depends

from internal.jwt_auth import admin_required
from internal.log import logger
from messages.transaction_out import TxnOutGetRequest
from models.transaction_out import get_txn_out_by_wallet
from models.wallet import get_wallets

router = APIRouter()


@router.get("/list")
async def get_wallets_api(user=Depends(admin_required)):
    """
    Get all wallets
    """
    logger.info(f">>> get_wallets_api start")
    db_user, db = user
    try:
        db_wallets = get_wallets(db)

        # 필터링된 요소를 포함한 딕셔너리 리스트 생성
        db_wallets_filtered = [
            {"wid": wallet.wid, "address": wallet.address, "enable": wallet.enable}
            for wallet in db_wallets
        ]

        logger.info(f"get_wallets_api db_wallets: {db_wallets_filtered}")
        return db_wallets_filtered

    finally:
        logger.info(f">>> get_wallets_api end")


@router.post("/txn_by_wallet")
async def post_txn_by_wallet(req: TxnOutGetRequest, user=Depends(admin_required)):
    """
    Get all transactions by wallet
    """
    logger.info(f">>> post_txn_by_wallet start")
    db_user, db = user
    try:
        db_wallet = get_txn_out_by_wallet(db, owner_id=req.owner_id)

        db_txns = get_txns_by_wallet(db, wallet_id=db_wallet.wid)
        logger.info(f"post_txn_by_wallet db_txns: {db_txns}")
        return db_txns

    finally:
        logger.info(f">>> post_txn_by_wallet end")
