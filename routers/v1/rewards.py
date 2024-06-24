from datetime import datetime

from fastapi import APIRouter, Depends

from internal.exceptions import RewardWorkoutNotExistsException
from internal.jwt_auth import get_current_user
from internal.log import logger
from messages.wallets import WalletTxnGetMonthReq
from models.owner_token_point import get_workout_summary_by_email
from models.point_out import make_point_out, get_point_out_by_pid
from models.transaction_out import (
    make_transaction_out,
    get_txns_by_owner_id,
)
from models.user import User
from models.wallet import get_wallet_by_owner_id
from models.workout import (
    get_workout_list_not_calculated_coin_by_user_id,
    get_workout_list_not_calculated_point_by_user_id,
)

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
        logger.info(f"    post_request_rewards_api db_workouts: {db_workouts}")

        # 계산할 리워드가 없는 경우.
        if len(db_workouts) == 0:
            raise RewardWorkoutNotExistsException

        txn = make_transaction_out(db_wallet.address, db_user.uid)

        sum_coin = 0
        for item in db_workouts:
            item.transaction_id = txn.tid
            item.operating_at = datetime.now()
            item.status = 1
            sum_coin += item.token
            db.merge(item)
            db.flush()

        txn.amount = sum_coin
        db.add(txn)
        db.commit()
        db.refresh(txn)

        logger.info(f"    post_request_rewards_api txn: {txn}")
        return txn

    finally:
        logger.info(f">>> post_request_rewards_api end")


@router.post("/request_point")
async def post_request_point_rewards_api(user: User = Depends(get_current_user)):
    """
    Get all rewards

    :return:
    """
    logger.info(f">>> post_request_point_rewards_api start")

    try:
        db_user, db = user

        db_wallet = get_wallet_by_owner_id(db, db_user.uid)

        db_workouts = get_workout_list_not_calculated_point_by_user_id(db, db_user.uid)
        logger.info(f"    post_request_point_rewards_api db_workouts: {db_workouts}")

        # 계산할 리워드가 없는 경우.
        if len(db_workouts) == 0:
            raise RewardWorkoutNotExistsException

        txn = make_point_out(db_wallet.address, db_user.uid)

        sum_point = 0
        for item in db_workouts:
            item.transaction_id = txn.pid
            item.operating_at = datetime.now()
            sum_point += item.point
            item.status = 1
            db.merge(item)
            db.flush()

        txn.amount = min(sum_point, 2000)
        db.add(txn)
        db.commit()
        db.refresh(txn)

        logger.info(f"    post_request_point_rewards_api txn: {txn}")
        return txn

    finally:
        logger.info(f">>> post_request_point_rewards_api end")


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

        db_workout_summary = get_workout_summary_by_email(db, db_user.email)
        logger.info(
            f"    post_total_rewards_api db_workout_summary: {db_workout_summary}"
        )
        return {
            "email": db_user.email,
            "point": db_workout_summary.total_point,
            "token": db_workout_summary.total_token,
            "duration": db_workout_summary.total_duration,
        }

    finally:
        logger.info(f">>> post_total_rewards_api end")


def make_start_end_data_month(month_str: str):
    year, month = map(int, month_str.split("-"))

    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month + 1, 1)

    return start_date, end_date


@router.post("/point_txn_list_by_owner_id")
async def post_txn_list_by_owner_id_api(
    req: WalletTxnGetMonthReq, user: User = Depends(get_current_user)
):
    """
    Get all rewards

    :return:
    """
    logger.info(f">>> post_txn_list_by_owner_id_api start")

    try:
        db_user, db = user

        start_date, end_date = make_start_end_data_month(req.month)

        db_txns = get_point_out_by_pid(db, db_user.uid, start_date, end_date)

        logger.info(f"    post_txn_list_by_owner_id_api db_txns: {db_txns}")
        if db_txns is None:
            db_txns = []
        return db_txns

    finally:
        logger.info(f">>> post_txn_list_by_owner_id_api end")


@router.post("/coin_txn_list_by_owner_id")
async def post_txn_list_by_owner_id_and_coint_api(
    req: WalletTxnGetMonthReq, user: User = Depends(get_current_user)
):
    """
    Get all rewards

    :param req: WalletTxnGetMonthReq
    :param user: User
    :return:
    """
    logger.info(f">>> post_txn_list_by_owner_id_and_coint_api start")

    try:
        db_user, db = user

        start_date, end_date = make_start_end_data_month(req.month)

        db_txns = get_txns_by_owner_id(db, db_user.uid, start_date, end_date)

        logger.info(f"    post_txn_list_by_owner_id_and_coint_api db_txns: {db_txns}")
        if db_txns is None:
            db_txns = []
        return db_txns

    finally:
        logger.info(f">>> post_txn_list_by_owner_id_and_coint_api end")
