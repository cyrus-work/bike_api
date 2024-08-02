from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, Depends

from internal.app_config import reward
from internal.exceptions import (
    LastWorkoutIdNotMatchException,
    LastWorkoutOwnerNotMatchException,
    BikeIdNotMatchException,
    LastWorkoutNotExistsException,
    BikeNotExistsException,
    UserNotExistsException,
)
from internal.jwt_auth import get_current_user
from internal.log import logger
from messages.workout import (
    WorkoutCreateRequest,
    WorkoutKeepRequest,
    WorkoutCreateMsg,
    WorkoutGetDurationRequest,
    WorkoutWidGetRequest,
    WorkoutGetMonthRequest,
)
from models.bike import get_bike_by_bike_no, get_bike_by_bike_no_with_status
from models.last_workout import (
    get_last_workout_by_owner_id,
)
from models.user import User
from models.workout import (
    get_workout_by_owner_id,
    make_workout,
    get_workout_by_wid,
    get_workout_duration_by_date_and_owner_id,
    get_monthly_summary_by_user,
    get_sum_of_not_calculated_token_by_user_id,
)
from models.workout_duration import get_workout_duration_sum_by_owner_id_and_date

router = APIRouter()


@router.post("/create")
async def post_workout_create_api(
    daily: WorkoutCreateRequest,
    user: User = Depends(get_current_user),
):
    """
    workout을 시작하는 API

    여기에서는 시작하는 workout의 id를 발급한다.
    :param daily: WorkoutCreateRequest 모델
    :param user: User, db 정보
    :return: WorkoutCreateMsg 모델
    """
    logger.info(f">>> post_workout_create_api start: {daily}")

    try:
        bike_serial = daily.bike_serial
        point_type = daily.ptype

        # 로그인한 사용자의 정보를 가져온다.
        db_user, db = user
        if db_user is None:
            raise UserNotExistsException

        # bike_serial로 bike 정보를 가져온다.
        db_bike = get_bike_by_bike_no_with_status(db, bike_serial)
        if db_bike is None:
            raise BikeNotExistsException

        logger.info(f"    post_workout_create_api: make_daily_production")
        # workout을 생성한다.
        db_daily = make_workout(db_user.uid, db_bike.bid, point_type)
        db.add(db_daily)
        db.commit()

        db.refresh(db_daily)
        logger.info(f"    post_workout_create_api db_daily: {db_daily}")

        return WorkoutCreateMsg(workout_id=db_daily.wid)

    finally:
        logger.info(f">>> post_workout_create_api end")


@router.post("/keep")
async def post_workout_keep_api(
    daily: WorkoutKeepRequest,
    user: User = Depends(get_current_user),
):
    """
    workout을 유지하는 API

    :param daily: WorkoutKeepRequest 모델
    :param user: User, db 정보
    :return: JSONResponse
    """
    logger.info(f">>> post_workout_keep_api start: {daily}")

    coin = 0
    point = 0
    try:

        wid = daily.wid
        bike_serial = daily.bike_serial
        energy = daily.energy
        calorie = daily.calorie
        duration = daily.running_time

        db_user, db = user

        db_last_workout = get_last_workout_by_owner_id(db, db_user.uid)
        if db_last_workout is None:
            raise LastWorkoutNotExistsException

        logger.info(f"    post_workout_keep_api db_workout: {db_last_workout}")

        if wid != db_last_workout.wid:
            raise LastWorkoutIdNotMatchException

        if db_user.uid != db_last_workout.owner_id:
            raise LastWorkoutOwnerNotMatchException

        db_bike = get_bike_by_bike_no_with_status(db, bike_serial)

        if db_last_workout.bid != db_bike.bid:
            raise BikeIdNotMatchException

        # 마지막 운동 정보를 가져온다.
        db_workout = get_workout_by_wid(db, db_last_workout.wid)

        db_workout.energy = Decimal(energy)
        db_workout.calorie = Decimal(calorie)
        duration_sec = duration
        db_workout.updated_at = datetime.now()

        # coin, point 계산
        minute_diff = int(duration_sec / 60)
        if minute_diff < 3:
            logger.info(f"    post_workout_keep_api invalid minute_diff: {minute_diff}")
            coin = 0
            point = 0
        else:
            logger.info(f"    post_workout_keep_api valid minute_diff: {minute_diff}")
            if db_workout.ptype == 0:
                coin = minute_diff * reward["token"]
            elif db_workout.ptype == 1:
                point = round(minute_diff * reward["point"])

        db_workout.token = coin
        db_workout.point = point
        db_workout.duration = minute_diff
        db_workout.duration_sec = duration_sec

        db.merge(db_workout)
        db.commit()

        db.refresh(db_workout)
        logger.info(f"    post_workout_keep_api db_workout: {db_workout}")
        return {"message": "update success"}

    finally:
        logger.info(f">>> post_workout_keep_api end")


