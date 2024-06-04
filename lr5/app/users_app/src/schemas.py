from typing import Optional, TypeVar

from pydantic import BaseModel


class UserSchema(BaseModel):
    first_name: Optional[str]
    second_name: Optional[str]
    password: Optional[str]
    login: Optional[str]
