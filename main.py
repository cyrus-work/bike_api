from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from jwt import InvalidTokenError, ExpiredSignatureError
from sqlalchemy.exc import IntegrityError

from internal.exceptions_handlers import integrity_exception_handler, expired_signature_exception_handler, \
    expired_data_exception_handler, invalid_token_exception_handler, unexpected_exception_handler, \
    user_exist_exception_handler
from internal.exceptions import JWTDataExpiredException, UserExistsException

from internal.mysql_db import Base, engine
from routers.v1.agency import router as v1_agency_router
from routers.v1.bike import router as v1_bike_router
from routers.v1.user import router as v1_user_router
from routers.v1.wallets import router as v1_wallet_router
from routers.v1.workout import router as v1_workout_router
from routers.v2.workout import router as v2_workout_router
from routers.v2.user import router as v2_user_router

# from models import user

# from models import transaction_history
# from models import user_check

app = FastAPI()

# 예외 처리기 등록
app.add_exception_handler(ExpiredSignatureError, expired_signature_exception_handler)
app.add_exception_handler(IntegrityError, integrity_exception_handler)
app.add_exception_handler(JWTDataExpiredException, expired_data_exception_handler)
app.add_exception_handler(InvalidTokenError, invalid_token_exception_handler)
app.add_exception_handler(Exception, unexpected_exception_handler)
app.add_exception_handler(UserExistsException, user_exist_exception_handler)

# 모든 도메인에서 접근 가능하도록 설정
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

# BikeManagement.create_view()

app.include_router(v1_user_router, prefix="/user", tags=["users"])
app.include_router(v1_bike_router, prefix="/bike", tags=["bike"])
app.include_router(v1_agency_router, prefix="/agency", tags=["agency"])
app.include_router(v1_wallet_router, prefix="/wallet", tags=["wallet"])
app.include_router(v1_workout_router, prefix="/workout", tags=["workout"])

app.include_router(v2_workout_router, prefix="/v2/workout", tags=["workout"])
app.include_router(v2_user_router, prefix="/v2/user", tags=["users"])
