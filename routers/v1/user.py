from datetime import timedelta

from fastapi import APIRouter, Depends

from internal.jwt_auth import (
    create_access_token,
    auth,
    get_info_from_refresh_token,
    oauth2_scheme,
)
from internal.log import logger
from internal.mysql_db import SessionLocal, get_db
from messages.jwt_auth import (
    TokenEmailNotExistsMsg,
    TokenRefreshNotExistsMsg,
    AccessTokenMsg,
)
from messages.user import (
    UserNotFoundMsg,
)
from models.user import get_user_by_email, get_users

router = APIRouter()


@router.get("/users")
async def read_users(db: SessionLocal = Depends(get_db)):
    users = get_users(db, offset=0, limit=100)
    return users


@router.post(
    "/refresh",
)
async def refresh_token_api(
    db: SessionLocal = Depends(get_db), token: str = Depends(oauth2_scheme)
):
    logger.info(f">>> refresh_token_api: {token}")
    try:
        info = get_info_from_refresh_token(token)

        email = info.get("email")
        refresh = info.get("refresh")
        if email is None:
            msg = {"code": 463, "content": "email is not exist"}
            logger.error(f"refresh_token_api: {msg}")
            return TokenEmailNotExistsMsg(**msg)

        if refresh is None:
            msg = {"code": 464, "content": "refresh token is not exist"}
            logger.error(f"refresh_token_api: {msg}")
            return TokenRefreshNotExistsMsg(**msg)

        user = get_user_by_email(db, email)
        if user is None:
            msg = {"code": 462, "content": "User not found."}
            logger.error(f"refresh_token_api: {msg}")
            return UserNotFoundMsg(**msg)

        access_token_expires = timedelta(minutes=auth["access_token_expires"])
        access_token = create_access_token(
            data={"email": email}, expires_delta=access_token_expires
        )

        token_msg = {"access_token": access_token, "token_type": "bearer"}
        logger.info(f"refresh_token_api: {token_msg}")
        return AccessTokenMsg(**token_msg)

    finally:
        logger.info(f">>> refresh_token_api end")
