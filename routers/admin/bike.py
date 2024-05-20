from fastapi import APIRouter, Depends

from internal.jwt_auth import admin_required
from internal.log import logger
from models.bike import get_bikes_all

router = APIRouter()


@router.get("/list")
async def get_bikes_all_api(user=Depends(admin_required)):
    """
    Get all bikes

    :return:
    """
    logger.info(f">>> get_bikes_all_api start")

    db_user, db = user

    try:
        db_bikes = get_bikes_all(db)
        logger.info(f"get_bikes_all_api db_bikes: {db_bikes}")
        return db_bikes

    finally:
        logger.info(f">>> get_bikes_all_api end")
