import traceback
from datetime import datetime

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from internal.jwt_auth import oauth2_scheme, get_email_from_jwt
from internal.log import logger
from internal.mysql_db import SessionLocal
from messages.daily_production import DailyProductionCreateRequest, DailyProductionRequest
from models.daily_prodution import get_daily_production_by_wid, make_daily_production
from models.user import get_user_by_email
from models.wallet import get_wallet_by_address, get_wallet_by_owner_id

router = APIRouter()


@router.post("/set_daily_production")
async def post_set_daily_production_api(daily: DailyProductionCreateRequest, token: str = Depends(oauth2_scheme)):
    logger.info(f"post_set_daily_production_api start: {daily}")
    db = None

    email = get_email_from_jwt(token)

    bike_serial = daily.bike_serial
    coin = daily.coin
    point = daily.point
    watt = daily.watt
    duration = daily.duration

    try:
        db = SessionLocal()

        db_user = get_user_by_email(db, email)
        if db_user is None:
            msg = {"code": 462, "content": "User not found."}
            logger.error(f"post_set_daily_production_api: {msg}")
            return JSONResponse(status_code=410, content=msg)

        db_wallet = get_wallet_by_owner_id(db, db_user.uid)
        if db_wallet is None:
            msg = {"code": 462, "content": "Wallet not found."}
            logger.error(f"post_set_daily_production_api: {msg}")
            return JSONResponse(status_code=410, content=msg)

        wallet = db_wallet.address
        db_wallet = get_wallet_by_address(db, wallet)
        if db_wallet is None:
            msg = {"code": 462, "content": "Wallet not found."}
            logger.error(f"post_set_daily_production_api: {msg}")
            return JSONResponse(status_code=410, content=msg)

        wallet_id = db_wallet.wid
        db_daily = get_daily_production_by_wid(db, wallet_id)
        if db_daily is None:
            logger.info(f"post_set_daily_production_api: make_daily_production")
            duration_obj = datetime.strptime(duration, "%H:%M:%S").time()
            db_daily = make_daily_production(wallet_id, bike_serial, coin, point, watt, duration_obj)
            db.add(db_daily)
            db.flush()
            db.refresh(db_daily)
        else:
            logger.info(f"post_set_daily_production_api: update_daily_production")
            db_daily.bike_serial = bike_serial
            db_daily.coin = coin
            db_daily.point = point
            db_daily.watt = watt
            db_daily.duration = datetime.strptime(duration, "%H:%M:%S").time()

        db.merge(db_daily)
        db.commit()

        return {"message": "register success"}

    except Exception as _:
        logger.error(f"post_set_daily_production_api error: {traceback.format_exc()}")
        msg = {"code": 461, "content": "Register failed."}
        logger.error(f"post_set_daily_production_api: {msg}")
        return JSONResponse(status_code=410, content=msg)

    finally:
        logger.info(f"post_set_daily_production_api end")
        if db:
            db.close()


@router.post("/get_daily_production")
async def post_get_daily_production_api(daily: DailyProductionRequest):
    logger.info(f"post_get_daily_production_api start: {daily}")
    db = None

    wallet = daily.wallet_address

    db_wallet = get_wallet_by_address(db, wallet)
    if db_wallet is None:
        msg = {"code": 462, "content": "Wallet not found."}
        logger.error(f"post_get_daily_production_api: {msg}")
        return JSONResponse(status_code=410, content=msg)

    db_daily = get_daily_production_by_wid(db, db_wallet.wid)
    if db_daily is None:
        msg = {"code": 462, "content": "Daily production not found."}
        logger.error(f"post_get_daily_production_api: {msg}")
        return JSONResponse(status_code=410, content=msg)

    logger.info(f"post_get_daily_production_api: {db_daily}")
    return db_daily

    try:
        db = SessionLocal()

        return {"message": "register success"}

    except Exception as _:
        logger.error(f"post_get_daily_production_api error: {traceback.format_exc()}")
        msg = {"code": 461, "content": "Register failed."}
        logger.error(f"post_get_daily_production_api: {msg}")
        return JSONResponse(status_code=410, content=msg)

    finally:
        logger.info(f"post_get_daily_production_api end")
        if db:
            db.close()
