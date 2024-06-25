from fastapi import Depends, APIRouter

from internal.exceptions import UserNotExistsException
from internal.jwt_auth import admin_required
from internal.log import logger
from messages.user import (
    UserSearchFlagRequest,
    UserEmailRequest,
    UserSearchWalletRequest,
    UserListGetReq,
    UserUpdateAdminReq,
)
from models.UserWithWorkoutAndWalletSummary import (
    get_user_with_workout_wallet_summary_like_email,
    get_count_user_with_workout_summary_wallet_like_email,
)
from models.owner_token_point import get_workout_summary_by_owner_id
from models.user import (
    get_user_by_email,
    get_users_like_email,
    get_count_users_like_email,
)
from models.user_wallet import (
    get_user_wallets,
    get_user_info_by_email_verified,
    get_user_info_by_wallet_exist,
    get_user_info_by_wallet,
    get_counts_of_user_wallets,
    get_user_wallets_by_email,
    get_count_of_user_wallets_by_exist,
    get_count_of_user_wallets_by_email_verified,
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

        logger.info(f"    get_user_info: {db_user_info}, {db_count}")
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
        offset = req.offset
        limit = req.limit

        db_user_info = get_user_info_by_email_verified(db, verified, offset, limit)
        db_count = get_count_of_user_wallets_by_email_verified(db, verified)

        logger.info(f"    post_email_verification: {db_user_info, db_count}")
        return {"count": db_count, "data": db_user_info}

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
        offset = req.offset
        limit = req.limit

        if wallet is None:
            db_users = get_user_info_by_wallet_exist(db, exist, offset, limit)
            db_count = get_count_of_user_wallets_by_exist(db, exist)
            logger.info(f"    post_wallet_exist: {db_users, db_count}")
            return {"count": db_count, "data": db_users}

        else:
            db_users = get_user_info_by_wallet(db, wallet)
            logger.info(f"post_wallet_exist: {db_users}")
            return db_users

    finally:
        logger.info(f">>> post_wallet_exist end")


@router.post("/info")
async def post_get_user_info_api(req: UserEmailRequest, user=Depends(admin_required)):
    """
    사용자 정보 조회

    :param req: UserEmailRequest 모델
    :param user: admin_required
    :return:
    """
    logger.info(f">>> post_get_user_info_api start")

    try:
        db_user, db = user
        email = req.email

        db_user_info = get_user_wallets_by_email(db, email)
        db_workout_summary = get_workout_summary_by_owner_id(db, db_user_info.uid)
        db_user_info.token = db_workout_summary.total_token_status_0
        db_user_info.point = db_workout_summary.total_point_status_0

        logger.info(f"    post_get_user_info_api: {db_user_info}")
        return db_user_info

    finally:
        logger.info(f">>> post_get_user_info_api end")


@router.post("/info_match")
async def post_get_user_info_match_api(
    req: UserEmailRequest, user=Depends(admin_required)
):
    """
    사용자 정보 조회 by search

    :param req: UserEmailRequest 모델
    :param user: admin_required
    :return:
    """
    logger.info(f">>> post_get_user_info_match_api start")

    try:
        db_user, db = user
        email = req.email

        db_user_info = get_users_like_email(db, email)
        db_count = get_count_users_like_email(db, email)

        result = []
        for item in db_user_info:
            db_workout_summary = get_workout_summary_by_owner_id(db, item.uid)
            item.token = db_workout_summary.total_token_status_0
            item.point = db_workout_summary.total_point_status_0
            result.append(item)

        logger.info(f"    post_get_user_info_match_api: {result}")
        return {"count": db_count, "data": result}

    finally:
        logger.info(f">>> post_get_user_info_match_api end")


@router.post("/info_by_email")
async def post_info_by_email_api(req: UserEmailRequest, user=Depends(admin_required)):
    """
    사용자 정보 조회 by email

    :param req: UserEmailRequest 모델
    :param user: admin_required
    :return:
    """
    logger.info(f">>> post_info_by_email_api start")

    try:
        db_user, db = user

        email = req.email
        offset = req.offset
        limit = req.limit

        db_user_info = get_user_with_workout_wallet_summary_like_email(
            db, email, offset, limit
        )
        db_count = get_count_user_with_workout_summary_wallet_like_email(db, email)

        logger.info(f"    post_info_by_email_api: {db_user_info}")
        return {"count": db_count, "data": db_user_info}

    finally:
        logger.info(f">>> post_info_by_email_api end")


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

        logger.info(f"    post_delete_user_by_email_api: {email} delete success")
        return {"message": "delete success"}

    finally:
        logger.info(f">>> post_delete_user_by_email_api end")


@router.post("/update")
async def post_update_user_by_email_api(
    req: UserUpdateAdminReq, user=Depends(admin_required)
):
    """
    사용자 정보 수정

    :param req: UserEmailRequest 모델
    :param user: admin_required
    :return:
    """
    logger.info(f">>> post_update_user_by_email_api: {req}")

    try:
        admin, db = user

        email = req.email
        name = req.name
        password = req.password
        level = req.level

        db_user = get_user_by_email(db, email)
        if db_user is None:
            raise UserNotExistsException

        if name is not None:
            db_user.name = name
        if password is not None:
            db_user.password = password
        if level is not None:
            db_user.level = level

        db.commit()
        db.refresh(db_user)
        logger.info(f"    post_update_user_by_email_api: {db_user}")

        return db_user

    finally:
        logger.info(f">>> post_update_user_by_email_api end")
