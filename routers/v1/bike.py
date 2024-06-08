from fastapi import APIRouter, Depends

from internal.log import logger
from internal.mysql_db import SessionLocal, get_db
from messages.bike import BikeCreateRequest
from models.bike import (
    make_bike,
    get_bikes_all,
)

router = APIRouter()


@router.post(
    "/create",
)
async def post_create_bike_api(
    bike: BikeCreateRequest, db: SessionLocal = Depends(get_db)
):
    """
    Create bike

    :param bike:
    :param db:
    :return:
    """
    logger.info(f">>> post_create_bike_api start: {bike}")

    try:
        serial = bike.serial
        cpu_version = bike.cpu_version
        board_version = bike.board_version

        db_bike = make_bike(serial, cpu_version, board_version)
        db.add(db_bike)
        db.commit()
        db.refresh(db_bike)
        return db_bike

    finally:
        logger.info(f">>> post_create_bike_api end")


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
