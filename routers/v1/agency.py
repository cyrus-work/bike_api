import traceback

from fastapi import APIRouter, Depends

from internal.jwt_auth import oauth2_scheme, get_email_from_jwt
from internal.log import logger
from internal.mysql_db import SessionLocal
from internal.utils import model_to_dict
from messages.agency import AgencyCreateRequest, AgencyInfo, AgencyManagementFailMsg
from models.agency import make_agency, get_agency_by_owner_id
from models.user import get_user_by_email

router = APIRouter()


@router.get("/")
async def get_agency_api():
    return {"message": "agency api"}


@router.post("/create",
             responses={
                 200: {"model": AgencyInfo},
                 461: {"model": AgencyManagementFailMsg},
             }, )
async def post_create_agency_api(agency: AgencyCreateRequest):
    """
    Create agency

    :param agency:
    :return:
    """
    logger.info(f"post_create_agency_api start: {agency}")
    db = None

    owner_email = agency.owner_email
    address = agency.address
    phone = agency.phone
    name = agency.name

    try:
        db = SessionLocal()

        db_owner = get_user_by_email(db, owner_email)
        if db_owner is None:
            msg = {"code": 462, "content": "User not found."}
            logger.error(f"post_create_agency_api: {msg}")
            return AgencyManagementFailMsg(**msg)

        owner_id = db_owner.uid

        db_agency = make_agency(owner_id, name, address, phone)
        db.add(db_agency)
        db.commit()
        db.refresh(db_agency)
        return AgencyInfo(**db_agency.__dict__)

    except Exception as _:
        logger.error(f"post_create_agency_api error: {traceback.format_exc()}")
        msg = {"code": 461, "content": "Create agency failed."}
        logger.error(f"post_create_agency_api: {msg}")
        return AgencyManagementFailMsg(**msg)

    finally:
        logger.info(f"post_create_agency_api end")
        if db:
            db.close()


@router.post('/get_own')
async def get_agency_by_owner_api(token: str = Depends(oauth2_scheme)):
    """
    Get agency by owner email

    :param token:
    :return:
    """
    logger.info(f"get_agency_by_owner_api start")
    db = None

    try:
        db = SessionLocal()

        email = get_email_from_jwt(token)

        db_user = get_user_by_email(db, email)

        db_agency = get_agency_by_owner_id(db, db_user.uid)
        if db_agency is None:
            msg = {"code": 463, "content": "Agency not found."}
            logger.error(f"get_agency_by_owner_api: {msg}")
            return AgencyManagementFailMsg(**msg)
        logger.info(f"get_agency_by_owner_api: {db_agency}")

        return [AgencyInfo(**model_to_dict(agency)) for agency in db_agency]


    except Exception as _:
        logger.error(f"get_agency_by_owner_api error: {traceback.format_exc()}")
        msg = {"code": 461, "content": "Get agency failed."}
        logger.error(f"get_agency_by_owner_api: {msg}")
        return AgencyManagementFailMsg(**msg)

    finally:
        logger.info(f"get_agency_by_owner_api end")
        if db:
            db.close()
