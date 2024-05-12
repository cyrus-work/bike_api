import traceback

from jwt import ExpiredSignatureError, InvalidTokenError
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from internal.exceptions import JWTDataExpiredException
from internal.log import logger
from internal.mysql_db import SessionLocal


async def expired_signature_exception_handler(request: Request, exc: ExpiredSignatureError) -> Response:
    logger.info(f"JWT token expired: {traceback.format_exc()}")
    msg = {"code": 101, "content": "JWT token expired."}
    return JSONResponse(
        status_code=410,
        content=msg
    )


async def integrity_exception_handler(request: Request, exc: Exception) -> Response:
    logger.error(f"An unexpected error occurred: {traceback.format_exc()}")
    db = SessionLocal()
    db.rollback()

    msg = {"code": 102, "content": "Integrity error occurred."}
    return JSONResponse(
        status_code=410,
        content=msg
    )


async def expired_data_exception_handler(request: Request, exc: JWTDataExpiredException) -> Response:
    logger.error(f"JWT data has expired: {traceback.format_exc()}")
    msg = {"code": 103, "content": "JWT data has expired"}
    return JSONResponse(
        status_code=410,
        content=msg
    )


async def invalid_token_exception_handler(request: Request, exc: InvalidTokenError) -> Response:
    logger.error(f"Invalid JWT token: {traceback.format_exc()}")
    msg = {"code": 104, "content": "Invalid JWT token"}
    return JSONResponse(
        status_code=410,
        content=msg
    )


async def unexpected_exception_handler(request: Request, exc: Exception) -> Response:
    logger.error(f"An unexpected error occurred: {traceback.format_exc()}")
    msg = {"code": 500, "content": "An unexpected error occurred, please try again later."}
    return JSONResponse(
        status_code=500,
        content=msg
    )

async def user_exist_exception_handler(request: Request, exc: Exception) -> Response:
    logger.error(f"User already exists: {traceback.format_exc()}")
    msg = {"code": 105, "content": "User already exists."}
    return JSONResponse(
        status_code=410,
        content=msg
    )