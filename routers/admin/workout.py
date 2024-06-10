from fastapi import APIRouter
from fastapi import Depends

from internal.jwt_auth import admin_required
from internal.log import logger
from messages.workout import WorkoutGetTypeRequest
from models.user_workout import get_user_workout_view, get_user_workout_view_by_type

router = APIRouter()


@router.get("/list")
async def get_workout_all(user=Depends(admin_required)):
    """
    Get all workouts

    :return:
    """
    logger.info(f">>> get_workout_all start")

    db_user, db = user
    try:
        db_workouts = get_user_workout_view(db)
        logger.info(f"get_workout_all db_workouts: {db_workouts}")
        return db_workouts

    finally:
        logger.info(f">>> get_workout_all end")


@router.post("/list_by_type")
async def get_workout_by_type(req: WorkoutGetTypeRequest, user=Depends(admin_required)):
    """
    Get all workouts by type

    :return:
    """
    logger.info(f">>> get_workout_by_type start")

    db_user, db = user
    try:
        db_workouts = get_user_workout_view_by_type(db, req.ptype)
        logger.info(f"get_workout_by_type db_workouts: {db_workouts}")
        return db_workouts

    finally:
        logger.info(f">>> get_workout_by_type end")
