from fastapi import APIRouter

from internal.log import logger
from internal.mysql_db import SessionLocal
from messages.bike import BikeCreateRequest, BikeManagementFailMsg, BikeCreateMsg
from models.agency import get_agency_by_name
from models.bike import make_bike, Bike
from models.user import get_user_by_email

router = APIRouter()


@router.get("/")
async def get_bike_api():
    return {"message": "bike api"}


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

    except Exception as e:
        logger.error(f"post_create_bike_api error: {e}")
        msg = {"code": 461, "content": "Create bike failed."}
        logger.error(f"post_create_bike_api: {msg}")
        return BikeManagementFailMsg(**msg)

    finally:
        logger.info(f"post_create_bike_api end")
        if db:
            db.close()
