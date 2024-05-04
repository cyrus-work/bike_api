from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from internal.mysql_db import Base, engine
from models.bike_management import BikeManagement

from routers.v1.user import router as v1_user_router
from routers.v1.bike import router as v1_bike_router
from routers.v1.agency import router as v1_agency_router
from routers.v1.wallets import router as v1_wallet_router
from routers.v1.daily_production import router as v1_daily_production_router

# from models import user
from models import wallet
from models import agency
from models import bike
from models import bike_management
from models import daily_prodution
# from models import transaction_history
# from models import user_check

app = FastAPI()

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
app.include_router(v1_daily_production_router, prefix="/daily", tags=["daily_production"])

@app.get("/")
async def root():
    return {"message": "Cyrus Bike API!"}
