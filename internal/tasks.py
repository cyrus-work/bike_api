from datetime import datetime

from internal.log import logger
from internal.mysql_db import SessionLocal
from internal.utils import is_valid_polygon_address
from models.reward_request import get_txn_out_by_txn_hash_is_null


def schedule_token_transfer():
    logger.info(f"schedule_token_transfer: Task is running at - {datetime.now}")

    try:
        db = SessionLocal()

        db_workouts = get_txn_out_by_txn_hash_is_null(db)

        for db_workout in db_workouts:
            logger.info(f"schedule_token_transfer: db_workout - {db_workout}")
            if is_valid_polygon_address(db_workout["wallet"]) is False:
                logger.error(
                    f"uid - {db_workout['uid']}, Invalid address - {db_workout['wallet']}"
                )
                continue
                # request를 사용하여 API 서버에 요청을 보내서 데이터를 가져온다.
            pass

    finally:
        logger.info(f"schedule_token_transfer: Task is finished at - {datetime.now}")
