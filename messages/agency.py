from typing import Optional

from pydantic import BaseModel
from pydantic_sqlalchemy import sqlalchemy_to_pydantic

from models.agency import Agency


class AgencyInfo(sqlalchemy_to_pydantic(Agency)):
    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "aid": "e7fce73002152d4a6b4308c98a6e09d72e278e7a949558c153f8e332713bd3ca",
                "owner_id": "e7fce73002152d4a6b4308c98a6e09d72e278e7a949558c153f8e332713bd3ca",
                "name": "test",
                "address": "test",
                "phone": "test",
                "status": 0,
                "created_at": "2021-07-06 15:00:00",
                "updated_at": "2021-07-06 15:00:00"
            }
        }


class AgencyCreateRequest(BaseModel):
    owner_email: str
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "owner_email": "yarang+v1@gmail.com",
                "name": "t_agency1",
                "address": "test",
                "phone": "test"
            }
        }


class AgencyManagementFailMsg(BaseModel):
    code: int
    content: str

    class Config:
        schema_extra = {"example": {"code": 461, "content": "Create agency failed."}}
