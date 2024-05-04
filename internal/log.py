import datetime
import logging
import os
from logging.config import fileConfig

import pytz

print('check dir exists')
if not os.path.exists('logs'):
    os.makedirs('logs')

fileConfig("./configs/logging.cfg")


class KSTFormatter(logging.Formatter):
    def converter(self, timestamp):
        # Create datetime in UTC
        dt = datetime.datetime.fromtimestamp(timestamp, tz=pytz.UTC)
        # Change datetime's timezone
        return dt.astimezone(pytz.timezone("Asia/Seoul"))

    def formatTime(self, record, datefmt=None):
        dt = self.converter(record.created)
        return dt.strftime("%Y-%m-%d %H:%M:%S")


logger = logging.getLogger()

handlers = logger.handlers
for handler in handlers:
    # 기존 formatter 가져오기
    existing_formatter = handler.formatter
    # 새로운 formatter로 교체
    new_formatter = KSTFormatter(
        fmt="%(asctime)s [%(levelname)s] %(message)s", datefmt=None
    )
    handler.setFormatter(new_formatter)

logger.info(
    "@@@@@@@@@@@@@@@@@@@@@@ mining API : Logging Start @@@@@@@@@@@@@@@@@@@@@@@@"
)
