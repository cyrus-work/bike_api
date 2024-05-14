from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, Depends

from internal.exceptions import (
    UserNotExistsException,
    BikeNotExistsException,
    LastWorkoutNotExistsException,
    LastWorkoutIdNotMatchException,
    WorkoutLastOwnerNotMatchException,
)
from internal.jwt_auth import oauth2_scheme, get_email_from_jwt, decode_data_from_jwt
from internal.log import logger
from internal.mysql_db import SessionLocal, get_db
from messages.workout import (
    WorkoutCreateMsg,
    WorkoutGetRequest,
    WorkoutGetDurationRequest,
    WorkoutDataRequest,
)
from models.bike import get_bike_by_bike_no
from models.last_workout import get_last_workout_by_owner_id
from models.user import get_user_by_email
from models.workout import (
    get_workout_by_owner_id,
    make_workout,
    get_workout_by_date_and_owner_id,
    get_workout_by_wid,
    get_workout_duration_by_date_and_owner_id,
)
from models.workout_duration import get_workout_duration_sum_by_owner_id_and_date

router = APIRouter()


@router.post("/create")
async def post_workout_create_api(
    daily: WorkoutDataRequest,
    db: SessionLocal = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    """
    workout을 시작하는 API

    여기에서는 시작하는 workout의 id를 발급한다.

    :param daily: WorkoutCreateRequest 모델
    :param db: SessionLocal
    :param token: JWT 토큰
    :return: WorkoutCreateMsg 모델
    """
    logger.info(f">>> post_workout_create_api start: {daily}")

    try:
        email = get_email_from_jwt(token)

        data_jwt = daily.data
        data = decode_data_from_jwt(data_jwt)
        logger.info(f"post_workout_create_api data: {data}")

        bike_serial = data["bike_serial"]
        point_type = data["ptype"]

        # 로그인한 사용자의 정보를 가져온다.
        db_user = get_user_by_email(db, email)
        if db_user is None:
            raise UserNotExistsException

        db_bike = get_bike_by_bike_no(db, bike_serial)
        if db_bike is None:
            raise BikeNotExistsException

        logger.info(f"post_workout_create_api: make_daily_production")
        db_daily = make_workout(db_user.uid, db_bike.bid, point_type)
        db.add(db_daily)
        db.flush()
        db.refresh(db_daily)

        db.merge(db_daily)
        db.commit()

        return WorkoutCreateMsg(workout_id=db_daily.wid)

    finally:
        logger.info(f">>> post_workout_create_api end")


@router.post("/keep")
async def post_workout_keep_api(
    daily: WorkoutDataRequest,
    db: SessionLocal = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    """
    workout을 유지하는 API

    :param daily: WorkoutKeepRequest 모델
    :param db: SessionLocal
    :param token: JWT 토큰
    :return: JSONResponse
    """
    logger.info(f">>> post_workout_keep_api start: {daily}")

    try:
        email = get_email_from_jwt(token)

        data_jwt = daily.data
        data = decode_data_from_jwt(data_jwt)

        wid = data["wid"]
        bike_serial = data["bike_serial"]
        energy = data["energy"]
        calorie = data["calorie"]

        db_user = get_user_by_email(db, email)

        db_last_workout = get_last_workout_by_owner_id(db, db_user.uid)
        if db_last_workout is None:
            raise LastWorkoutNotExistsException
        logger.info(f"post_workout_keep_api db_workout: {db_last_workout}")

        if wid != db_last_workout.wid:
            raise LastWorkoutIdNotMatchException

        if db_user.uid != db_last_workout.owner_id:
            raise WorkoutLastOwnerNotMatchException

        db_workout = get_workout_by_wid(db, db_last_workout.wid)

        db_workout.energy = Decimal(energy)
        db_workout.calorie = Decimal(calorie)
        # db_workout.end_time = datetime.now()

        db.merge(db_workout)
        db.commit()

        db.refresh(db_workout)
        logger.info(f"post_workout_keep_api db_workout: {db_workout}")

        return {"message": "update success"}

    finally:
        logger.info(f">>> post_workout_keep_api end")


@router.post("/get_workout")
async def post_get_workout_api(
    daily: WorkoutGetRequest,
    db: SessionLocal = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    """
    workout을 조회하는 API

    :param daily: WorkoutGetRequest 모델
    :param db: SessionLocal
    :param token: JWT 토큰
    :return: WorkoutCreateMsg 모델
    """
    logger.info(f"post_get_workout_api start: {daily}")

    try:
        email = get_email_from_jwt(token)
        date = daily.date

        db_user = get_user_by_email(db, email)

        if date is not None:
            db_workout = get_workout_by_date_and_owner_id(db, db_user.uid, date)
        else:
            db_workout = get_workout_by_owner_id(db, db_user.uid)

        logger.info(f"post_get_workout_api db_workout: {db_workout}")
        return db_workout

    finally:
        logger.info(f">>> post_get_workout_api end")


@router.post("/get_workout_duration")
async def post_get_workout_duration_api(
    daily: WorkoutGetDurationRequest,
    db: SessionLocal = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    """
    workout duration을 조회하는 API
    시작 날자와 종료 날자를 받아서 조회한다.
    종료 날자가 없으면 오늘 날자로 조회한다.

    :param daily: WorkoutGetDurationRequest 모델
    :param db: SessionLocal
    :param token: JWT 토큰
    :return: WorkoutCreateMsg 모델
    """
    logger.info(f">>> post_get_workout_duration_api start: {daily}")

    try:
        email = get_email_from_jwt(token)

        start_date = daily.start_date

        if daily.end_date is None:
            end_date = datetime.today()
        else:
            end_date = daily.end_date

        db_user = get_user_by_email(db, email)

        db_workout = get_workout_duration_by_date_and_owner_id(
            db, db_user.uid, start_date, end_date
        )
        logger.info(f"post_get_workout_duration_api db_workout: {db_workout}")
        return db_workout

    finally:
        logger.info(f">>> post_get_workout_duration_api end")


@router.get("/get_workout_sum")
async def get_workout_duration_api(
    db: SessionLocal = Depends(get_db), token: str = Depends(oauth2_scheme)
):
    """
    하루의 workout duration을 조회하는 API
    """
    logger.info(f">>> get_workout_duration_api start")

    try:
        email = get_email_from_jwt(token)

        db_user = get_user_by_email(db, email)

        db_workout = get_workout_duration_sum_by_owner_id_and_date(db, db_user.uid)
        logger.info(f"get_workout_duration_api db_workout: {db_workout}")
        return db_workout

    finally:
        logger.info(f">>> get_workout_duration_api end")


@router.get("/get_workout_by_date_and_owner_id")
async def get_workout_by_date_and_owner_id_api(
    db: SessionLocal = Depends(get_db), token: str = Depends(oauth2_scheme)
):
    logger.info(f">>> get_workout_by_date_and_owner_id_api start")

    try:
        email = get_email_from_jwt(token)

        db_user = get_user_by_email(db, email)
        owner_id = db_user.uid

        db_workout = get_workout_by_date_and_owner_id(db, owner_id)
        logger.info(f"get_workout_by_date_and_owner_id_api db_workout: {db_workout}")
        return db_workout

    finally:
        logger.info(f">>> get_workout_by_date_and_owner_id_api end")
