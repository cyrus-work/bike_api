import logging

# Custom logger for tasking.py
log_task = logging.getLogger("tasking_logger")
handler = logging.FileHandler("/tmp/tasking.log")
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
log_task.addHandler(handler)
log_task.setLevel(logging.INFO)
