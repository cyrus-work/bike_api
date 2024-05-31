from pydantic import BaseModel

from messages.messages import Message


class BikeCreateRequest(BaseModel):
    serial: str
    cpu_version: str
    board_version: str

    class Config:
        schema_extra = {
            "example": {
                "serial": "C1B000123Z",
                "cpu_version": "1.0.0",
                "board_version": "1.0.0",
            }
        }


class BikeCreateMsg(Message):
    class Config:
        schema_extra = {"example": {"code": 200, "content": "Bike create"}}


class BikeManagementFailMsg(Message):
    class Config:
        schema_extra = {"example": {"code": 461, "content": "Create bike failed."}}
