from pydantic import BaseModel


class TxnOutGetRequest(BaseModel):
    email: str

    class Config:
        schema_extra = {"example": {"email": "test@example.com"}}
