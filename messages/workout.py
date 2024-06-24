from typing import Optional

from pydantic import BaseModel


class WorkoutCreateRequest(BaseModel):
    """
    workout을 시작하는 Request 모델

    bike_serial: 자전거 시리얼
    ptype: point type (0: token, 1: point)
    """

    bike_serial: str
    ptype: int

    class Config:
        schema_extra = {
            "example": {
                "bike_serial": "1234567890",
                "ptype": 0,
            }
        }


class WorkoutKeepRequest(BaseModel):
    wid: str
    bike_serial: str
    energy: float
    calorie: float
    running_time: int

    class Config:
        schema_extra = {
            "example": {
                "wid": "e7fce73002152d4a6b4308c98a6e09d72e278e7a949558c153f8e332713bd3ca",
                "bike_serial": "1234567890",
                "energy": 0.1,
                "calorie": 0.1,
                "running_time": 10,
            }
        }


class WorkoutDataRequest(BaseModel):
    data: str

    class Config:
        schema_extra = {
            "example": {
                "data": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxMjM0LCJ1c2VybmFtZSI6ImV4YW1wbGVfdXNlciIsImV4cCI6MTcxNTQyOTIwNn0.XVn71RSBx4osoy5oMTwH3IhiBoMnenHmhLJDhDhBQwc",
            }
        }


class WorkoutGetRequest(BaseModel):
    date: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "date": "2021-07-06",
            }
        }


class WorkoutWidGetRequest(BaseModel):
    wid: str

    class Config:
        schema_extra = {
            "example": {
                "wid": "T1A11060b3ea2a5be5a0620237afdb565bf211c896b29095f2467e2f4985a8fa",
            }
        }


class WorkoutGetDurationRequest(BaseModel):
    start_date: str
    end_date: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "start_date": "2021-07-06",
                "end_date": "2021-07-06",
            }
        }


class WorkoutGetDateRequest(BaseModel):
    date: str

    class Config:
        schema_extra = {
            "example": {
                "date": "2021-07-01",
            }
        }


class WorkoutGetMonthRequest(BaseModel):
    month: str

    class Config:
        schema_extra = {
            "example": {
                "month": "2021-07",
            }
        }


class WorkoutGetMonthTestRequest(BaseModel):
    email: str

    class Config:
        schema_extra = {
            "example": {
                "email": "test@exam.com"
            }
        }


class WorkoutCreateMsg(BaseModel):
    workout_id: str

    class Config:
        schema_extra = {
            "example": {
                "workout_id": "e7fce73002152d4a6b4308c98a6e09d72e278e7a949558c153f8e332713bd3ca",
            }
        }


class WorkoutGetAllRequest(BaseModel):
    offset: Optional[int] = 0
    limit: Optional[int] = 50

    class Config:
        schema_extra = {
            "example": {
                "offset": 0,
                "limit": 50,
            }
        }


class WorkoutGetTypeRequest(BaseModel):
    ptype: int
    offset: Optional[int] = 0
    limit: Optional[int] = 50

    class Config:
        schema_extra = {
            "example": {
                "ptype": 0,
                "offset": 0,
                "limit": 50,
            }
        }


class WorkoutGetUserRequest(BaseModel):
    ptype: int
    email: Optional[str] = None
    offset: Optional[int] = 0
    limit: Optional[int] = 50

    class Config:
        schema_extra = {
            "example": {
                "email": "test@example.com",
                "ptype": 0,
                "offset": 0,
                "limit": 50,
            }
        }


class WorkoutGetSearchRequest(BaseModel):
    ptype: int
    email: str
    start_date: str = None
    end_date: Optional[str] = None
    offset: Optional[int] = 0
    limit: Optional[int] = 50

    class Config:
        schema_extra = {
            "example": {
                "email": "test@example.com",
                "ptype": 0,
                "start_date": "2021-07-01",
                "end_date": "2021-07-01",
                "offset": 0,
                "limit": 50,
            }
        }
