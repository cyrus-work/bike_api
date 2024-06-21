from fastapi import APIRouter, Depends

from internal.exceptions import BikeNotExistsException
from internal.log import logger
from internal.mysql_db import SessionLocal, get_db
from messages.bike import BikeGetRequest
from models.bike import (
    get_bikes_all,
    get_bike_by_bike_no,
)

router = APIRouter()


@router.get("/get_all")
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


@router.post("/check")
async def post_check_bike_api(bike: BikeGetRequest, db: SessionLocal = Depends(get_db)):
    """
    Check bike

    :param bike:
    :param db:
    :return:
    """
    logger.info(f">>> post_check_bike_api start: {bike}")

    try:
        db_bike = get_bike_by_bike_no(db, bike.serial)
        logger.info(f"post_check_bike_api db_bike: {db_bike}")

        if db_bike is None:
            raise BikeNotExistsException

        return db_bike

    finally:
        logger.info(f">>> post_check_bike_api end")
