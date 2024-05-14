from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from jwt import InvalidTokenError, ExpiredSignatureError
from sqlalchemy.exc import IntegrityError

from internal.exceptions import JWTDataExpiredException, UserExistsException, UserEmailNotConfirmException, \
    UserNotExistsException, UserCheckerNotExistException, UserCheckerNotMatchException, UserEmailNotExistException, \
    JWTRefreshTokenNotExistException, EmailVerifiedException, UserPasswordNotMatchException, \
    LastWorkoutIdNotMatchException, WorkoutLastOwnerNotMatchException, BikeNotExistsException, \
    LastWorkoutNotExistsException, AgencyNotExistsException
from internal.exceptions_handlers import integrity_exception_handler, expired_signature_exception_handler, \
    expired_data_exception_handler, invalid_token_exception_handler, unexpected_exception_handler, \
    user_exist_exception_handler, user_email_confirm_exception_handler, user_not_exist_exception_handler, \
    user_checker_not_exist_exception_handler, user_checker_not_match_exception_handler, \
    user_email_not_exist_exception_handler, jwt_refresh_token_not_exist_exception_handler, \
    email_verified_exception_handler, user_password_not_match_exception_handler, \
    workout_last_id_not_match_exception_handler, workout_last_owner_not_match_exception_handler, \
    bike_not_exist_exception_handler, last_workout_not_exist_exception_handler, agency_not_exist_exception_handler
from internal.mysql_db import Base, engine
from routers.v1.agency import router as v1_agency_router
from routers.v1.bike import router as v1_bike_router
from routers.v1.user import router as v1_user_router
from routers.v1.wallets import router as v1_wallet_router
from routers.v1.workout import router as v1_workout_router
from routers.v2.user import router as v2_user_router
from routers.v2.workout import router as v2_workout_router

app = FastAPI()

# 예외 처리기 등록
app.add_exception_handler(ExpiredSignatureError, expired_signature_exception_handler)
app.add_exception_handler(IntegrityError, integrity_exception_handler)
app.add_exception_handler(JWTDataExpiredException, expired_data_exception_handler)
app.add_exception_handler(InvalidTokenError, invalid_token_exception_handler)
app.add_exception_handler(Exception, unexpected_exception_handler)
app.add_exception_handler(UserExistsException, user_exist_exception_handler)
app.add_exception_handler(UserNotExistsException, user_not_exist_exception_handler)
app.add_exception_handler(UserEmailNotConfirmException, user_email_confirm_exception_handler)
app.add_exception_handler(UserCheckerNotExistException, user_checker_not_exist_exception_handler)
app.add_exception_handler(UserCheckerNotMatchException, user_checker_not_match_exception_handler)
app.add_exception_handler(UserEmailNotExistException, user_email_not_exist_exception_handler)
app.add_exception_handler(JWTRefreshTokenNotExistException, jwt_refresh_token_not_exist_exception_handler)
app.add_exception_handler(EmailVerifiedException, email_verified_exception_handler)
app.add_exception_handler(UserPasswordNotMatchException, user_password_not_match_exception_handler)
app.add_exception_handler(LastWorkoutIdNotMatchException, workout_last_id_not_match_exception_handler)
app.add_exception_handler(WorkoutLastOwnerNotMatchException, workout_last_owner_not_match_exception_handler)
app.add_exception_handler(BikeNotExistsException, bike_not_exist_exception_handler)
app.add_exception_handler(LastWorkoutNotExistsException, last_workout_not_exist_exception_handler)
app.add_exception_handler(AgencyNotExistsException, agency_not_exist_exception_handler)

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
