from fastapi import APIRouter
from fastapi import Depends

from internal.jwt_auth import admin_required
from internal.log import logger
from messages.workout import (
    WorkoutGetTypeRequest,
    WorkoutGetSearchRequest,
    WorkoutGetUserRequest,
    WorkoutGetAllRequest,
    WorkoutGetDateRequest,
    WorkoutGetDateAdminRequest,
)
from models.user_workout import (
    get_user_workout_view,
    get_user_workout_view_by_type,
    get_user_workout_view_by_email_and_ptype,
    get_user_workout_view_by_email_and_date,
    get_count_of_workout_by_type,
    get_count_user_workout_view_by_email_and_ptype,
    get_count_user_workout_view,
    get_user_workout_view_by_email,
    get_count_user_workout_view_by_email,
    get_user_workout_view_by_email_and_date_and_ptype,
    get_count_user_workout_view_by_email_and_date_and_ptype,
    get_count_user_workout_view_by_email_and_date,
    get_user_workout_view_by_date,
    get_count_user_workout_view_by_date,
)

router = APIRouter()


@router.post("/list")
async def post_workout_all(req: WorkoutGetAllRequest, user=Depends(admin_required)):
    """
    Get all workouts

    :return:
    """
    logger.info(f">>> post_workout_all start")

    try:
        db_user, db = user

        offset = req.offset
        limit = req.limit

        db_workouts = get_user_workout_view(db, offset, limit)
        db_count = get_count_user_workout_view(db)
        logger.info(f"    get_workout_all db_workouts: {db_workouts, db_count}")
        return {"count": db_count, "data": db_workouts}

    finally:
        logger.info(f">>> get_workout_all end")


@router.post("/list_by_type")
async def get_workout_by_type(req: WorkoutGetTypeRequest, user=Depends(admin_required)):
    """
    Get all workouts by type

    :return:
    """
    logger.info(f">>> get_workout_by_type start")

    try:
        db_user, db = user

        offset = req.offset
        limit = req.limit

        db_workouts = get_user_workout_view_by_type(db, req.ptype, offset, limit)
        db_counts = get_count_of_workout_by_type(db, req.ptype)
        logger.info(f"    get_workout_by_type db_workouts: {db_workouts}, {db_counts}")
        return {"count": db_counts, "data": db_workouts}

    finally:
        logger.info(f">>> get_workout_by_type end")


@router.post("/list_by_user")
async def get_workout_by_user(req: WorkoutGetUserRequest, user=Depends(admin_required)):
    """
    운동 리스트를 사용자 이메일로 조회해서 가져옴.

    :return:
    """
    logger.info(f">>> get_workout_by_user start")

    try:
        db_user, db = user

        email = req.email
        ptype = req.ptype
        offset = req.offset
        limit = req.limit

        if ptype is None:
            db_workouts = get_user_workout_view_by_email(db, email, offset, limit)
            db_counts = get_count_user_workout_view_by_email(db, email)
        else:
            db_workouts = get_user_workout_view_by_email_and_ptype(
                db, email, ptype, offset, limit
            )
            db_counts = get_count_user_workout_view_by_email_and_ptype(db, email, ptype)
        logger.info(f"    get_workout_by_user db_workouts ptype: {ptype}")
        logger.info(f"    get_workout_by_user db_workouts: {db_workouts}, {db_counts}")
        return {"count": db_counts, "data": db_workouts}

    finally:
        logger.info(f">>> get_workout_by_user end")


@router.post("/list_by_date")
async def post_workout_by_date_api(
    req: WorkoutGetDateAdminRequest, user=Depends(admin_required)
):
    """
    Get all workouts by date

    :return:
    """
    logger.info(f">>> post_workout_by_date_api start")

    try:
        db_user, db = user

        start_date = req.start_date
        end_date = req.end_date
        offset = req.offset
        limit = req.limit

        db_workouts = get_user_workout_view_by_date(
            db, start_date, end_date, offset, limit
        )
        db_count = get_count_user_workout_view_by_date(db, start_date, end_date)
        logger.info(f"    post_workout_by_date_api db_workouts: {db_workouts}")
        return {"count": db_count, "data": db_workouts}

    finally:
        logger.info(f">>> post_workout_by_date_api end")


@router.post("/list_by_user_and_date")
async def post_workout_by_user_and_date_api(
    req: WorkoutGetSearchRequest, user=Depends(admin_required)
):
    """
    사용자의 운동 리스트를 날짜로 조회해서 가져옴.

    :return:
    """
    logger.info(f">>> post_workout_by_user_and_date_api start")

    try:
        db_user, db = user

        ptype = req.ptype
        email = req.email
        start_date = req.start_date
        offset = req.offset
        limit = req.limit

        end_date = req.end_date if req.end_date is not None else start_date

        logger.info(
            f"    post_workout_by_user_and_date_api infos: "
            f"{ptype}, {email}, {start_date}, {end_date}, {offset}, {limit}"
        )

        if ptype is None:
            db_workouts = get_user_workout_view_by_email_and_date(
                db, email, start_date, end_date, offset, limit
            )
            db_count = get_count_user_workout_view_by_email_and_date(
                db, email, start_date, end_date
            )
        else:
            db_workouts = get_user_workout_view_by_email_and_date_and_ptype(
                db, email, start_date, end_date, ptype, offset, limit
            )
            db_count = get_count_user_workout_view_by_email_and_date_and_ptype(
                db, email, start_date, end_date, ptype
            )
        logger.info(f"    post_workout_by_user_and_date_api db_workouts: {db_workouts}")
        return {"count": db_count, "data": db_workouts}

    finally:
        logger.info(f">>> post_workout_by_user_and_date_api end")
