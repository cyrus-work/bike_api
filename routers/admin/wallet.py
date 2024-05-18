from fastapi import APIRouter, Depends

from internal.log import logger
from internal.mysql_db import SessionLocal, get_db
from models.wallet import get_wallets

router = APIRouter()


@router.get("/list")
async def get_wallets_api(db: SessionLocal = Depends(get_db)):
    """
    Get all wallets
    """
    logger.info(f">>> get_wallets_api start")
    try:
        db_wallets = get_wallets(db)
        logger.info(f"get_wallets_api db_wallets: {db_wallets}")
        return db_wallets

    finally:
        logger.info(f">>> get_wallets_api end")
