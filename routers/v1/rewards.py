from fastapi import APIRouter, Depends

from internal.exceptions import RewardWorkoutNotExistsException
from internal.jwt_auth import get_current_user
from internal.log import logger
from models.reward_request import make_transaction_out
from models.user import User
from models.wallet import get_wallet_by_owner_id
from models.workout import get_workout_duration_not_calculated_by_user_id

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

        db_workouts = get_workout_duration_not_calculated_by_user_id(db, db_user.uid)
        logger.info(f"post_request_rewards_api db_workouts: {db_workouts}")

        if len(db_workouts) == 0:
            raise RewardWorkoutNotExistsException

        txn = make_transaction_out(db_wallet.address)

        sum_coin = 0
        for item in db_workouts:
            item.transaction_id = txn.tid
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
