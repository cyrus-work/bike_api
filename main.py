from asyncio import Timeout
from multiprocessing import current_process

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError, HTTPException
from filelock import FileLock
from jwt import ExpiredSignatureError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import UnmappedInstanceError

from internal.app_config import setting
from internal.exceptions import exception_handlers
from internal.exceptions_handlers import (
    custom_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    integrity_error_handler,
    unmapped_instance_error_handler, jwt_error_handler,
)
from internal.log import logger
from internal.mysql_db import Base, engine
from internal.tasks import schedule_token_transfer, schedule_token_checker
from routers.admin.bike import router as admin_bike_router
from routers.admin.user_info import router as admin_user_info_router
from routers.admin.wallet import router as admin_wallet_router
from routers.admin.workout import router as admin_workout_router
from routers.v1.bike import router as v1_bike_router
from routers.v1.rewards import router as v1_rewards_router
from routers.v1.user import router as v1_user_router
from routers.v1.wallets import router as v1_wallet_router
from routers.v1.workout import router as v1_workout_router

app = FastAPI()

hour = setting["scheduler"]["hour"]
minute = setting["scheduler"]["minute"]
lock_file_path = "/tmp/scheduler.lock"
scheduler = BackgroundScheduler()

# 예외 처리기 등록
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(IntegrityError, integrity_error_handler)
app.add_exception_handler(UnmappedInstanceError, unmapped_instance_error_handler)
app.add_exception_handler(ExpiredSignatureError, jwt_error_handler)
app.add_exception_handler(Exception, custom_exception_handler)
for exc_type in exception_handlers:
    app.add_exception_handler(exc_type, custom_exception_handler)

# 모든 도메인에서 접근 가능하도록 설정
from fastapi.middleware.cors import CORSMiddleware

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(v1_user_router, prefix="/user", tags=["users"])
app.include_router(v1_bike_router, prefix="/bike", tags=["bike"])
app.include_router(v1_wallet_router, prefix="/wallet", tags=["wallet"])
app.include_router(v1_workout_router, prefix="/workout", tags=["workout"])
app.include_router(v1_rewards_router, prefix="/rewards", tags=["rewards"])
app.include_router(v1_rewards_router, prefix="/v1/rewards", tags=["rewards"])

app.include_router(admin_user_info_router, prefix="/admin/user", tags=["admin"])
app.include_router(admin_workout_router, prefix="/admin/workout", tags=["admin"])
app.include_router(admin_bike_router, prefix="/admin/bike", tags=["admin"])
app.include_router(admin_wallet_router, prefix="/admin/wallet", tags=["admin"])


def get_registered_jobs():
    jobs = scheduler.get_jobs()
    return jobs


@app.get("/scheduled-jobs")
def scheduled_jobs():
    jobs = get_registered_jobs()
    job_details = [
        {
            "id": job.id,
            "name": job.name,
            "next_run_time": job.next_run_time,
            "trigger": str(job.trigger),
        }
        for job in jobs
    ]
    return {"jobs": job_details}


# 첫 번째 워커에 대해 환경 변수 설정
logger.info(f"Current process name: {current_process().name}")


def start_scheduler():
    logger.info("Attempting to acquire scheduler lock")
    lock = FileLock(lock_file_path, timeout=1)
    try:
        lock.acquire()
        logger.info("Scheduler worker started")
        scheduler.add_job(
            schedule_token_transfer,
            "cron",
            hour=hour,
            minute=minute,
            id=f"scheduled_transfer_{current_process().name}",
        )

        scheduler.add_job(
            schedule_token_checker,
            "cron",
            hour="*/1",
            minute="*/10",
            id=f"scheduled_checker_{current_process().name}",
        )
        logger.info(f"Current registered jobs: {get_registered_jobs()}")
        scheduler.start()
    except Timeout:
        logger.info("Scheduler lock already held by another process")
    finally:
        lock.release()


if current_process().name == "SpawnProcess-1":
    start_scheduler()
