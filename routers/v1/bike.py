from fastapi import APIRouter, Depends

from internal.jwt_auth import oauth2_scheme, get_email_from_jwt
from internal.log import logger
from internal.mysql_db import SessionLocal
from messages.bike import BikeCreateRequest, BikeManagementFailMsg, BikeCreateMsg
from models.agency import get_agency_by_name, get_agency_by_owner_id
from models.bike import make_bike, get_bikes_by_owner_id, get_bikes_by_agency_id
from models.user import get_user_by_email

router = APIRouter()


@router.post("/create",
             responses={
                 200: {"model": BikeCreateMsg},
                 461: {"model": BikeManagementFailMsg},
             }, )
async def post_create_bike_api(bike: BikeCreateRequest):
    """
    Create bike

    :param bike:
    :return:
    """
    logger.info(f"post_create_bike_api start: {bike}")
    db = None

    serial = bike.serial
    cpu_version = bike.cpu_version
    board_version = bike.board_version
    owner_email = bike.owner_email
    agency_name = bike.agency_name

    try:
        db = SessionLocal()

        db_owner = get_user_by_email(db, owner_email)
        if db_owner is None:
            msg = {"code": 462, "content": "User not found."}
            logger.error(f"post_create_bike_api: {msg}")
            return BikeManagementFailMsg(**msg)

        db_agency = get_agency_by_name(db, agency_name)
        if db_agency is None:
            msg = {"code": 463, "content": "Agency not found."}
            logger.error(f"post_create_bike_api: {msg}")
            return BikeManagementFailMsg(**msg)

        owner_id = db_owner.uid
        agency_id = db_agency.aid

        db_bike = make_bike(serial, cpu_version, board_version, owner_id, agency_id)
        db.add(db_bike)
        db.commit()
        db.refresh(db_bike)
        return db_bike

    finally:
        logger.info(f"post_create_bike_api end")
        if db:
            db.close()


@router.get('/get_own')
async def get_bikes_own_api(token: str = Depends(oauth2_scheme)):
    """
    Get all bikes

    :return:
    """
    logger.info(f"get_bikes_own_api start: {token}")
    db = None

    try:
        email = get_email_from_jwt(token)

        db = SessionLocal()

        db_user = get_user_by_email(db, email)

        db_bikes = get_bikes_by_owner_id(db, db_user.uid)
        logger.info(f"get_bikes_own_api: {db_bikes}")
        return db_bikes

    finally:
        logger.info(f"get_bikes_own_api end")
        if db:
            db.close()

@router.get('/get_agency')
async def get_bikes_agency_api(token: str = Depends(oauth2_scheme)):
    """
    Get all bikes

    :return:
    """
    logger.info(f"get_bikes_agency_api start: {token}")
    db = None

    try:
        email = get_email_from_jwt(token)

        db = SessionLocal()

        db_user = get_user_by_email(db, email)

        db_agencies = get_agency_by_owner_id(db, db_user.uid)
        if db_agencies is None:
            msg = {"code": 463, "content": "Agency not found."}
            logger.error(f"get_bikes_agency_api: {msg}")
            return BikeManagementFailMsg(**msg)

        db_bikes_list = []
        for db_agency in db_agencies:
            db_bikes = get_bikes_by_agency_id(db, db_agency.aid)
            db_bikes_list.extend(db_bikes)

        logger.info(f"get_bikes_agency_api: {db_bikes_list}")
        return db_bikes_list

    finally:
        logger.info(f"get_bikes_agency_api end")
        if db:
            db.close()