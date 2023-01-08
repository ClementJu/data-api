from datetime import datetime

from pydantic import BaseModel


class DialogDataCreateModel(BaseModel):
    text: str
    language: str


class DialogDataModel(DialogDataCreateModel):
    id: int
    customer_id: str
    dialog_id: str
    received_at_timestamp_utc: datetime

    class Config:
        orm_mode = True