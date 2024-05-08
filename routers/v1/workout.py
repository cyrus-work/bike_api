import traceback
from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from internal.jwt_auth import oauth2_scheme, get_email_from_jwt
from internal.log import logger
from internal.mysql_db import SessionLocal
from messages.workout import WorkoutCreateRequest, WorkoutKeepRequest, WorkoutCreateMsg, WorkoutGetRequest
from models.bike import get_bike_by_bike_no
from models.user import get_user_by_email
from models.workout import get_workout_by_owner_id, make_workout, get_workout_by_did, get_workout_by_date

router = APIRouter()


@router.post("/create")
async def post_workout_create_api(daily: WorkoutCreateRequest, token: str = Depends(oauth2_scheme)):
    """
    workout을 시작하는 API

    여기에서는 시작하는 workout의 id를 발급한다.
    :param daily: WorkoutCreateRequest 모델
    :param token: JWT 토큰
    :return: WorkoutCreateMsg 모델
    """
    logger.info(f"post_workout_create_api start: {daily}")
    db = None

    email = get_email_from_jwt(token)
    bike_serial = daily.bike_serial
    point_type = daily.ptype

    try:
        db = SessionLocal()

        # 로그인한 사용자의 정보를 가져온다.
        db_user = get_user_by_email(db, email)
        if db_user is None:
            msg = {"code": 462, "content": "User not found."}
            logger.error(f"post_workout_create_api: {msg}")
            return JSONResponse(status_code=410, content=msg)

        db_bike = get_bike_by_bike_no(db, bike_serial)
        if db_bike is None:
            msg = {"code": 462, "content": "Bike not found."}
            logger.error(f"post_workout_create_api: {msg}")
            return JSONResponse(status_code=410, content=msg)

        logger.info(f"post_workout_create_api: make_daily_production")
        db_daily = make_workout(db_user.uid, db_bike.bid, point_type)
        db.add(db_daily)
        db.flush()
        db.refresh(db_daily)

        db.merge(db_daily)
        db.commit()

        return WorkoutCreateMsg(workout_id=db_daily.did)

    except Exception as _:
        logger.error(f"post_workout_create_api error: {traceback.format_exc()}")
        msg = {"code": 461, "content": "Register failed."}
        logger.error(f"post_workout_create_api: {msg}")
        return JSONResponse(status_code=410, content=msg)

    finally:
        logger.info(f"post_workout_create_api end")
        if db:
            db.close()


@router.post("/keep")
async def post_workout_keep_api(daily: WorkoutKeepRequest, token: str = Depends(oauth2_scheme)):
    logger.info(f"post_workout_keep_api start: {daily}")
    db = None

    try:
        email = get_email_from_jwt(token)

        wid = daily.wid
        bike_serial = daily.bike_serial
        energy = daily.energy
        calorie = daily.calorie

        db = SessionLocal()

        db_user = get_user_by_email(db, email)
        if db_user is None:
            msg = {"code": 462, "content": "User not found."}
            logger.error(f"post_workout_keep_api: {msg}")
            return JSONResponse(status_code=410, content=msg)

        db_workout = get_workout_by_did(db, did=wid)
        if db_workout is None:
            logger.info(f"post_workout_keep_api: make_daily_production")
            msg = {"code": 462, "content": "workout date not found."}
            logger.error(f"post_workout_keep_api: {msg}")
            return JSONResponse(status_code=410, content=msg)
        logger.info(f"post_workout_keep_api db_workout: {db_workout}")

        if wid != db_workout.wid:
            msg = {"code": 462, "content": "workout date not match bike serial."}
            logger.error(f"post_workout_keep_api: {msg}")
            return JSONResponse(status_code=410, content=msg)

        if db_user.uid != db_workout.owner_id:
            msg = {"code": 462, "content": "workout date not match user."}
            logger.error(f"post_workout_keep_api: {msg}")
            return JSONResponse(status_code=410, content=msg)

        db_workout.energy = Decimal(energy)
        db_workout.calorie = Decimal(calorie)
        db_workout.end_time = datetime.now()

        db.merge(db_workout)
        db.commit()

        return {"message": "update success"}

    except Exception as _:
        logger.error(f"post_workout_keep_api error: {traceback.format_exc()}")
        msg = {"code": 461, "content": "Register failed."}
        logger.error(f"post_workout_keep_api: {msg}")
        return JSONResponse(status_code=410, content=msg)

    finally:
        logger.info(f"post_workout_keep_api end")
        if db:
            db.close()


@router.post("/get_workout")
async def post_get_workout_api(daily: WorkoutGetRequest, token: str = Depends(oauth2_scheme)):
    logger.info(f"post_get_workout_api start: {daily}")
    db = None

    try:
        email = get_email_from_jwt(token)

        date = daily.date

        db = SessionLocal()

        db_user = get_user_by_email(db, email)
        if db_user is None:
            msg = {"code": 462, "content": "User not found."}
            logger.error(f"post_get_workout_api: {msg}")
            return JSONResponse(status_code=410, content=msg)

        if date is not None:
            db_workout = get_workout_by_date(db, db_user.uid, date)
        else:
            db_workout = get_workout_by_owner_id(db, db_user.uid)

        logger.info(f"post_get_workout_api: {db_workout}")
        return db_workout

    except Exception as _:
        logger.error(f"post_get_workout_api error: {traceback.format_exc()}")
        msg = {"code": 461, "content": "Register failed."}
        logger.error(f"post_get_workout_api: {msg}")
        return JSONResponse(status_code=410, content=msg)

    finally:
        logger.info(f"post_get_workout_api end")
        if db:
            db.close()
