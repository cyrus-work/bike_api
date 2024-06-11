from datetime import datetime

from fastapi import APIRouter, Depends

from internal.exceptions import RewardWorkoutNotExistsException
from internal.jwt_auth import get_current_user
from internal.log import logger
from models.transaction_out import make_transaction_out
from models.user import User
from models.wallet import get_wallet_by_owner_id
from models.workout import get_workout_list_not_calculated_coin_by_user_id
from models.workout_summary import get_summary_by_email

router = APIRouter()


@router.post("/request")
async def post_request_rewards_api(user: User = Depends(get_current_user)):
    """
    Get all rewards

    :return:
    """
    logger.info(f">>> post_request_rewards_api start")

    try:
        db_user, db = user

        db_wallet = get_wallet_by_owner_id(db, db_user.uid)

        db_workouts = get_workout_list_not_calculated_coin_by_user_id(db, db_user.uid)
        logger.info(f"post_request_rewards_api db_workouts: {db_workouts}")

        # 계산할 리워드가 없는 경우.
        if len(db_workouts) == 0:
            raise RewardWorkoutNotExistsException

        txn = make_transaction_out(db_wallet.address)

        sum_coin = 0
        for item in db_workouts:
            item.transaction_id = txn.tid
            item.operating_at = datetime.now()
            sum_coin += item.token
            db.merge(item)
            db.flush()

        txn.amount = sum_coin
        db.add(txn)
        db.commit()
        db.refresh(txn)

        return txn

    finally:
        logger.info(f">>> post_request_rewards_api end")


@router.post("/total")
async def post_total_rewards_api(user: User = Depends(get_current_user)):
    """
    Get total rewards
    정산받은 것 + 정산받지 않은 것

    :return:
    """
    logger.info(f">>> post_total_rewards_api start")

    try:
        db_user, db = user
        logger.info(f"post_total_rewards_api db_user: {db_user}")

        db_workout_summary = get_summary_by_email(db, db_user.email)
        return db_workout_summary

    finally:
        logger.info(f">>> post_total_rewards_api end")
