from pydantic import BaseModel


class DailyProductionCreateRequest(BaseModel):
    wallet_address: str
    bike_serial: str
    coin: float
    point: float
    watt: float
    duration: str

    class Config:
        schema_extra = {
            "example": {
                "wallet_address": "0x1234567890123456789012345678901234567890",
                "bike_serial": "1234567890",
                "coin": 0.1,
                "point": 0.1,
                "watt": 0.1,
                "duration": "00:00:00",
            }
        }


class WorkoutSendRequest(BaseModel):
    wallet_address: str
    bike_serial: str
    warmup_at: str
    cooldown_at: str
    watt: float
    calorie: float

    class Config:
        schema_extra = {
            "example": {
                "wallet_address": "0x1234567890123456789012345678901234567890",
                "bike_serial": "1234567890",
                "coin": 0.1,
                "point": 0.1,
                "watt": 0.1,
                "duration": "00:00:00",
            }
        }

class DailyProductionRequest(BaseModel):
    wallet_address: str

    class Config:
        schema_extra = {
            "example": {
                "wallet_address": "0x1234567890123456789012345678901234567890",
            }
        }