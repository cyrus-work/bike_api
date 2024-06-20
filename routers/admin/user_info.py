from fastapi import Depends, APIRouter

from internal.exceptions import UserNotExistsException
from internal.jwt_auth import admin_required
from internal.log import logger
from messages.user import (
    UserSearchFlagRequest,
    UserEmailRequest,
    UserSearchWalletRequest,
    UserListGetReq,
)
from models.user import get_user_by_email
from models.user_wallet import (
    get_user_wallets,
    get_user_info_by_email_verified,
    get_user_info_by_wallet_exist,
    get_user_info_by_wallet,
    get_counts_of_user_wallets,
)

router = APIRouter()


@router.post("/list")
async def get_user_info(req: UserListGetReq, user=Depends(admin_required)):
    """
    사용자 정보 조회

    :param req: UserListGetReq 모델
    :param user: admin_required
    :return:
    """
    logger.info(f">>> get_user_info start")

    try:
        db_user, db = user

        offset = req.offset
        limit = req.limit

        db_user_info = get_user_wallets(db, offset, limit)
        db_count = get_counts_of_user_wallets(db)

        logger.info(f"get_user_info: {db_user_info}, {db_count}")
        return {"count": db_count, "data": db_user_info}

    finally:
        logger.info(f">>> get_user_info end")


@router.post("/email_verification")
async def post_email_verification(
    req: UserSearchFlagRequest, user=Depends(admin_required)
):
    """
    사용자 이메일 인증

    :param req: UserSearchFlagRequest 모델
    :param user: admin_required
    :return:
    """
    logger.info(f">>> post_email_verification start")

    try:
        db_user, db = user
        verified = req.verified

        db_user_info = get_user_info_by_email_verified(db, verified)

        logger.info(f"post_email_verification: {db_user_info}")
        return db_user_info

    finally:
        logger.info(f">>> post_email_verification end")


@router.post("/wallet_info")
async def post_wallet_exist(req: UserSearchWalletRequest, user=Depends(admin_required)):
    """
    사용자 지갑 정보 조회

    :param req: UserSearchWalletRequest 모델
    :param user: admin_required
    :return:
    """
    logger.info(f">>> post_wallet_exist start")

    try:
        db_user, db = user
        exist = req.exist
        wallet = req.wallet

        if wallet is None:
            db_users = get_user_info_by_wallet_exist(db, exist)
        else:
            db_users = get_user_info_by_wallet(db, wallet)

        logger.info(f"post_wallet_exist: {db_users}")
        return db_users

    finally:
        logger.info(f">>> post_wallet_exist end")


@router.post("/delete")
async def post_delete_user_by_email_api(
    req: UserEmailRequest, user=Depends(admin_required)
):
    """
    사용자 삭제

    :param req: UserEmailRequest 모델
    :param user: admin_required
    :return:
    """
    logger.info(f">>> post_delete_user_by_email_api: {req}")

    try:
        admin, db = user

        email = req.email

        db_user = get_user_by_email(db, email)
        if db_user is None:
            raise UserNotExistsException

        db.delete(db_user)
        db.commit()

        logger.info(f"post_delete_user_by_email_api: {email} delete success")
        return {"message": "delete success"}

    finally:
        logger.info(f">>> post_delete_user_by_email_api end")
