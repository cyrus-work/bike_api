import traceback
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
from models.transaction_out import (
    get_txn_out_by_txn_hash_is_null,
    get_txn_out_by_status_not_clear,
)


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
            db_workout.operating_at = datetime.now()
            db.merge(db_workout)
            db.flush()

            nonce += 1

        db.commit()
        logger.info(f"schedule_token_transfer: Task is finished at - {datetime.now}")

    finally:
        db.close()
        logger.info(f"schedule_token_transfer: Task is finished at - {datetime.now}")


def schedule_token_checker():
    logger.info(f"schedule_token_checker: Task is running at - {datetime.now}")

    from_address = web3.eth.account.from_key(private_key).address
    nonce = web3.eth.get_transaction_count(from_address)

    db = None

    try:
        db = SessionLocal()

        db_txns = get_txn_out_by_status_not_clear(db)
        logger.info(f"schedule_token_checker: check txn hashes - {db_txns}")

        for db_txn in db_txns:
            logger.info(f"schedule_token_checker: txn wallet - {db_txn.wallet}")
            if is_valid_polygon_address(db_txn.wallet) is False:
                logger.error(f"uid - {db_txn.uid}, Invalid address - {db_txn.wallet}")
                continue

            # 직접 블록체인 네트워크에 요청을 보내서 토큰을 전송한다.
            txn_hash = db_txn.txn_hash
            tx_receipt = web3.eth.wait_for_transaction_receipt(txn_hash)
            if tx_receipt is None:
                db_txn.status = 2
                db_txn.result_at = datetime.now()
                db.merge(db_txn)
                db.flush()
                logger.info(f"schedule_token_checker: tx_receipt is None")

            if tx_receipt.status == 1:
                db_txn.status = 5
                db_txn.result_at = datetime.now()
                db.merge(db_txn)
                db.flush()
                logger.info(f"schedule_token_checker: status: receipt is finished")
            else:
                db_txn.status = 3
                db_txn.operating_at = datetime.now()
                db.merge(db_txn)
                db.flush()
                logger.info(f"schedule_token_checker: status: receipt is not finished")

            if tx_receipt.blockNumber is None:
                db_txn.status = 4
                db_txn.result_at = datetime.now()
                db.merge(db_txn)
                db.flush()
                logger.info(f"schedule_token_checker: status: blockNumber is None")

            logger.info(f"schedule_token_checker: txn_hash - {db_txn.status}")
            db.commit()

        logger.info(f"schedule_token_transfer: Task is finished at - {datetime.now}")

    except Exception as e:
        db.rollback()
        logger.error(f"schedule_token_checker: error - {traceback.format_exc()}")

    finally:
        db.close()
        logger.info(f"schedule_token_transfer: Task is finished at - {datetime.now}")
