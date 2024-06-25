from fastapi import APIRouter, Depends

from internal.jwt_auth import admin_required
from internal.log import logger
from messages.transaction_out import (
    TxnOutGetRequest,
    TxnOutGetReq,
    TxnOutGetEmailDateReq,
    TxnOutGetAllReq,
)
from models.transaction_out import (
    get_txn_out_by_owner_id,
    get_txns_all,
    get_txn_out_by_date,
    get_txn_out_by_email_and_date,
    get_count_txn_out_by_date,
    get_count_txn_out_by_owner_id, get_count_txns_all,
)
from models.user import get_user_by_email
from models.wallet import get_wallets

router = APIRouter()


@router.post("/list")
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

        logger.info(f"    get_wallets_api db_wallets: {db_wallets_filtered}")
        return db_wallets_filtered

    finally:
        logger.info(f">>> get_wallets_api end")


@router.post("/txn_by_email")
async def post_txn_by_email_api(req: TxnOutGetRequest, user=Depends(admin_required)):
    """
    Get all transactions by wallet
    """
    logger.info(f">>> post_txn_by_wallet start")
    db_user, db = user
    try:
        email = req.email
        offset = req.offset
        limit = req.limit

        target_user = get_user_by_email(db, email)

        db_txns = get_txn_out_by_owner_id(
            db, owner_id=target_user.uid, offset=offset, limit=limit
        )
        db_count = get_count_txn_out_by_owner_id(db, owner_id=target_user.uid)

        logger.info(f"    post_txn_by_wallet db_txns: {db_txns}")
        return {"count": db_count, "data": db_txns}

    finally:
        logger.info(f">>> post_txn_by_wallet end")


@router.post("/txn_by_date")
async def post_txn_by_date_api(req: TxnOutGetReq, user=Depends(admin_required)):
    """
    Get all transactions by date
    """
    logger.info(f">>> post_txn_by_date_api start")
    try:
        db_user, db = user

        start_date = req.start_date
        end_date = req.end_date
        offset = req.offset
        limit = req.limit

        db_txns = get_txn_out_by_date(db, start_date, end_date, offset, limit)
        db_count = get_count_txn_out_by_date(db, start_date, end_date)

        logger.info(f"    post_txn_by_date_api db_txns: {db_txns}")
        return {"count": db_count, "data": db_txns}

    finally:
        logger.info(f">>> post_txn_by_date_api end")


@router.post("/txn_by_email_and_date")
async def post_txn_by_email_and_date_api(
    req: TxnOutGetEmailDateReq, user=Depends(admin_required)
):
    """
    Get all transactions by email and date
    """
    logger.info(f">>> post_txn_by_email_and_date_api start")
    db_user, db = user
    try:
        email = req.email
        start_date = req.start_date
        end_date = req.end_date
        offset = req.offset
        limit = req.limit

        target_user = get_user_by_email(db, email)

        db_txns = get_txn_out_by_email_and_date(
            db, email, start_date, end_date, offset, limit
        )
        db_count = get_count_txn_out_by_date(db, email, start_date, end_date)

        logger.info(
            f"    post_txn_by_email_and_date_api db_txns: {db_txns}, {db_count}"
        )
        return {"count": db_count, "data": db_txns}

    finally:
        logger.info(f">>> post_txn_by_email_and_date_api end")


@router.post("/txn_all")
async def post_txn_all_api(req: TxnOutGetAllReq, user=Depends(admin_required)):
    """
    Get all transactions
    """
    logger.info(f">>> post_txn_all_api start")
    db_user, db = user
    try:
        offset = req.offset
        limit = req.limit

        db_txns = get_txns_all(db, offset=offset, limit=limit)
        db_count = get_count_txns_all(db)

        logger.info(f"    post_txn_all_api db_txns: {db_txns}")
        return {"count": db_count, "data": db_txns}

    finally:
        logger.info(f">>> post_txn_all_api end")