@router.post("/get_workout")
async def post_get_workout_api(user: User = Depends(get_current_user)):
    """
    workout을 조회하는 API

    :param daily: WorkoutGetRequest 모델
    :param user: User, db 정보
    :return: WorkoutCreateMsg 모델
    """
    logger.info(f">>> post_get_workout_api start")

    try:
        db_user, db = user

        db_workout = get_workout_by_owner_id(db, db_user.uid)

        logger.info(f"    post_get_workout_api db_workout: {db_workout}")
        return db_workout

    finally:
        logger.info(f">>> post_get_workout_api end")


@router.post("/get_workout_wid")
async def post_get_workout_with_wid__api(
    daily: WorkoutWidGetRequest, user: User = Depends(get_current_user)
):
    """
    workout을 wid로 조회하는 API

    :param daily: WorkoutGetRequest 모델
    :param user: User, db 정보
    :return: WorkoutCreateMsg 모델
    """
    logger.info(f">>> post_get_workout_with_wid__api start: {daily}")

    try:
        wid = daily.wid

        db_user, db = user

        db_workout = get_workout_by_wid(db, wid)

        logger.info(f"    post_get_workout_api db_workout: {db_workout}")
        return db_workout

    finally:
        logger.info(f">>> post_get_workout_api end")


@router.post("/get_workout_duration")
async def post_get_workout_duration_api(
    daily: WorkoutGetDurationRequest, user: User = Depends(get_current_user)
):
    """
    workout duration을 조회하는 API
    시작 날자와 종료 날자를 받아서 조회한다.
    종료 날자가 없으면 오늘 날자로 조회한다.

    :param daily: WorkoutGetDurationRequest 모델
    :param user: User, db 정보
    :return: WorkoutCreateMsg 모델
    """
    logger.info(f">>> post_get_workout_duration_api start: {daily}")

    try:
        db_user, db = user

        start_date = daily.start_date

        if daily.end_date is None:
            end_date = datetime.today().date()
        else:
            end_date = daily.end_date + " 23:59:59"

        logger.info(f"    post_get_workout_duration_api: {start_date}, {end_date}")

        db_workout = get_workout_duration_by_date_and_owner_id(
            db, db_user.uid, start_date, end_date
        )
        logger.info(f"    post_get_workout_duration_api db_workout: {db_workout}")
        return db_workout

    finally:
        logger.info(f">>> post_get_workout_duration_api end")


@router.get("/get_workout_sum")
async def get_workout_duration_api(user: User = Depends(get_current_user)):
    """
    하루의 workout duration 합을 조회하는 API

    :param user: User, db 정보
    :return: WorkoutCreateMsg 모델
    """
    logger.info(f">>> get_workout_duration_api start")

    try:
        db_user, db = user

        db_workout = get_workout_duration_sum_by_owner_id_and_date(db, db_user.uid)
        logger.info(f"    get_workout_duration_api db_workout: {db_workout}")
        return db_workout

    finally:
        logger.info(f">>> get_workout_duration_api end")


@router.get("/not_calculated_token")
async def get_not_calculated_token_api(user: User = Depends(get_current_user)):
    """
    정산되지 않은 token을 조회하는 API
    """
    logger.info(f">>> get_not_calculated_token_api start")

    try:
        db_user, db = user

        db_workout = get_sum_of_not_calculated_token_by_user_id(db, db_user.uid)
        logger.info(f"    get_not_calculated_token_api db_workout: {db_workout}")
        return db_workout

    finally:
        logger.info(f">>> get_not_calculated_token_api end")


@router.post("/get_workout_by_date_and_owner_id")
async def get_workout_by_date_and_owner_id_api(
    req: WorkoutGetMonthRequest,
    user: User = Depends(get_current_user),
):
    logger.info(f">>> get_workout_by_date_and_owner_id_api start")

    try:
        month = req.month

        db_user, db = user
        owner_id = db_user.uid

        db_workout = get_monthly_summary_by_user(db, owner_id, month)
        logger.info(
            f"    get_workout_by_date_and_owner_id_api db_workout: {db_workout}"
        )
        return db_workout

    finally:
        logger.info(f">>> get_workout_by_date_and_owner_id_api end")
