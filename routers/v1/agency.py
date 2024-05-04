import traceback

from fastapi import APIRouter
from starlette.responses import JSONResponse

from internal.log import logger
from internal.mysql_db import SessionLocal
from messages.agency import AgencyCreateRequest, AgencyInfo, AgencyManagementFailMsg
from models.agency import make_agency, get_agency_by_email
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