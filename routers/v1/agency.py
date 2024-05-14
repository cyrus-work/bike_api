from fastapi import APIRouter, Depends

from internal.exceptions import AgencyNotExistsException
from internal.jwt_auth import oauth2_scheme, get_email_from_jwt
from internal.log import logger
from internal.mysql_db import SessionLocal
from internal.utils import model_to_dict
from messages.agency import AgencyCreateRequest, AgencyInfo
from models.agency import make_agency, get_agency_by_owner_id
from models.user import get_user_by_email

router = APIRouter()


@router.post(
    "/create",
)
async def post_create_agency_api(
    agency: AgencyCreateRequest, db: SessionLocal = Depends(SessionLocal)
):
    """
    Create agency

    :param agency:
    :param db:
    :return:
    """
    logger.info(f">>> post_create_agency_api start: {agency}")

    try:
        owner_email = agency.owner_email
        address = agency.address
        phone = agency.phone
        name = agency.name

        db_owner = get_user_by_email(db, owner_email)
        if db_owner is None:
            raise AgencyNotExistsException

        owner_id = db_owner.uid

        db_agency = make_agency(owner_id, name, address, phone)
        db.add(db_agency)
        db.commit()
        db.refresh(db_agency)
        return AgencyInfo(**db_agency.__dict__)

    finally:
        logger.info(f">>> post_create_agency_api end")


@router.post("/get_own")
async def get_agency_by_owner_api(
    db: SessionLocal = Depends(SessionLocal), token: str = Depends(oauth2_scheme)
):
    """
    Get agency by owner email

    :param token:
    :param db:
    :return:
    """
    logger.info(f">>> get_agency_by_owner_api start")

    try:
        email = get_email_from_jwt(token)

        db_user = get_user_by_email(db, email)

        db_agency = get_agency_by_owner_id(db, db_user.uid)
        if db_agency is None:
            raise AgencyNotExistsException

        logger.info(f"get_agency_by_owner_api: {db_agency}")

        return [AgencyInfo(**model_to_dict(agency)) for agency in db_agency]

    finally:
        logger.info(f">>> get_agency_by_owner_api end")
