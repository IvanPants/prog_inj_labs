from pydantic import BaseModel


class ChatModel(BaseModel):
    admins: list[int]
    members: list[int]
    chat_name: str
    messages: list
    is_P2P: bool
