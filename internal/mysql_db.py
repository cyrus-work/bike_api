from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from internal.app_config import database

DB_USER = database["user"]
DB_PASSWORD = database["password"]
DB_HOST = database["host"]
DB_NAME = database["name"]
DB_PORT = database["port"]

# SQLAlchemy 엔진 생성
SQLALCHEMY_DATABASE_URL = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
Base_ex = declarative_base()
