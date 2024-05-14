from typing import Optional

from pydantic import BaseModel
from pydantic_sqlalchemy import sqlalchemy_to_pydantic

from messages.messages import Message
from models.wallet import Wallet


class WalletInfo(sqlalchemy_to_pydantic(Wallet)):
    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "wid": "e7fce73002152d4a6b4308c98a6e09d72e278e7a949558c153f8e332713bd3ca",
                "owner_id": "e7fce73002152d4a6b4308c98a6e09d72e278e7a949558c153f8e332713bd3ca",
                "address": "0xd53eb5203e367bbdd4f72338938224881fc501ab",
                "enable": "Y",
                "created_at": "2021-07-06 15:00:00",
                "updated_at": "2021-07-06 15:00:00",
            }
        }


class WalletCreateMsg(Message):
    class Config:
        schema_extra = {"example": {"code": 200, "content": "Wallet create"}}


class WalletMsg(BaseModel):
    owner_id: str
    address: str


class WalletFailMsg(BaseModel):
    error_code: int
    error_message: str
    error_detail: str
