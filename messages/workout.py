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

    class Config:
        schema_extra = {
            "example": {
                "wid": "e7fce73002152d4a6b4308c98a6e09d72e278e7a949558c153f8e332713bd3ca",
                "bike_serial": "1234567890",
                "energy": 0.1,
                "calorie": 0.1,
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


class WorkoutCreateMsg(BaseModel):
    workout_id: str

    class Config:
        schema_extra = {
            "example": {
                "workout_id": "e7fce73002152d4a6b4308c98a6e09d72e278e7a949558c153f8e332713bd3ca",
            }
        }
