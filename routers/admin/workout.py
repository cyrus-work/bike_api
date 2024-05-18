from fastapi import APIRouter
from fastapi import Depends
from internal.log import logger
from internal.mysql_db import SessionLocal, get_db
from models.user_workout import get_user_workout_view

router = APIRouter()


@router.get("/list")
async def get_workout_all(db: SessionLocal = Depends(get_db)):
    """
    Get all workouts

    :return:
    """
    logger.info(f">>> get_workout_all start")

    try:
        db_workouts = get_user_workout_view(db)
        logger.info(f"get_workout_all db_workouts: {db_workouts}")
        return db_workouts

    finally:
        logger.info(f">>> get_workout_all end")
