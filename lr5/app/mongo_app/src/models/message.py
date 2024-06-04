from datetime import datetime

from pydantic import BaseModel


class Message(BaseModel):
    message_string: str
    send_date: datetime
    member_sent: int
