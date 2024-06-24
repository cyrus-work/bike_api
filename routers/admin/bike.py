import traceback
from datetime import timedelta
from io import BytesIO

import pandas as pd
from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    Request,
    HTTPException,
    status,
    Cookie,
)
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates

from internal.app_config import auth
from internal.exceptions import BikeNotExistsException, CredentialException
from internal.jwt_auth import (
    admin_required,
    create_access_token,
    get_active_auth_user,
    get_access_token_from_cookie,
)
from internal.log import logger
from internal.mysql_db import SessionLocal
from messages.bike import (
    BikeCreateRequest,
    BikeGetRequest,
    BikeDeleteMsg,
    BikeCreateMsg,
    BikeListGetReq,
)
from models.bike import (
    get_bikes_all,
    make_bike,
    get_bike_by_bike_no,
    get_bikes_count_all,
    get_bike_by_bike_no_like,
    get_count_bike_by_bike_no_like,
)

templates = Jinja2Templates(directory="templates")

router = APIRouter()


@router.post("/list")
async def get_bikes_all_api(req: BikeListGetReq, user=Depends(admin_required)):
    """
    Get all bikes

    :param req: BikeListGetReq model
    :param user: admin_required 리턴값
    :return:
    """
    logger.info(f">>> get_bikes_all_api start")

    try:
        admin, db = user

        offset = req.offset
        limit = req.limit

        db_bikes = get_bikes_all(db, offset, limit)
        db_count = get_bikes_count_all(db)
        logger.info(f"    get_bikes_all_api db_bikes: {db_bikes}, {db_count}")
        return {"count": db_count, "data": db_bikes}

    finally:
        logger.info(f">>> get_bikes_all_api end")


@router.post("/info")
async def post_bike_info_api(bike: BikeGetRequest, user=Depends(admin_required)):
    """
    Get bike info

    :param bike:
    :param user:
    :return:
    """
    logger.info(f">>> post_bike_info_api start: {bike}")

    try:
        admin, db = user
        serial = bike.serial

        db_bike = get_bike_by_bike_no(db, serial)
        if db_bike is None:
            raise BikeNotExistsException

        logger.info(f"    post_bike_info_api db_bike: {db_bike}")
        return db_bike

    finally:
        logger.info(f">>> post_bike_info_api end")


@router.post("/info_match")
async def post_bike_info_match_api(bike: BikeGetRequest, user=Depends(admin_required)):
    """
    Get bike info by search

    :param bike:
    :param user:
    :return:
    """
    logger.info(f">>> post_bike_info_match_api start: {bike}")

    try:
        admin, db = user
        serial = bike.serial

        db_bike = get_bike_by_bike_no_like(db, serial)
        db_count = get_count_bike_by_bike_no_like(db, serial)

        logger.info(f"    post_bike_info_match_api db_bike: {db_bike}")
        if db_bike is None:
            db_bike = []
        return {"count": db_count, "data": db_bike}

    finally:
        logger.info(f">>> post_bike_info_match_api end")


@router.post("/create")
async def post_create_bike_api(bike: BikeCreateRequest, user=Depends(admin_required)):
    """
    Create bike

    :param bike:
    :param user:
    :return:
    """
    logger.info(f">>> post_create_bike_api start: {bike}")

    try:
        admin, db = user
        serial = bike.serial
        cpu_version = bike.cpu_version
        board_version = bike.board_version

        db_bike = make_bike(serial, cpu_version, board_version)
        db.add(db_bike)
        db.commit()
        db.refresh(db_bike)
        logger.info(f"    post_create_bike_api db_bike: {db_bike}")
        return BikeCreateMsg(serial=db_bike.bike_no, code=200, content="success")

    finally:
        logger.info(f">>> post_create_bike_api end")


@router.post("/delete")
async def post_delete_bike_api(bike: BikeGetRequest, user=Depends(admin_required)):
    """
    Delete bike

    :param bike:
    :param user:
    :return:
    """
    logger.info(f">>> post_delete_bike_api start: {bike}")

    try:
        admin, db = user
        serial = bike.serial

        db_bike = get_bike_by_bike_no(db, serial)
        if db_bike is None:
            raise BikeNotExistsException

        db.delete(db_bike)
        db.commit()
        logger.info(f"    post_delete_bike_api: {serial} delete success")
        return BikeDeleteMsg(code=200, content="success", serial=serial)

    finally:
        logger.info(f">>> post_delete_bike_api end")


"""
대량 업로드
"""


@router.post("/bulk_create")
async def upload_file(file: UploadFile = File(...), access_token: str = Cookie(None)):
    """
    대량 업로드

    :param file: 업로드 파일
    :param access_token: access_token
    """
    logger.info(f">>> file upload page start")
    db = None
    try:
        db = SessionLocal()

        db_user = get_access_token_from_cookie(db, access_token)
        if db_user is None:
            raise CredentialException()

        logger.info(f"    file upload page start")

        contents = await file.read()
        data = BytesIO(contents)
        df = pd.read_excel(data)
        df = df.applymap(
            lambda x: (
                x.encode("latin1", errors="ignore").decode("latin1")
                if isinstance(x, str)
                else x
            )
        )

        logger.info(f"df: {df}")
        for index, row in df.iterrows():
            serial = row["serial_no"]
            cpu_version = row["cpu_version"]
            board_version = row["board_version"]
            db_bike = make_bike(serial, cpu_version, board_version)
            db.add(db_bike)
            db.flush()

        db.commit()
        return {"code": 200, "content": "success"}
    except Exception as e:
        logger.info(f"    Exception: {traceback.format_exc()}")
        if db:
            db.rollback()
        return {"code": 400, "content": str(e)}

    finally:
        if db:
            db.close()
        logger.info(f">>> file upload page end")


@router.get("/upload_form")
def form(req: Request, access_token: str = Cookie(None)):  # session_token 매개변수 추가
    """
    file upload form page

    :param req: Request
    :param access_token: access_token
    """
    logger.info(">>> file upload form page")

    db = None

    try:
        db = SessionLocal()

        db_user = get_access_token_from_cookie(db, access_token)
        if db_user is None:
            raise CredentialException()

        logger.info(f"    file upload form page send")
        return templates.TemplateResponse("upload_form.html", {"request": req})

    except Exception as e:
        if db:
            db.rollback()
        logger.error(f"    file upload form page Exception: {e}")
        return {"error": str(e)}

    finally:
        if db:
            db.close()
        logger.info(">>> file upload form page end")


@router.get("/login_form", response_class=HTMLResponse)
async def login_page(request: Request):
    """
    login form page
    """
    logger.info(">>> login form page")
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    login for access token

    :param form_data: OAuth2PasswordRequestForm
    """
    logger.info(f">>> login_for_access_token: {form_data}")
    try:
        db_user = get_active_auth_user(form_data.username, form_data.password)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token_expires = timedelta(minutes=auth["access_token_expires"])
        access_token = create_access_token(
            data={"email": db_user.email}, expires_delta=access_token_expires
        )
        if not access_token:
            raise HTTPException(status_code=500, detail="Failed to create access token")

        response = JSONResponse(content={"access_token": access_token}, status_code=200)
        response.set_cookie(
            key="access_token", value=access_token, httponly=True, max_age=1800
        )
        logger.info(f"    login_for_access_token: {response}")
        return response

    finally:
        logger.error(">>> login_for_access_token end")
