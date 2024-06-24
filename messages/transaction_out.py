from typing import Optional

from pydantic import BaseModel


class TxnOutGetRequest(BaseModel):
    email: str
    offset: Optional[int] = 0
    limit: Optional[int] = 50

    class Config:
        schema_extra = {
            "example": {"email": "test@example.com", "offset": 0, "limit": 50}
        }


class TxnOutGetReq(BaseModel):
    offset: Optional[int] = 0
    limit: Optional[int] = 50

    class Config:
        schema_extra = {"example": {"offset": 0, "limit": 50}}


class TxnOutGetDateReq(BaseModel):
    start_date: str
    end_date: str
    offset: Optional[int] = 0
    limit: Optional[int] = 50

    class Config:
        schema_extra = {
            "example": {
                "start_date": "2021-01-01",
                "end_date": "2021-12-31",
                "offset": 0,
                "limit": 50,
            }
        }
