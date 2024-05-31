from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError, HTTPException

from internal.exceptions import exception_handlers
from internal.exceptions_handlers import custom_exception_handler, http_exception_handler, validation_exception_handler
from internal.mysql_db import Base, engine
from routers.admin.bike import router as admin_bike_router
from routers.admin.wallet import router as admin_wallet_router
from routers.admin.workout import router as admin_workout_router
from routers.v1.agency import router as v1_agency_router
from routers.v1.bike import router as v1_bike_router
from routers.v1.rewards import router as v1_rewards_router
from routers.v1.user import router as v1_user_router
from routers.v1.wallets import router as v1_wallet_router
from routers.v1.workout import router as v1_workout_router
from routers.v2.user import router as v2_user_router

app = FastAPI()

# 예외 처리기 등록
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
for exc_type in exception_handlers:
    app.add_exception_handler(exc_type, custom_exception_handler)

# 모든 도메인에서 접근 가능하도록 설정
from fastapi.middleware.cors import CORSMiddleware

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(v1_user_router, prefix="/user", tags=["users"])
app.include_router(v1_bike_router, prefix="/bike", tags=["bike"])
app.include_router(v1_agency_router, prefix="/agency", tags=["agency"])
app.include_router(v1_wallet_router, prefix="/wallet", tags=["wallet"])
app.include_router(v1_workout_router, prefix="/workout", tags=["workout"])

app.include_router(v2_user_router, prefix="/v2/user", tags=["users"])
app.include_router(v1_rewards_router, prefix="/v1/rewards", tags=["rewards"])

app.include_router(admin_workout_router, prefix="/admin/workout", tags=["admin"])
app.include_router(admin_bike_router, prefix="/admin/bike", tags=["admin"])
app.include_router(admin_wallet_router, prefix="/admin/wallet", tags=["admin"])