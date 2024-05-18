from fastapi import APIRouter, Depends
from internal.log import logger
from internal.mysql_db import SessionLocal, get_db
from models.bike import get_bikes_all
from models.user_workout import get_user_workout_view

router = APIRouter()


@router.get("/list")
async def get_bikes_all_api(db: SessionLocal = Depends(get_db)):
    """
    Get all bikes

    :return:
    """
    logger.info(f">>> get_bikes_all_api start")

    try:
        db_bikes = get_bikes_all(db)
        logger.info(f"get_bikes_all_api db_bikes: {db_bikes}")
        return db_bikes

    finally:
        logger.info(f">>> get_bikes_all_api end")
