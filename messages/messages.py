from pydantic import BaseModel


class Message(BaseModel):
    """
    Message model

    code: int
    content: str
    """
    code: int
    content: str


class ExceptionMsg(BaseModel):
    """
    Exception message model

    detail: str
    """
    detail: str
