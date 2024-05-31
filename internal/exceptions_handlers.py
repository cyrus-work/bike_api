import traceback

from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from internal.exceptions import exception_handlers
from internal.log import logger
from internal.mysql_db import SessionLocal


def db_clean():
    db = SessionLocal()
    try:
        db.rollback()
    except Exception as e:
        logger.error(f"DB rollback error: {e}")
    finally:
        db.close()


async def custom_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(f"Exception: {exc}")
    exc_type = type(exc)
    if exc_type in exception_handlers:
        status_code, error_code, detail = exception_handlers[exc_type]
        logger.error(f"{detail}: {traceback.format_exc()}")
        db_clean()
        return JSONResponse(
            status_code=status_code,
            content={"detail": detail, "error_code": error_code},
        )
    logger.error(f"An unexpected error occurred: {traceback.format_exc()}")
    db_clean()
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred, please try again later."},
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    logger.error(f"HTTPException: {traceback.format_exc()}")
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    logger.error(f"RequestValidationError: {traceback.format_exc()}")
    return JSONResponse(status_code=422, content={"detail": exc.errors()})
