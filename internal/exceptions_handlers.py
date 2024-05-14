import traceback

from jwt import ExpiredSignatureError, InvalidTokenError
from fastapi.requests import Request
from fastapi.responses import JSONResponse, Response

from internal.exceptions import JWTDataExpiredException
from internal.log import logger
from internal.mysql_db import SessionLocal


async def expired_signature_exception_handler(
    request: Request, exc: ExpiredSignatureError
) -> Response:
    logger.info(f"JWT token expired: {traceback.format_exc()}")
    msg = {"code": 101, "content": "JWT token expired."}
    return JSONResponse(status_code=410, content=msg)


async def integrity_exception_handler(request: Request, exc: Exception) -> Response:
    logger.error(f"An unexpected error occurred: {traceback.format_exc()}")
    db = SessionLocal()
    db.rollback()

    msg = {"code": 102, "content": "Integrity error occurred."}
    return JSONResponse(status_code=410, content=msg)


async def expired_data_exception_handler(
    request: Request, exc: JWTDataExpiredException
) -> Response:
    logger.error(f"JWT data has expired: {traceback.format_exc()}")
    msg = {"code": 103, "content": "JWT data has expired"}
    return JSONResponse(status_code=410, content=msg)


async def invalid_token_exception_handler(
    request: Request, exc: InvalidTokenError
) -> Response:
    logger.error(f"Invalid JWT token: {traceback.format_exc()}")
    msg = {"code": 104, "content": "Invalid JWT token"}
    return JSONResponse(status_code=410, content=msg)


async def unexpected_exception_handler(request: Request, exc: Exception) -> Response:
    logger.error(f"An unexpected error occurred: {traceback.format_exc()}")
    msg = {
        "code": 500,
        "content": "An unexpected error occurred, please try again later.",
    }
    return JSONResponse(status_code=500, content=msg)


async def user_exist_exception_handler(request: Request, exc: Exception) -> Response:
    logger.error(f"User already exists: {traceback.format_exc()}")
    msg = {"code": 105, "content": "User already exists."}
    return JSONResponse(status_code=410, content=msg)


async def user_not_exist_exception_handler(
    request: Request, exc: Exception
) -> Response:
    logger.error(f"User not found: {traceback.format_exc()}")
    msg = {"code": 106, "content": "User not found."}
    return JSONResponse(status_code=410, content=msg)


async def user_email_confirm_exception_handler(
    request: Request, exc: Exception
) -> Response:
    logger.error(f"User email not confirmed: {traceback.format_exc()}")
    msg = {"code": 107, "content": "User email not confirmed."}
    return JSONResponse(status_code=410, content=msg)


async def user_checker_not_exist_exception_handler(
    request: Request, exc: Exception
) -> Response:
    logger.error(f"User checker not found: {traceback.format_exc()}")
    msg = {"code": 108, "content": "User checker not found."}
    return JSONResponse(status_code=410, content=msg)


async def user_checker_not_match_exception_handler(
    request: Request, exc: Exception
) -> Response:
    logger.error(f"User checker not match: {traceback.format_exc()}")
    msg = {"code": 109, "content": "User checker not match."}
    return JSONResponse(status_code=410, content=msg)


async def user_email_not_exist_exception_handler(
    request: Request, exc: Exception
) -> Response:
    logger.error(f"User email not found: {traceback.format_exc()}")
    msg = {"code": 110, "content": "User email not found."}
    return JSONResponse(status_code=410, content=msg)


async def jwt_refresh_token_not_exist_exception_handler(
    request: Request, exc: Exception
) -> Response:
    logger.error(f"JWT refresh token not found: {traceback.format_exc()}")
    msg = {"code": 111, "content": "JWT refresh token not found."}
    return JSONResponse(status_code=410, content=msg)


async def email_verified_exception_handler(
    request: Request, exc: Exception
) -> Response:
    logger.error(f"Email already verified: {traceback.format_exc()}")
    msg = {"code": 112, "content": "Email already verified."}
    return JSONResponse(status_code=410, content=msg)


async def user_password_not_match_exception_handler(
    request: Request, exc: Exception
) -> Response:
    logger.error(f"User password not match: {traceback.format_exc()}")
    msg = {"code": 113, "content": "User password not match."}
    return JSONResponse(status_code=410, content=msg)


async def workout_last_id_not_match_exception_handler(
    request: Request, exc: Exception
) -> Response:
    logger.error(f"Workout last id not match: {traceback.format_exc()}")
    msg = {"code": 114, "content": "Workout last id not match."}
    return JSONResponse(status_code=410, content=msg)


async def workout_last_owner_not_match_exception_handler(
    request: Request, exc: Exception
) -> Response:
    logger.error(f"Workout last owner not match: {traceback.format_exc()}")
    msg = {"code": 115, "content": "Workout last owner not match."}
    return JSONResponse(status_code=410, content=msg)


async def bike_not_exist_exception_handler(
    request: Request, exc: Exception
) -> Response:
    logger.error(f"Bike not found: {traceback.format_exc()}")
    msg = {"code": 116, "content": "Bike not found."}
    return JSONResponse(status_code=410, content=msg)


async def last_workout_not_exist_exception_handler(
    request: Request, exc: Exception
) -> Response:
    logger.error(f"Last workout not found: {traceback.format_exc()}")
    msg = {"code": 117, "content": "Last workout not found."}
    return JSONResponse(status_code=410, content=msg)


async def agency_not_exist_exception_handler(
    request: Request, exc: Exception
) -> Response:
    logger.error(f"Agency not found: {traceback.format_exc()}")
    msg = {"code": 118, "content": "Agency not found."}
    return JSONResponse(status_code=410, content=msg)
