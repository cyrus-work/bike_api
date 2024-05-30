from multiprocessing import current_process

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI
from filelock import FileLock, Timeout

from internal.app_config import setting
from internal.log_task import log_task
from internal.tasks import schedule_token_transfer

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


hour = setting["scheduler"]["hour"]
minute = setting["scheduler"]["minute"]
lock_file_path = "/tmp/scheduler.lock"
scheduler = BackgroundScheduler()


def start_scheduler():
    log_task.info("Attempting to acquire scheduler lock")
    lock = FileLock(lock_file_path, timeout=1)
    try:
        lock.acquire()
        log_task.info("Scheduler worker started")
        scheduler.add_job(
            schedule_token_transfer,
            "cron",
            hour=hour,
            minute=minute,
            id=f"scheduled_transfer_{current_process().name}",
        )
        scheduler.start()
    except Timeout:
        log_task.info("Scheduler lock already held by another process")
    finally:
        lock.release()


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
log_task.info(f"Current process name: {current_process().name}")


if current_process().name == "SpawnProcess-2":
    start_scheduler()
elif current_process().name == "SpawnProcess-1":
    start_scheduler()
