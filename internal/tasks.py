from datetime import datetime

from internal.blockchain import (
    get_check_sum_address,
    reward_transfer,
    web3,
    private_key,
)
from internal.log import logger
from internal.mysql_db import SessionLocal
from internal.utils import is_valid_polygon_address
from models.reward_request import get_txn_out_by_txn_hash_is_null


def schedule_token_transfer():
    logger.info(f"schedule_token_transfer: Task is running at - {datetime.now}")

    from_address = web3.eth.account.from_key(private_key).address
    nonce = web3.eth.get_transaction_count(from_address)

    db = None

    try:
        db = SessionLocal()

        db_workouts = get_txn_out_by_txn_hash_is_null(db)
        logger.info(f"schedule_token_transfer: db_workouts - {db_workouts}")

        for db_workout in db_workouts:
            logger.info(
                f"schedule_token_transfer: db_workout wallet - {db_workout.wallet}"
            )
            if is_valid_polygon_address(db_workout.wallet) is False:
                logger.error(
                    f"uid - {db_workout.uid}, Invalid address - {db_workout.wallet}"
                )
                continue

            # 직접 블록체인 네트워크에 요청을 보내서 토큰을 전송한다.
            to_address = get_check_sum_address(db_workout.wallet)
            amount = db_workout.amount * 10**18
            txn_hash = reward_transfer(to_address, amount, nonce)
            logger.info(f"schedule_token_transfer: txn_hash - {txn_hash}")

            db_workout.txn_hash = txn_hash
            db_workout.status = 1
            db.merge(db_workout)
            db.flush()

            nonce += 1

        db.commit()
        logger.info(f"schedule_token_transfer: Task is finished at - {datetime.now}")

    finally:
        db.close()
        logger.info(f"schedule_token_transfer: Task is finished at - {datetime.now}")
