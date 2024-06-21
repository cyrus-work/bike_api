from typing import Optional

from pydantic import BaseModel

from messages.messages import Message

"""
Bike Request Models
"""


class BikeCreateRequest(BaseModel):
    serial: str
    cpu_version: Optional[str] = "1.0.0"
    board_version: Optional[str] = "1.0.0"

    class Config:
        schema_extra = {
            "example": {
                "serial": "C1B000123Z",
                "cpu_version": "1.0.0",
                "board_version": "1.0.0",
            }
        }


class BikeGetRequest(BaseModel):
    """
    Bike get model

    serial: Bike serial
    """

    serial: str

    class Config:
        schema_extra = {"example": {"serial": "C1B000123Z"}}


"""
Bike Messages
"""


class BikeCreateMsg(Message):
    serial: str

    class Config:
        schema_extra = {"example": {"code": 200, "content": "Bike create"}}


class BikeDeleteMsg(Message):
    class Config:
        schema_extra = {"example": {"code": 200, "content": "Bike delete"}}


class BikeManagementFailMsg(Message):
    class Config:
        schema_extra = {"example": {"code": 461, "content": "Create bike failed."}}


"""
Admin messages
"""


class BikeListGetReq(BaseModel):
    """
    Bike list get model

    offset: offset
    limit: limit
    """

    offset: Optional[int] = 0
    limit: Optional[int] = 50

    class Config:
        schema_extra = {
            "example": {
                "offset": 0,
                "limit": 50,
            }
        }
