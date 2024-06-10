from fastapi import APIRouter, Depends

from internal.exceptions import BikeNotExistsException
from internal.jwt_auth import admin_required
from internal.log import logger
from messages.bike import (
    BikeCreateRequest,
    BikeGetRequest,
    BikeDeleteMsg,
    BikeCreateMsg,
)
from models.bike import get_bikes_all, make_bike, get_bike_by_bike_no

router = APIRouter()


@router.get("/list")
async def get_bikes_all_api(user=Depends(admin_required)):
    """
    Get all bikes

    :return:
    """
    logger.info(f">>> get_bikes_all_api start")

    admin, db = user

    try:
        db_bikes = get_bikes_all(db)
        logger.info(f"get_bikes_all_api db_bikes: {db_bikes}")
        return db_bikes

    finally:
        logger.info(f">>> get_bikes_all_api end")


@router.post("/create")
async def post_create_bike_api(bike: BikeCreateRequest, user=Depends(admin_required)):
    """
    Create bike

    :param bike:
    :param user:
    :return:
    """
    logger.info(f">>> post_create_bike_api start: {bike}")

    try:
        admin, db = user
        serial = bike.serial
        cpu_version = bike.cpu_version
        board_version = bike.board_version

        db_bike = make_bike(serial, cpu_version, board_version)
        db.add(db_bike)
        db.commit()
        db.refresh(db_bike)
        return BikeCreateMsg(serial=db_bike.bike_no, code=200, content="success")

    finally:
        logger.info(f">>> post_create_bike_api end")


@router.post("/delete")
async def post_delete_bike_api(bike: BikeGetRequest, user=Depends(admin_required)):
    """
    Delete bike

    :param bike:
    :param user:
    :return:
    """
    logger.info(f">>> post_delete_bike_api start: {bike}")

    try:
        admin, db = user
        serial = bike.serial

        db_bike = get_bike_by_bike_no(db, serial)
        if db_bike is None:
            raise BikeNotExistsException

        db.delete(db_bike)
        db.commit()
        return BikeDeleteMsg(code=200, content="success", serial=serial)

    finally:
        logger.info(f">>> post_delete_bike_api end")
