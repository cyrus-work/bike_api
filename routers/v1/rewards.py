from fastapi import APIRouter, Depends

from internal.jwt_auth import oauth2_scheme, get_email_from_jwt
from internal.mysql_db import SessionLocal, get_db
from internal.log import logger
from models.reward import get_rewards_sum_by_owner_id

from models.user import get_user_by_email

router = APIRouter()


@router.post("/sum")
async def post_sum_rewards_api(
    db: SessionLocal = Depends(get_db), token: str = Depends(oauth2_scheme)
):
    """
    Get all rewards

    :return:
    """
    logger.info(f">>> post_sum_rewards_api start")

    try:
        email = get_email_from_jwt(token)

        db_user = get_user_by_email(db, email)

        db_rewards = get_rewards_sum_by_owner_id(db, db_user.uid)
        logger.info(f"post_sum_rewards_api db_rewards: {db_rewards}")
        return db_rewards

    finally:
        logger.info(f">>> post_sum_rewards_api end")
